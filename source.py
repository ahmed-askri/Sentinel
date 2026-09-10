import json

def load_events(path: str) -> list[dict]:
    """Swap this for a live feed later — everything else stays the same,
    as long as events keep this shape: camera_id, event_type, confidence,
    timestamp, location."""
    with open(path) as f:
        return json.load(f)