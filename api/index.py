from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json

app = FastAPI()

# Enable CORS for all origins, all methods, all headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow requests from any origin
    allow_methods=["*"],  # allow POST, GET, etc.
    allow_headers=["*"],  # allow all headers
)

# Load telemetry JSON
with open("q-vercel-latency.json", "r") as f:
    telemetry = json.load(f)

@app.post("/analytics")
async def analytics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 999999)

    result = {}
    for region in regions:
        records = [r for r in telemetry if r["region"] == region]
        if not records:
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(l > threshold for l in latencies),
        }
    return result

