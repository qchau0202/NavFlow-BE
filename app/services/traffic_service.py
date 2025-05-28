"""
Traffic service for handling traffic detection and analysis
"""
import asyncio
from typing import Dict, Optional, Tuple
import cv2
import numpy as np
from app.services.yolo_service import yolo_service
from app.services.camera_service import camera_service
from app.core.config import settings
from app.core.camera_api import CAMERA_URLS

class TrafficService:
    def __init__(self):
        self.active_detections: Dict[str, bool] = {}
        self.detection_tasks: Dict[str, asyncio.Task] = {}
        self.latest_results: Dict[str, dict] = {}

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
        """Main detection loop for a camera"""
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
traffic_service = TrafficService() 