import os
from dotenv import load_dotenv
load_dotenv()
SENTINEL_API_KEY = os.environ.get("SENTINEL_API_KEY", "")
EVENT_SOURCE_PATH = os.environ.get("SENTINEL_EVENTS_PATH", "events.json")
NOTIFY_METHOD = os.environ.get("SENTINEL_NOTIFY", "console")  # "console" or "webhook"
WEBHOOK_URL = os.environ.get("SENTINEL_WEBHOOK_URL", "")