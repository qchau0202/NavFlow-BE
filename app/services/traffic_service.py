"""
Traffic service for handling traffic detection and analysis
"""
import asyncio
from typing import Dict, Optional, Tuple, List
import cv2
import numpy as np
from app.services.yolo_service import yolo_service
from app.services.camera_service import camera_service
from app.core.config import settings
from app.core.camera_api import CAMERA_URLS
import heapq
from datetime import datetime
import time

class TrafficService:
    def __init__(self):
        self.active_detections: Dict[str, bool] = {}
        self.detection_tasks: Dict[str, asyncio.Task] = {}
        self.latest_results: Dict[str, dict] = {}
        self.congestion_threshold = 0.7  # Threshold for considering a road congested

    async def start_detection(self, camera_id: str):
        """Start detection for a camera"""
        if camera_id in self.active_detections and self.active_detections[camera_id]:
            return  # Already running
        
        # Ensure camera is in camera_service
        if camera_id not in camera_service.cameras:
            if camera_id in CAMERA_URLS:
                camera_service.add_camera(camera_id, CAMERA_URLS[camera_id])
            else:
                raise ValueError(f"Camera {camera_id} not found in configuration")
        
        self.active_detections[camera_id] = True
        self.detection_tasks[camera_id] = asyncio.create_task(
            self._detection_loop(camera_id)
        )

    async def stop_detection(self, camera_id: str):
        """Stop detection for a camera"""
        if camera_id in self.active_detections:
            self.active_detections[camera_id] = False
            if camera_id in self.detection_tasks:
                self.detection_tasks[camera_id].cancel()
                try:
                    await self.detection_tasks[camera_id]
                except asyncio.CancelledError:
                    pass
                del self.detection_tasks[camera_id]
            if camera_id in self.latest_results:
                del self.latest_results[camera_id]

    async def _detection_loop(self, camera_id: str):
        while self.active_detections.get(camera_id, False):
            try:
                # Get frame from camera
                frame = await camera_service.get_frame(camera_id)
                if frame is None:
                    print(f"No frame available for camera {camera_id}")
                    await asyncio.sleep(1)
                    continue

                # Run detection and get both results and visualization
                results, vis_frame = await yolo_service.detect_with_visualization(frame)
                
                # Store only detection results, not the frame
                self.latest_results[camera_id] = {
                    "timestamp": asyncio.get_event_loop().time(),
                    "results": results,
                    "visualization": vis_frame
                }

                # Wait for next frame
                await asyncio.sleep(settings.CAMERA_UPDATE_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in detection loop for camera {camera_id}: {e}")
                await asyncio.sleep(1)  # Wait before retrying

    def get_latest_results(self, camera_id: str) -> Optional[dict]:
        """Get latest detection results for a camera"""
        return self.latest_results.get(camera_id)

    def draw_detections(self, frame: np.ndarray, detections: list) -> np.ndarray:
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

    def calculate_congestion_rate(self, detection_results: Dict) -> float:
        if not detection_results:
            return 0.0
            
        fullness = detection_results.get("fullness", 0)
        total_vehicles = detection_results.get("total_vehicles", 0)
        
        # Weighted combination of fullness and vehicle count
        congestion_rate = (fullness * 0.7) + (min(total_vehicles / 50, 1.0) * 0.3)
        return min(congestion_rate, 1.0)

    def get_congestion_data(self) -> Dict[str, float]:
        congestion_data = {}
        for camera_id, results in self.latest_results.items():
            if results and "results" in results:
                congestion_data[camera_id] = self.calculate_congestion_rate(results["results"])
            else:
                congestion_data[camera_id] = 0.0
        return congestion_data

    def get_all_stats(self) -> Dict[str, dict]:
        stats = {}
        now = time.time()
        window_seconds = 60  # 1 minute window for flow rate
        for camera_id in CAMERA_URLS.keys():
            latest = self.latest_results.get(camera_id)
            if latest and "results" in latest:
                res = latest["results"]
                # Vehicle type breakdown
                vehicle_types = {}
                for det in res.get("detections", []):
                    label = det.get("label", "Unknown")
                    vehicle_types[label] = vehicle_types.get(label, 0) + 1
                # Flow rate calculation (vehicles per minute)
                # Store detection history in latest_results if not present
                if "history" not in latest:
                    latest["history"] = []
                # Append current detection to history
                latest["history"].append({
                    "timestamp": latest["timestamp"],
                    "total_vehicles": res.get("total_vehicles", 0)
                })
                # Remove old entries
                latest["history"] = [h for h in latest["history"] if now - h["timestamp"] <= window_seconds]
                # Calculate flow rate as difference in vehicle count over time window
                history = latest["history"]
                if len(history) >= 2:
                    dt = history[-1]["timestamp"] - history[0]["timestamp"]
                    dv = history[-1]["total_vehicles"] - history[0]["total_vehicles"]
                    flow_rate = dv / (dt / 60) if dt > 0 else 0.0
                else:
                    flow_rate = 0.0
                stats[camera_id] = {
                    "total_vehicles": res.get("total_vehicles", 0),
                    "vehicle_types": vehicle_types,
                    "flow_rate": round(flow_rate, 2),
                    "fullness": res.get("fullness", 0.0),
                    "timestamp": latest.get("timestamp", "")
                }
            else:
                stats[camera_id] = {
                    "total_vehicles": 0,
                    "vehicle_types": {},
                    "flow_rate": 0.0,
                    "fullness": 0.0,
                    "timestamp": ""
                }
        return stats

# Create singleton instance
traffic_service = TrafficService() 