"""
Sentinel — API layer. Any camera pipeline 
POSTs detections here instead of Sentinel reading a file.
"""
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from fastapi.staticfiles import StaticFiles
from incident_db import list_recent_incidents
import asyncio
from config import NOTIFY_METHOD, WEBHOOK_URL
from notifiers import build_notifier
from agent.tools import build_tools
from agent.graph import build_graph
from incident_db import init_db, log_incident
init_db()

def determine_decision(messages) -> str:
    tool_names = set()
    for m in messages:
        for tc in (getattr(m, "tool_calls", None) or []):
            tool_names.add(tc["name"])
    if "escalate_to_security" in tool_names:
        return "escalate"
    if "flag_for_human_review" in tool_names:
        return "human_review"
    return "no_escalate"

app = FastAPI(title="Sentinel")
notifier = build_notifier(NOTIFY_METHOD, WEBHOOK_URL)
tools = build_tools(notifier)
sentinel_graph = build_graph(tools)

class ResolveRequest(BaseModel):
    was_real: bool

@app.get("/incidents")
def get_incidents():
    return list_recent_incidents()

@app.patch("/incidents/{incident_id}/resolve")
def resolve(incident_id: int, body: ResolveRequest):
    from incident_db import resolve_incident
    success = resolve_incident(incident_id, body.was_real)
    if not success:
        return {"success": False, "message": "Incident not found"}
    return {"success": True, "incident_id": incident_id, "resolved_as": "real" if body.was_real else "false_alarm"}


class DetectionEvent(BaseModel):
    camera_id: str
    event_type: str
    confidence: float
    timestamp: str
    location: Optional[str] = None


def extract_text(message) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            b["text"] if isinstance(b, dict) else b
            for b in content if isinstance(b, dict) and b.get("type") == "text" or isinstance(b, str)
        )
    return str(content)


@app.post("/events")
async def receive_event(event: DetectionEvent):
    prompt = (
        f"New detection event: camera {event.camera_id} flagged '{event.event_type}'"
        + (f" at {event.location}" if event.location else "")
        + f" ({event.timestamp}, confidence {event.confidence}). Decide what to do."
    )
    thread_id = f"camera-{event.camera_id}"
    config = {"configurable": {"thread_id": thread_id}}
    result = await asyncio.to_thread(sentinel_graph.invoke, {"messages": [HumanMessage(content=prompt)]}, config)
    decision = determine_decision(result["messages"])
    incident_id = log_incident(event.camera_id, event.event_type, event.confidence, event.timestamp, decision)
    text = extract_text(result["messages"][-1]).strip()
    if not text:
        text = f"Decision: {decision} (model returned no explanatory text this time)"
    return {"camera_id": event.camera_id, "incident_id": incident_id, "decision": text}
app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")