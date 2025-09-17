# Emergency SOS Handler for Traffic Management
import traci
import json
import time
from datetime import datetime

class SOSHandler:
    def __init__(self):
        self.active_sos = {}
        self.emergency_routes = {}

    def receive_sos(self, sos_data):
        sos_id = f"SOS_{int(time.time())}"

        sos_request = {
            'id': sos_id,
            'type': sos_data.get('emergency_type', 'general'),
            'location': sos_data.get('location', {}),
            'timestamp': datetime.now().isoformat(),
            'status': 'received',
            'priority': self.calculate_priority(sos_data.get('emergency_type'))
        }

        self.active_sos[sos_id] = sos_request
        self.create_green_corridor(sos_id, sos_request)

        return sos_id

    def calculate_priority(self, emergency_type):
        priorities = {
            'medical': 10,
            'fire': 9,
            'accident': 8,
            'crime': 7,
            'general': 5
        }
        return priorities.get(emergency_type, 5)

    def create_green_corridor(self, sos_id, sos_request):
        try:
            # Find route to nearest emergency service
            route_junctions = self.plan_emergency_route(sos_request)

            # Set all lights to green along the route
            for junction in route_junctions:
                traci.trafficlight.setPhase(junction, 0)  # Green phase
                traci.trafficlight.setPhaseDuration(junction, 120)  # 2 minutes

            self.emergency_routes[sos_id] = route_junctions

            print(f"Green corridor created for {sos_id}: {route_junctions}")

            # Log the emergency response
            self.log_emergency_response(sos_id, sos_request, route_junctions)

        except Exception as e:
            print(f"Error creating green corridor: {e}")

    def plan_emergency_route(self, sos_request):
        # Simplified route planning (would use advanced routing in real system)
        emergency_type = sos_request['type']

        if emergency_type == 'medical':
            return ["J0", "J1", "J5"]  # Route to hospital
        elif emergency_type == 'fire':
            return ["J0", "J2", "J6"]  # Route to fire station
        else:
            return ["J0", "J3", "J4"]  # Route to police station

    def log_emergency_response(self, sos_id, sos_request, route):
        log_entry = {
            'sos_id': sos_id,
            'emergency_type': sos_request['type'],
            'route': route,
            'response_time': datetime.now().isoformat(),
            'status': 'green_corridor_active'
        }

        with open("../data/logs/emergency_responses.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_active_sos(self):
        return list(self.active_sos.values())

    def complete_sos(self, sos_id):
        if sos_id in self.active_sos:
            self.active_sos[sos_id]['status'] = 'completed'

            # Reset traffic lights
            if sos_id in self.emergency_routes:
                for junction in self.emergency_routes[sos_id]:
                    traci.trafficlight.setPhase(junction, 0)

                del self.emergency_routes[sos_id]

            print(f"SOS {sos_id} completed and corridor cleared")

if __name__ == "__main__":
    handler = SOSHandler()
    print("SOS Handler initialized")
