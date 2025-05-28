import os
import cv2
import numpy as np
from typing import Dict, List, Any, Tuple
from ultralytics import YOLO
from app.core.config import settings
import requests
from pathlib import Path

def download_model_from_github():
    model_url = "https://github.com/qchau0202/NavFlow-ML/releases/download/v1.0.0/navflow_traffic_detection_v1.pt"
    model_path = Path(settings.MODEL_DIR) / "navflow_traffic_detection_v1.pt"
    
    # Check if model already exists
    if model_path.exists():
        print(f"Model already exists at {model_path}")
        return
    
    # Create the directory if it doesn't exist
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Download the model
    print(f"Downloading model from {model_url}...")
    response = requests.get(model_url)
    if response.status_code == 200:
        with open(model_path, 'wb') as f:
            f.write(response.content)
        print(f"Model downloaded successfully to {model_path}")
    else:
        print(f"Failed to download model: {response.status_code}")

class YOLOService:
    def __init__(self):
        self.model = None
        self.load_model()
        # Classes will be loaded from the model itself

    def load_model(self):
        """Load the custom trained YOLO model"""
        try:
            model_path = os.path.join(settings.MODEL_DIR, "navflow_traffic_detection_v1.pt")
            if not os.path.exists(model_path):
                download_model_from_github()  # Download if not found
            self.model = YOLO(model_path)
            print(f"Custom model loaded successfully from {model_path}")
            print(f"Model classes: {self.model.names}")
        except Exception as e:
            print(f"Error loading custom model: {e}")
            raise

    async def detect(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Perform traffic detection on a frame using custom model
        Returns detection results and road fullness
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
            
        try:
            # Run inference with custom model
            results = self.model(frame)
            
            # Calculate road fullness
            frame_area = frame.shape[0] * frame.shape[1]
            vehicle_area = 0
            detections = []

            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    label = self.model.names[class_id]  # Get label from model's class names
                    
                    # Calculate vehicle area
                    vehicle_area += (x2 - x1) * (y2 - y1)
                    
                    # Add detection
                    detections.append({
                        "label": label,
                        "confidence": confidence,
                        "bbox": [x1, y1, x2, y2],
                        "class_id": class_id
                    })

            # Calculate fullness
            fullness = (vehicle_area / frame_area) * 100

            return {
                "detections": detections,
                "fullness": fullness,
                "total_vehicles": len(detections)
            }
        except Exception as e:
            print(f"Error during detection: {e}")
            raise

    async def detect_with_visualization(self, frame: np.ndarray) -> Tuple[Dict, np.ndarray]:
        """
        Run detection and return both results and visualization frame
        """
        # Get detection results
        results = await self.detect(frame)
        
        # Create a copy of the frame for visualization
        vis_frame = frame.copy()
        
        # Draw bounding boxes and labels
        for detection in results["detections"]:
            x1, y1, x2, y2 = detection["bbox"]
            label = detection["label"]
            confidence = detection["confidence"]
            
            # Draw bounding box
            cv2.rectangle(vis_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            
            # Draw label
            label_text = f"{label}: {confidence:.2f}"
            cv2.putText(vis_frame, label_text, (int(x1), int(y1) - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Add total count
        cv2.putText(vis_frame, f"Total Vehicles: {results['total_vehicles']}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return results, vis_frame

    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """Draw detection boxes on the frame"""
        try:
            for det in detections:
                x1, y1, x2, y2 = det["bbox"]
                label = det["label"]
                conf = det["confidence"]
                
                # Draw box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw label
                cv2.putText(
                    frame,
                    f"{label} {conf:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )
            
            return frame
        except Exception as e:
            print(f"Error drawing detections: {e}")
            return frame

# Create singleton instance
yolo_service = YOLOService() 