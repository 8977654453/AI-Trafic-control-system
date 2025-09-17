# SOS Emergency Response API
from fastapi import APIRouter, HTTPException
from datetime import datetime
import json
from typing import List, Dict

router = APIRouter(prefix="/api/sos", tags=["emergency"])

# In-memory storage for demo (would use database in production)
active_sos_requests = {}

@router.post("/submit")
async def submit_sos_request(sos_data: dict):
    sos_id = f"SOS_{int(datetime.now().timestamp())}"

    sos_request = {
        "id": sos_id,
        "user_id": sos_data.get("user_id", "anonymous"),
        "emergency_type": sos_data.get("emergency_type", "general"),
        "location": {
            "lat": sos_data.get("lat", 0),
            "lon": sos_data.get("lon", 0),
            "address": sos_data.get("address", "Unknown")
        },
        "description": sos_data.get("description", ""),
        "contact": sos_data.get("contact", ""),
        "timestamp": datetime.now().isoformat(),
        "status": "received",
        "priority": calculate_priority(sos_data.get("emergency_type", "general")),
        "response_time": None,
        "assigned_units": []
    }

    active_sos_requests[sos_id] = sos_request

    # Trigger green corridor creation
    create_green_corridor(sos_request)

    return {
        "sos_id": sos_id,
        "status": "received",
        "message": "Emergency services have been notified",
        "estimated_response_time": "5-8 minutes",
        "priority": sos_request["priority"]
    }

@router.get("/active")
async def get_active_sos():
    return list(active_sos_requests.values())

@router.get("/{sos_id}")
async def get_sos_details(sos_id: str):
    if sos_id not in active_sos_requests:
        raise HTTPException(status_code=404, detail="SOS request not found")

    return active_sos_requests[sos_id]

@router.put("/{sos_id}/status")
async def update_sos_status(sos_id: str, status_data: dict):
    if sos_id not in active_sos_requests:
        raise HTTPException(status_code=404, detail="SOS request not found")

    active_sos_requests[sos_id]["status"] = status_data.get("status")
    active_sos_requests[sos_id]["response_time"] = status_data.get("response_time")

    return {"message": "SOS status updated successfully"}

def calculate_priority(emergency_type: str) -> int:
    priorities = {
        "medical": 10,
        "fire": 9,
        "accident": 8,
        "crime": 7,
        "breakdown": 3,
        "general": 5
    }
    return priorities.get(emergency_type.lower(), 5)

def create_green_corridor(sos_request: dict):
    # Green corridor logic would interface with TraCI
    emergency_type = sos_request["emergency_type"]

    if emergency_type == "medical":
        route = ["J0", "J1", "J5"]  # Hospital route
    elif emergency_type == "fire":
        route = ["J2", "J6", "J3"]  # Fire station route
    else:
        route = ["J0", "J4", "J7"]  # Police station route

    sos_request["green_corridor"] = {
        "route": route,
        "duration": 120,  # seconds
        "created_at": datetime.now().isoformat()
    }

    return route
