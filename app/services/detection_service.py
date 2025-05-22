"""
Detection service for handling traffic detection
"""
import asyncio
from typing import Dict, Optional, Tuple
from app.services.yolo_service import yolo_service
from app.services.camera_service import camera_service
from app.core.config import settings

class DetectionService:
    def __init__(self):
        self.active_detections: Dict[str, bool] = {}
        self.detection_tasks: Dict[str, asyncio.Task] = {}
        self.latest_results: Dict[str, dict] = {}  # Only stores detection results, not frames

    async def start_detection(self, camera_id: str):
        """Start detection for a camera"""
        if camera_id in self.active_detections and self.active_detections[camera_id]:
            return  # Already running
        
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
                    continue

                # Run detection and get both results and visualization
                results, vis_frame = await yolo_service.detect_with_visualization(frame)
                
                # Store only detection results, not the frame
                self.latest_results[camera_id] = {
                    "timestamp": asyncio.get_event_loop().time(),
                    "results": results,
                    "visualization": vis_frame  # This will be streamed directly to frontend
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

# Create singleton instance
detection_service = DetectionService() 