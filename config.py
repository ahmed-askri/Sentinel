import os
from dotenv import load_dotenv
load_dotenv()

EVENT_SOURCE_PATH = os.environ.get("SENTINEL_EVENTS_PATH", "events.json")
NOTIFY_METHOD = os.environ.get("SENTINEL_NOTIFY", "console")  # "console" or "webhook"
WEBHOOK_URL = os.environ.get("SENTINEL_WEBHOOK_URL", "")