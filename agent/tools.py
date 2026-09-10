from collections import Counter
from langchain_core.tools import tool
from incident_db import query_past_incidents as db_query


def build_tools(notifier):
    @tool
    def query_past_incidents(camera_id: str, event_type: str) -> str:
        """Search historical incident logs for similar past events at a given camera."""
        rows = db_query(camera_id, event_type)
        if not rows:
            return f"No past incidents found for camera {camera_id}, event_type '{event_type}'. This is the first recorded occurrence."
        counts = Counter(r["decision"] for r in rows)
        summary = ", ".join(f"{v}x {k.replace('_', ' ')}" for k, v in counts.items())
        return f"Found {len(rows)} past '{event_type}' event(s) at camera {camera_id}. Past decisions: {summary}."

    @tool
    def escalate_to_security(camera_id: str, summary: str, severity: str) -> str:
        """Send a real alert to the security team. Only for confirmed, serious events."""
        return notifier.escalate(camera_id, summary, severity)

    @tool
    def flag_for_human_review(camera_id: str, reason: str) -> str:
        """Use only when history is genuinely mixed or missing — not as a default."""
        return notifier.flag_for_review(camera_id, reason)

    return [query_past_incidents, escalate_to_security, flag_for_human_review]