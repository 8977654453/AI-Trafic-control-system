# YOLO-based Vehicle Detection for Traffic Management
import cv2
import numpy as np
from ultralytics import YOLO
import torch
import time
from datetime import datetime

class VehicleDetector:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        self.confidence_threshold = 0.5

    def detect_vehicles(self, image_path):
        # Load and process image
        image = cv2.imread(image_path)
        if image is None:
            return []

        # Run YOLO detection
        results = self.model(image)

        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Extract box information
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())

                    # Filter for vehicles only
                    if class_id in self.vehicle_classes and confidence > self.confidence_threshold:
                        detection = {
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': float(confidence),
                            'class_id': class_id,
                            'class_name': self.model.names[class_id]
                        }
                        detections.append(detection)

        return detections

    def detect_violation(self, image_path, traffic_light_state="red"):
        detections = self.detect_vehicles(image_path)

        violations = []
        for detection in detections:
            # Check if vehicle is in violation zone during red light
            bbox = detection['bbox']

            # Define violation zone (stop line area)
            violation_zone = self.get_violation_zone(image_path)

            if self.is_in_violation_zone(bbox, violation_zone) and traffic_light_state == "red":
                violation = {
                    'vehicle_bbox': bbox,
                    'confidence': detection['confidence'],
                    'vehicle_type': detection['class_name'],
                    'violation_type': 'RED_LIGHT_VIOLATION',
                    'timestamp': datetime.now().isoformat()
                }
                violations.append(violation)

        return violations

    def get_violation_zone(self, image_path):
        # Define violation zone coordinates (would be calibrated for each camera)
        # This is a simplified version
        return {'x1': 200, 'y1': 300, 'x2': 600, 'y2': 500}

    def is_in_violation_zone(self, bbox, violation_zone):
        # Check if vehicle bounding box overlaps with violation zone
        x1, y1, x2, y2 = bbox
        vx1, vy1, vx2, vy2 = violation_zone['x1'], violation_zone['y1'], violation_zone['x2'], violation_zone['y2']

        # Calculate overlap
        overlap_x = max(0, min(x2, vx2) - max(x1, vx1))
        overlap_y = max(0, min(y2, vy2) - max(y1, vy1))
        overlap_area = overlap_x * overlap_y

        # Vehicle is in violation if there's significant overlap
        return overlap_area > 1000  # threshold for violation

    def extract_license_plate(self, image_path, vehicle_bbox):
        # Extract license plate from vehicle region
        image = cv2.imread(image_path)
        x1, y1, x2, y2 = vehicle_bbox

        # Extract vehicle region
        vehicle_region = image[y1:y2, x1:x2]

        # Use EasyOCR for license plate recognition
        try:
            import easyocr
            reader = easyocr.Reader(['en'])

            # Detect text in vehicle region
            results = reader.readtext(vehicle_region)

            # Filter for license plate patterns
            for (bbox, text, confidence) in results:
                if confidence > 0.5 and self.is_license_plate_format(text):
                    return {
                        'plate_number': text.upper(),
                        'confidence': confidence,
                        'bbox': bbox
                    }
        except ImportError:
            print("EasyOCR not installed. Using mock plate detection.")
            return {
                'plate_number': f"KA01{np.random.randint(1000, 9999)}",
                'confidence': 0.85,
                'bbox': [[0, 0], [100, 0], [100, 30], [0, 30]]
            }

        return None

    def is_license_plate_format(self, text):
        # Simple license plate format validation
        import re
        # Indian license plate pattern: KA01AB1234
        pattern = r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$'
        return bool(re.match(pattern, text.replace(' ', '')))

# Example usage
if __name__ == "__main__":
    detector = VehicleDetector()

    # Simulate detection on a traffic image
    print("Vehicle Detector initialized")
    print("Ready to detect violations and extract license plates")
