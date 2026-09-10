import sqlite3

DB_PATH = "sentinel_incidents.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            confidence REAL,
            event_timestamp TEXT,
            decision TEXT NOT NULL,
            logged_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def log_incident(camera_id, event_type, confidence, event_timestamp, decision):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "INSERT INTO incidents (camera_id, event_type, confidence, event_timestamp, decision) VALUES (?, ?, ?, ?, ?)",
        (camera_id, event_type, confidence, event_timestamp, decision),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def query_past_incidents(camera_id, event_type, limit=10):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT decision FROM incidents WHERE camera_id = ? AND event_type = ? ORDER BY id DESC LIMIT ?",
        (camera_id, event_type, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def resolve_incident(incident_id: int, was_real: bool) -> bool:
    """Human confirms/rejects a flagged or escalated incident after the fact."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "UPDATE incidents SET decision = ? WHERE id = ?",
        ("confirmed_real" if was_real else "confirmed_false", incident_id),
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated