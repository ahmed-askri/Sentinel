# Sentinel — Pluggable Agentic Reasoning Layer for Video Surveillance Systems

An LLM agent that reasons over security camera detections instead of alerting on every trigger — checks history, decides escalate vs. false alarm vs. needs-human-review, and explains why.

![demo](demo/sentinel_run.png)

## What it does
- Reasons over detection events using tool-calling (check history, escalate, flag for human review)
- Decoupled perception from reasoning — any camera pipeline can plug in, not just one
- Real incident database with a human-feedback loop: flagged incidents can be confirmed/rejected, feeding real ground truth back into future decisions
- Provider-agnostic LLM (built on Claude, swapped to Gemini with a 2-line change)
- Exposed as a persistent, SQLite-checkpointed REST API any pipeline can POST to

## Why it's built this way
Ports-and-adapters architecture: `source.py` (event input) and `notifiers.py` (alert output) are both swappable without touching the agent core in `agent/graph.py`. The agent itself only ever sees generic event dicts — it has no idea "camera" or "security" even exists, which is what makes it reusable across different surveillance domains, not just one project.

## Architecture
Camera pipeline → API layer (FastAPI) → Agent core (LangGraph) → Adapters (DB + notifier)

## Validated against a real pipeline
Integrated end-to-end with a real YOLO26x + MViTv2-S smoking-detection pipeline over a live WebSocket bridge — real detections, real agent reasoning, real decisions logged to a database (see `bridge.py`).

**Honest limitation**: on CPU-only hardware, sustaining stable real-time RTSP inference indefinitely hit real throughput limits (frame drops, read timeouts) — a genuine, common constraint in production CV systems, not a Sentinel bug. Diagnosed the cause (inference blocking the read loop) and confirmed clean, correct end-to-end runs rather than chasing indefinite live uptime on hardware not built for it.

## Quickstart
```bash
git clone <this-repo>
cd sentinel
pip install -r requirements.txt
# Create a .env file with GOOGLE_API_KEY=your-key (free at aistudio.google.com)
python main.py          # batch test on events.json
# or
uvicorn api.app:app --reload --port 8001   # real-time API
```

## What I'd do next
- Async request handling (currently synchronous, blocks under concurrent cameras)
- API key authentication on the `/events` endpoint
- Dockerize Sentinel itself for one-command deployment
- Structured per-decision logging (groundwork for a planned evaluation pipeline, AgentLens)

## Tech stack
`Python` `LangGraph` `Google Gemini API` `FastAPI` `SQLite` `WebSockets`