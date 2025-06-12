"""
Camera service for handling video streams
"""
import cv2
import numpy as np
import requests
import re
from typing import Dict, Optional, Tuple, List
from app.core.config import settings
from app.core.camera_api import CAMERA_CONFIGS

class CameraService:
    def __init__(self):
        self.cameras: Dict[str, cv2.VideoCapture] = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'image/avif,image/webp,image/apng,*/*',
            'Referer': 'http://giaothong.hochiminhcity.gov.vn/',
        })
        # Initialize cameras from config
        for config in CAMERA_CONFIGS:
            self.add_camera(config["id"], config["url"])

    async def get_frame(self, camera_id: str) -> Optional[np.ndarray]:
        """
        Get frame from camera without storing it
        """

        # If it's a URL camera
        if isinstance(self.cameras[camera_id], str):
            return await self._fetch_url_frame(self.cameras[camera_id])
        
        # If it's a VideoCapture object
        cap = self.cameras[camera_id]
        ret, frame = cap.read()
        
        if ret:
            return frame
        return None

    async def _fetch_url_frame(self, api_url: str) -> Optional[np.ndarray]:
        """
        Fetch frame from HCMC traffic camera URL without storing
        """
        try:
            cam_id_match = re.search(r'camId=([^&]+)', api_url)
            if cam_id_match:
                cam_id = cam_id_match.group(1)
                image_url = f"http://giaothong.hochiminhcity.gov.vn/render/ImageHandler.ashx?id={cam_id}"
                img_response = self.session.get(image_url, timeout=settings.CAMERA_TIMEOUT, stream=True)
                
                if img_response.status_code == 200 and img_response.headers.get('content-type', '').startswith('image/'):
                    img_array = np.asarray(bytearray(img_response.content), dtype=np.uint8)
                    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    if frame is not None:
                        return frame
                
        except requests.RequestException as error:
            print(f"Error accessing image URL: {error}")
        return None

    def get_all_cameras(self) -> List[dict]:
        """
        Get all camera configurations
        """
        return [
            {
                "id": config["id"],
                "name": config["name"],
                "coordinates": config["coordinates"],
                "status": "active" if config["id"] in self.cameras else "inactive"
            }
            for config in CAMERA_CONFIGS
        ]

    def get_all_stats(self) -> Dict[str, dict]:
        """
        Get statistics for all cameras from real detection results if available
        """
        stats = {}
        for config in CAMERA_CONFIGS:
            camera_id = config["id"]
            detection = traffic_service.get_latest_results(camera_id)
            if detection and "results" in detection:
                res = detection["results"]
                stats[camera_id] = {
                    "total_vehicles": res.get("total_vehicles", 0),
                    "flow_rate": res.get("flow_rate", 0.0),
                    "vehicle_types": res.get("vehicle_types", {}),
                    "timestamp": detection.get("timestamp", "")
                }
            else:
                stats[camera_id] = {
                    "total_vehicles": 0,
                    "flow_rate": 0.0,
                    "vehicle_types": {"car": 0, "truck": 0, "motorcycle": 0},
                    "timestamp": ""
                }
        return stats

    def list_cameras(self) -> list:
        """
        List available cameras
        """
        return list(self.cameras.keys())

    def add_camera(self, camera_id: str, source: str):
        if source.startswith('http'):
            self.cameras[camera_id] = source
        else:
            self.cameras[camera_id] = cv2.VideoCapture(source)

    def remove_camera(self, camera_id: str):
        """
        Remove a camera
        """
        if camera_id in self.cameras:
            if not isinstance(self.cameras[camera_id], str):
                self.cameras[camera_id].release()
            del self.cameras[camera_id]

# Create singleton instance
camera_service = CameraService() 