import asyncio, websockets, json, requests, time

SAFESTATION_WS = "ws://localhost:8000/ws/alerts"
SENTINEL_URL = "http://localhost:8001/events"
COOLDOWN_SECONDS = 30  # ignore repeat alerts from the same camera+type within this window

last_sent = {}

async def listen():
    async with websockets.connect(SAFESTATION_WS) as ws:
        print("Listening for SafeStation alerts...")
        async for message in ws:
            alert = json.loads(message)
            key = (alert["camera_id"], alert["event"])
            now = time.time()

            if key in last_sent and now - last_sent[key] < COOLDOWN_SECONDS:
                continue  # skip duplicate, still within cooldown

            last_sent[key] = now
            event = {
                "camera_id": alert["camera_id"],
                "event_type": alert["event"],
                "confidence": alert["confidence"],
                "timestamp": alert["timestamp"],
                "location": alert.get("location"),
            }
            print(f"\n📹 {event['event_type']} on camera {event['camera_id']}")
            try:
                r = requests.post(SENTINEL_URL, json=event, timeout=90)
                r.raise_for_status()
                data = r.json()
                print("🧠 Sentinel (raw):", data)
            except Exception as e:
                print(f"⚠️ Sentinel call failed: {e}")

if __name__ == "__main__":
    asyncio.run(listen())