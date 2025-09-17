# FastAPI Backend for Smart Traffic Management System
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import asyncio
from datetime import datetime
import sqlite3
from typing import List, Dict

app = FastAPI(title="Smart Traffic Management API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections
active_connections: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle WebSocket messages
            message = json.loads(data)
            await broadcast_message(message)
    except:
        active_connections.remove(websocket)

async def broadcast_message(message: dict):
    for connection in active_connections:
        try:
            await connection.send_text(json.dumps(message))
        except:
            active_connections.remove(connection)

@app.get("/")
async def root():
    return {"message": "Smart Traffic Management API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Traffic data endpoints
@app.get("/api/traffic/current")
async def get_current_traffic():
    # Mock traffic data - would connect to TraCI in real implementation
    traffic_data = {
        "junctions": {
            "J0": {"vehicles": 15, "waiting_time": 8.5, "status": "normal"},
            "J1": {"vehicles": 22, "waiting_time": 12.3, "status": "congested"},
            "J2": {"vehicles": 8, "waiting_time": 3.2, "status": "normal"},
            "J3": {"vehicles": 18, "waiting_time": 9.1, "status": "moderate"},
            "J4": {"vehicles": 12, "waiting_time": 5.7, "status": "normal"}
        },
        "timestamp": datetime.now().isoformat()
    }
    return traffic_data

@app.post("/api/sos/submit")
async def submit_sos(sos_data: dict):
    sos_id = f"SOS_{int(datetime.now().timestamp())}"

    # Process SOS request
    response = {
        "sos_id": sos_id,
        "status": "received",
        "message": "Emergency services have been notified",
        "estimated_response_time": "5-8 minutes"
    }

    # Broadcast SOS alert to connected clients
    await broadcast_message({
        "type": "sos_alert",
        "data": {"sos_id": sos_id, "emergency_type": sos_data.get("emergency_type")}
    })

    return response

@app.get("/api/violations/recent")
async def get_recent_violations():
    # Mock violation data
    violations = [
        {
            "id": "V001",
            "vehicle_id": "KA01AB1234",
            "type": "RED_LIGHT_VIOLATION",
            "location": "J0",
            "timestamp": "2024-01-15T10:30:00",
            "fine_amount": 1000,
            "status": "pending"
        },
        {
            "id": "V002", 
            "vehicle_id": "KA02CD5678",
            "type": "SPEEDING_VIOLATION",
            "location": "E0",
            "timestamp": "2024-01-15T11:15:00",
            "fine_amount": 500,
            "status": "pending"
        }
    ]
    return violations

@app.post("/api/route/optimize")
async def optimize_route(route_data: dict):
    origin = route_data.get("origin")
    destination = route_data.get("destination")

    # Mock route optimization - would use AI in real implementation
    optimized_route = {
        "route": [origin, "Junction_1", "Junction_2", destination],
        "distance": 12.5,
        "estimated_time": 18,
        "traffic_level": "moderate",
        "fuel_consumption": 1.2,
        "alternative_routes": [
            {"route": [origin, "Alt_1", destination], "time": 22, "distance": 14.2},
            {"route": [origin, "Alt_2", destination], "time": 25, "distance": 11.8}
        ]
    }

    return optimized_route

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
