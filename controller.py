# TraCI Controller for SUMO Traffic Management
import traci
import time
import json
import logging
from datetime import datetime

class TrafficController:
    def __init__(self, sumo_config):
        self.sumo_config = sumo_config
        self.junctions = ["J0", "J1", "J2", "J3", "J4", "J5", "J6", "J7", "J8", "J9"]
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def start_simulation(self):
        try:
            sumo_binary = "sumo-gui"
            sumo_cmd = [sumo_binary, "-c", self.sumo_config]
            traci.start(sumo_cmd)
            self.logger.info("SUMO simulation started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start SUMO: {e}")
            return False

    def get_traffic_data(self):
        traffic_data = {}
        try:
            for junction in self.junctions:
                vehicles = traci.junction.getLastStepVehicleNumber(junction)
                waiting_time = traci.junction.getLastStepMeanWaitingTime(junction)

                traffic_data[junction] = {
                    'vehicles': vehicles,
                    'waiting_time': waiting_time,
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Error getting traffic data: {e}")

        return traffic_data

    def adaptive_signal_control(self, junction_id):
        try:
            vehicle_count = traci.junction.getLastStepVehicleNumber(junction_id)

            if vehicle_count > 15:  # Heavy traffic
                green_duration = 60
            elif vehicle_count > 8:  # Moderate traffic
                green_duration = 40
            else:  # Light traffic
                green_duration = 25

            traci.trafficlight.setPhaseDuration(junction_id, green_duration)
            self.logger.info(f"Adaptive signal: {junction_id} set to {green_duration}s")

        except Exception as e:
            self.logger.error(f"Error in adaptive control: {e}")

    def run_controller(self):
        if not self.start_simulation():
            return

        try:
            while traci.simulation.getMinExpectedNumber() > 0:
                # Apply adaptive control to all junctions
                for junction in self.junctions:
                    self.adaptive_signal_control(junction)

                # Get current traffic data
                traffic_data = self.get_traffic_data()

                # Save to data logs
                with open("../data/logs/traffic_data.json", "a") as f:
                    f.write(json.dumps(traffic_data) + "\n")

                traci.simulationStep()
                time.sleep(0.1)

        except KeyboardInterrupt:
            self.logger.info("Controller stopped by user")
        finally:
            traci.close()

if __name__ == "__main__":
    controller = TrafficController("../sumo/config.sumocfg")
    controller.run_controller()
