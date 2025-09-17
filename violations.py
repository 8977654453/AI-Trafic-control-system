# Traffic Violations Management API
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import json
from typing import List, Dict

router = APIRouter(prefix="/api/violations", tags=["violations"])

# Mock violation database
violations_db = [
    {
        "id": "V001",
        "vehicle_id": "KA01AB1234", 
        "driver_license": "DL123456789",
        "violation_type": "RED_LIGHT_VIOLATION",
        "location": "J0",
        "timestamp": "2024-01-15T10:30:15",
        "speed": 45.2,
        "speed_limit": 40,
        "evidence": {
            "photo": "evidence_001.jpg",
            "video": "evidence_001.mp4",
            "confidence": 0.95
        },
        "fine_amount": 1000,
        "status": "pending",
        "officer_notes": ""
    },
    {
        "id": "V002",
        "vehicle_id": "KA02CD5678",
        "driver_license": "DL987654321", 
        "violation_type": "SPEEDING_VIOLATION",
        "location": "E0",
        "timestamp": "2024-01-15T11:15:22",
        "speed": 72.5,
        "speed_limit": 50,
        "evidence": {
            "photo": "evidence_002.jpg",
            "radar_data": "speed_72.5_at_11:15:22",
            "confidence": 0.98
        },
        "fine_amount": 500,
        "status": "pending",
        "officer_notes": ""
    }
]

@router.get("/")
async def get_violations(status: str = None, limit: int = 50):
    filtered_violations = violations_db

    if status:
        filtered_violations = [v for v in violations_db if v["status"] == status]

    return filtered_violations[:limit]

@router.get("/{violation_id}")
async def get_violation_details(violation_id: str):
    violation = next((v for v in violations_db if v["id"] == violation_id), None)

    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")

    return violation

@router.post("/")
async def create_violation(violation_data: dict):
    violation_id = f"V{len(violations_db) + 1:03d}"

    new_violation = {
        "id": violation_id,
        "vehicle_id": violation_data.get("vehicle_id"),
        "violation_type": violation_data.get("violation_type"),
        "location": violation_data.get("location"),
        "timestamp": datetime.now().isoformat(),
        "evidence": violation_data.get("evidence", {}),
        "fine_amount": calculate_fine(violation_data.get("violation_type")),
        "status": "pending",
        "officer_notes": ""
    }

    violations_db.append(new_violation)
    return new_violation

@router.put("/{violation_id}/status")
async def update_violation_status(violation_id: str, status_data: dict):
    violation = next((v for v in violations_db if v["id"] == violation_id), None)

    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")

    violation["status"] = status_data.get("status", violation["status"])
    violation["officer_notes"] = status_data.get("officer_notes", violation["officer_notes"])

    return {"message": "Violation status updated successfully"}

@router.get("/analytics/summary")
async def get_violation_analytics():
    total_violations = len(violations_db)
    pending_violations = len([v for v in violations_db if v["status"] == "pending"])

    violation_types = {}
    total_fines = 0

    for violation in violations_db:
        v_type = violation["violation_type"]
        violation_types[v_type] = violation_types.get(v_type, 0) + 1
        total_fines += violation["fine_amount"]

    return {
        "total_violations": total_violations,
        "pending_violations": pending_violations,
        "violation_types": violation_types,
        "total_fine_amount": total_fines,
        "average_fine": total_fines / total_violations if total_violations > 0 else 0
    }

def calculate_fine(violation_type: str) -> int:
    fine_schedule = {
        "RED_LIGHT_VIOLATION": 1000,
        "SPEEDING_VIOLATION": 500,
        "WRONG_SIDE_DRIVING": 1500,
        "ILLEGAL_PARKING": 200,
        "MOBILE_PHONE_USE": 1000,
        "SEAT_BELT_VIOLATION": 500
    }
    return fine_schedule.get(violation_type, 500)
