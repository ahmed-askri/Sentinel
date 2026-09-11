"""
Fires two requests at truly the same instant and times them,
to prove whether Sentinel handles them concurrently or serially.
"""
import time
import requests
from concurrent.futures import ThreadPoolExecutor

URL = "http://localhost:8001/events"

def fire(camera_id):
    start = time.time()
    r = requests.post(URL, json={
        "camera_id": camera_id,
        "event_type": "loitering",
        "confidence": 0.8,
        "timestamp": "2026-09-11T12:00:00",
        "location": "dock",
    })
    end = time.time()
    print(f"{camera_id}: started at {start:.2f} | finished at {end:.2f} | took {end - start:.2f}s")

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(fire, ["cam_test_1", "cam_test_2"])