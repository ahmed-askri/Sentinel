"""
Sentinel — entry point.
"""

from langchain_core.messages import HumanMessage

from config import EVENT_SOURCE_PATH, NOTIFY_METHOD, WEBHOOK_URL
from source import load_events
from notifiers import build_notifier
from agent.tools import build_tools
from agent.graph import build_graph


def extract_text(message) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return str(content)


def run_on_event(graph, event: dict, thread_id: str):
    prompt = (
        f"New detection event: camera {event['camera_id']} flagged "
        f"'{event['event_type']}' at {event['location']} "
        f"({event['timestamp']}, confidence {event['confidence']}). "
        f"Decide what to do."
    )
    cfg = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke({"messages": [HumanMessage(content=prompt)]}, cfg)
    final_message = result["messages"][-1]
    print(f"\n=== Event: {event['event_type']} @ camera {event['camera_id']} ===")
    print(extract_text(final_message))


if __name__ == "__main__":
    notifier = build_notifier(NOTIFY_METHOD, WEBHOOK_URL)
    tools = build_tools(notifier)
    sentinel_graph = build_graph(tools)
    print(sentinel_graph.get_graph().draw_ascii())

    events = load_events(EVENT_SOURCE_PATH)
    for i, event in enumerate(events):
        run_on_event(sentinel_graph, event, thread_id=f"event-{i}")