# Heuristic Traffic Signal Controller
import numpy as np
from datetime import datetime
import json

class HeuristicController:
    def __init__(self):
        self.min_green_time = 15
        self.max_green_time = 60
        self.yellow_time = 4
        self.red_clearance_time = 2

        # Traffic density thresholds
        self.low_density_threshold = 5
        self.medium_density_threshold = 15
        self.high_density_threshold = 30

    def calculate_phase_timing(self, junction_data):
        # Extract traffic data for each approach
        approaches = junction_data.get('approaches', {})
        total_vehicles = sum(approach.get('vehicle_count', 0) for approach in approaches.values())

        # Calculate base green time using Webster's formula
        cycle_time = self.calculate_optimal_cycle_time(junction_data)

        phase_timings = {}
        for phase_id, approach_data in approaches.items():
            flow_ratio = approach_data.get('flow_ratio', 0.3)
            saturation_flow = approach_data.get('saturation_flow', 1800)  # vehicles/hour

            # Calculate green time allocation
            green_time = max(
                self.min_green_time,
                min(
                    self.max_green_time,
                    (flow_ratio * (cycle_time - total_lost_time)) / sum(flow_ratios)
                )
            )

            phase_timings[phase_id] = {
                'green_time': int(green_time),
                'yellow_time': self.yellow_time,
                'red_time': int(cycle_time - green_time - self.yellow_time)
            }

        return phase_timings

    def calculate_optimal_cycle_time(self, junction_data):
        # Webster's optimal cycle time formula
        total_lost_time = 12  # seconds (startup + clearance losses)
        critical_flow_ratios = []

        approaches = junction_data.get('approaches', {})
        for approach_data in approaches.values():
            flow = approach_data.get('flow', 0)
            saturation_flow = approach_data.get('saturation_flow', 1800)
            critical_flow_ratios.append(flow / saturation_flow if saturation_flow > 0 else 0)

        Y = sum(critical_flow_ratios)

        if Y >= 1:
            Y = 0.9  # Cap to prevent oversaturation

        optimal_cycle = (1.5 * total_lost_time + 5) / (1 - Y)

        # Constrain to reasonable bounds
        return max(60, min(120, optimal_cycle))

    def adaptive_timing_adjustment(self, junction_id, current_traffic):
        # Real-time adjustment based on current conditions
        vehicle_count = current_traffic.get('vehicle_count', 0)
        queue_length = current_traffic.get('queue_length', 0)
        waiting_time = current_traffic.get('avg_waiting_time', 0)

        base_green = 30  # seconds

        # Density-based adjustment
        if vehicle_count > self.high_density_threshold:
            density_factor = 1.5
        elif vehicle_count > self.medium_density_threshold:
            density_factor = 1.2
        elif vehicle_count < self.low_density_threshold:
            density_factor = 0.8
        else:
            density_factor = 1.0

        # Queue-based adjustment
        queue_factor = 1.0 + min(0.5, queue_length * 0.05)

        # Waiting time adjustment
        waiting_factor = 1.0 + min(0.3, waiting_time * 0.01)

        # Calculate adjusted green time
        adjusted_green = base_green * density_factor * queue_factor * waiting_factor
        adjusted_green = max(self.min_green_time, min(self.max_green_time, adjusted_green))

        return {
            'junction_id': junction_id,
            'recommended_green_time': int(adjusted_green),
            'adjustment_factors': {
                'density_factor': density_factor,
                'queue_factor': queue_factor,
                'waiting_factor': waiting_factor
            },
            'reasoning': f'Vehicles: {vehicle_count}, Queue: {queue_length}, Wait: {waiting_time}s'
        }

    def emergency_override(self, junction_id, emergency_direction):
        # Emergency vehicle priority control
        emergency_timing = {
            'emergency_phase': {
                'green_time': 60,  # Extended green for emergency vehicle
                'yellow_time': 3,
                'red_time': 0
            },
            'other_phases': {
                'green_time': 0,
                'yellow_time': 0,
                'red_time': 63  # All other directions red
            }
        }

        return {
            'junction_id': junction_id,
            'emergency_override': True,
            'emergency_direction': emergency_direction,
            'timing': emergency_timing,
            'duration': 60,  # seconds
            'priority_level': 'high'
        }

    def coordination_control(self, corridor_junctions, target_speed=50):
        # Coordinate multiple junctions for green wave
        coordination_plan = {}

        distance_between_junctions = 400  # meters (typical)
        travel_time = distance_between_junctions / (target_speed * 1000/3600)  # seconds

        for i, junction_id in enumerate(corridor_junctions):
            offset = i * travel_time

            coordination_plan[junction_id] = {
                'cycle_time': 90,  # seconds
                'offset': int(offset % 90),  # offset within cycle
                'green_start': int(offset % 90),
                'green_duration': 45,
                'coordination_group': 'main_corridor'
            }

        return coordination_plan

    def time_of_day_adjustment(self, junction_id, current_hour):
        # Adjust timing based on time of day patterns
        if 7 <= current_hour <= 9:  # Morning rush
            return {
                'adjustment_type': 'morning_rush',
                'green_extension': 15,
                'cycle_extension': 20,
                'priority_directions': ['eastbound', 'westbound']
            }
        elif 17 <= current_hour <= 19:  # Evening rush
            return {
                'adjustment_type': 'evening_rush',
                'green_extension': 15,
                'cycle_extension': 20,
                'priority_directions': ['westbound', 'eastbound']
            }
        elif 22 <= current_hour or current_hour <= 5:  # Night time
            return {
                'adjustment_type': 'night_time',
                'green_extension': -10,
                'cycle_extension': -30,
                'priority_directions': []
            }
        else:  # Regular hours
            return {
                'adjustment_type': 'regular',
                'green_extension': 0,
                'cycle_extension': 0,
                'priority_directions': []
            }

# Example usage
if __name__ == "__main__":
    controller = HeuristicController()

    # Example junction data
    junction_data = {
        'junction_id': 'J0',
        'approaches': {
            'north': {'vehicle_count': 12, 'flow': 800, 'saturation_flow': 1800},
            'south': {'vehicle_count': 8, 'flow': 600, 'saturation_flow': 1800},
            'east': {'vehicle_count': 15, 'flow': 900, 'saturation_flow': 1800},
            'west': {'vehicle_count': 10, 'flow': 700, 'saturation_flow': 1800}
        }
    }

    # Calculate optimal timing
    timing = controller.calculate_phase_timing(junction_data)
    print(f"Calculated phase timing: {timing}")

    # Adaptive adjustment
    current_traffic = {'vehicle_count': 25, 'queue_length': 8, 'avg_waiting_time': 15}
    adjustment = controller.adaptive_timing_adjustment('J0', current_traffic)
    print(f"Adaptive adjustment: {adjustment}")
