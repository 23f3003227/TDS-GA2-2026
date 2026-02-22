from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import json
import statistics
from typing import List

app = FastAPI()

# Enhanced CORS for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the telemetry data - Ensure telemetry.json is in the same folder!
try:
    with open("telemetry.json", "r") as f:
        telemetry_data = json.load(f)
except FileNotFoundError:
    telemetry_data = []

@app.get("/")
async def health_check():
    return {"status": "Vercel is live", "user": "23f3003227", "data_loaded": len(telemetry_data) > 0}

@app.post("/")
async def get_analytics(regions: List[str] = Body(..., embed=True), threshold_ms: int = Body(..., embed=True)):
    results = {}
    
    for region in regions:
        region_data = [d for d in telemetry_data if d["region"] == region]
        if not region_data:
            continue
            
        latencies = [d["latency"] for d in region_data]
        uptimes = [1 if d["status"] == "up" else 0 for d in region_data]
        
        # Calculate P95 using the statistics library
        results[region] = {
            "avg_latency": round(statistics.mean(latencies), 2),
            "p95_latency": round(statistics.quantiles(latencies, n=20)[18], 2),
            "avg_uptime": round(statistics.mean(uptimes), 4),
            "breaches": sum(1 for l in latencies if l > threshold_ms)
        }
        
    return results