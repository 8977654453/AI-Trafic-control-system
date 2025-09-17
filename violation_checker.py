# Traffic Violation Detection using SUMO data
import traci
import cv2
import numpy as np
from datetime import datetime
import json

class ViolationChecker:
    def __init__(self):
        self.violations = []
        self.speed_limits = {"E0": 50, "W0": 50, "N0": 40, "S0": 40}

    def check_red_light_violation(self, junction_id):
        violations = []
        try:
            tl_state = traci.trafficlight.getRedYellowGreenState(junction_id)
            incoming_edges = traci.junction.getIncomingEdges(junction_id)

            for i, edge in enumerate(incoming_edges):
                if i < len(tl_state) and tl_state[i] == 'r':  # Red light
                    vehicles = traci.edge.getLastStepVehicleIDs(edge)

                    for vehicle_id in vehicles:
                        position = traci.vehicle.getPosition(vehicle_id)
                        speed = traci.vehicle.getSpeed(vehicle_id)

                        # Check if vehicle is close to junction and moving
                        junction_pos = traci.junction.getPosition(junction_id)
                        distance = np.sqrt((position[0] - junction_pos[0])**2 + 
                                         (position[1] - junction_pos[1])**2)

                        if distance < 20 and speed > 2:  # Violation detected
                            violation = {
                                'vehicle_id': vehicle_id,
                                'type': 'RED_LIGHT_VIOLATION',
                                'location': junction_id,
                                'timestamp': datetime.now().isoformat(),
                                'evidence': self.capture_evidence(vehicle_id, junction_id)
                            }
                            violations.append(violation)

        except Exception as e:
            print(f"Error checking red light violations: {e}")

        return violations

    def check_speeding_violation(self, edge_id):
        violations = []
        speed_limit = self.speed_limits.get(edge_id, 50)

        try:
            vehicles = traci.edge.getLastStepVehicleIDs(edge_id)

            for vehicle_id in vehicles:
                speed = traci.vehicle.getSpeed(vehicle_id) * 3.6  # Convert to km/h

                if speed > speed_limit + 10:  # 10 km/h tolerance
                    violation = {
                        'vehicle_id': vehicle_id,
                        'type': 'SPEEDING_VIOLATION',
                        'location': edge_id,
                        'speed': speed,
                        'speed_limit': speed_limit,
                        'timestamp': datetime.now().isoformat(),
                        'evidence': self.capture_evidence(vehicle_id, edge_id)
                    }
                    violations.append(violation)

        except Exception as e:
            print(f"Error checking speeding violations: {e}")

        return violations

    def capture_evidence(self, vehicle_id, location):
        # Simulate evidence capture (would integrate with CCTV in real system)
        evidence = {
            'photo_id': f"evidence_{vehicle_id}_{int(datetime.now().timestamp())}",
            'location': location,
            'timestamp': datetime.now().isoformat(),
            'vehicle_plate': self.extract_plate_number(vehicle_id),
            'confidence': 0.95
        }
        return evidence

    def extract_plate_number(self, vehicle_id):
        # Simulate plate number extraction (would use OCR in real system)
        return f"KA01{vehicle_id[-4:].upper()}"

    def log_violation(self, violation):
        self.violations.append(violation)

        # Save to file
        with open("../data/logs/violations.json", "a") as f:
            f.write(json.dumps(violation) + "\n")

        print(f"Violation logged: {violation['type']} by {violation['vehicle_id']}")

if __name__ == "__main__":
    checker = ViolationChecker()
    print("Violation checker initialized")
