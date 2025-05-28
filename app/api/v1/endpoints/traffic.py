from fastapi import APIRouter, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import io
from typing import List, Dict
from app.services.camera_service import camera_service
from app.services.traffic_service import traffic_service
from app.core.config import settings
from app.core.camera_api import CAMERA_CONFIGS, CAMERA_URLS

router = APIRouter()

# Camera Management Endpoints
@router.get("/cameras")
async def list_cameras():
    """Get list of available cameras with their details"""
    cameras = []
    for cam in CAMERA_CONFIGS:
        camera_info = {
            "id": cam["id"],
            "name": cam["name"],
            "coordinates": cam["coordinates"],
            "status": cam["status"],
            "url": cam["url"]
        }
        # Add detection status if available
        if cam["id"] in traffic_service.active_detections:
            camera_info["detection_status"] = "active"
        else:
            camera_info["detection_status"] = "inactive"
        cameras.append(camera_info)
    return cameras

@router.post("/cameras/{camera_id}")
async def add_camera(camera_id: str):
    """Add a new camera"""
    try:
        if camera_id not in CAMERA_URLS:
            raise HTTPException(status_code=404, detail="Camera not found in configuration")
        camera_service.add_camera(camera_id, CAMERA_URLS[camera_id])
        return {"message": f"Camera {camera_id} added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/cameras/{camera_id}")
async def remove_camera(camera_id: str):
    """Remove a camera"""
    try:
        camera_service.remove_camera(camera_id)
        return {"message": f"Camera {camera_id} removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Traffic Detection Endpoints
@router.post("/detection/start/{camera_id}")
async def start_detection(camera_id: str):
    """Start background detection for a camera"""
    if camera_id not in camera_service.cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    try:
        await traffic_service.start_detection(camera_id)
        return {"message": f"Detection started for camera {camera_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detection/stop/{camera_id}")
async def stop_detection(camera_id: str):
    """Stop detection for a camera"""
    if camera_id not in camera_service.cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    try:
        await traffic_service.stop_detection(camera_id)
        return {"message": f"Detection stopped for camera {camera_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detection/stats/{camera_id}")
async def get_traffic_stats(camera_id: str):
    """Get traffic statistics for a camera"""
    if camera_id not in camera_service.cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    results = traffic_service.get_latest_results(camera_id)
    if results is None:
        raise HTTPException(status_code=404, detail="No detection results available")
    
    return {
        "camera_id": camera_id,
        "timestamp": results["timestamp"],
        "fullness": results["results"]["fullness"],
        "total_vehicles": results["results"]["total_vehicles"],
        "detections": results["results"]["detections"]
    }

@router.get("/detection/stream/{camera_id}")
async def stream_camera(camera_id: str):
    """Stream camera feed with detection overlay"""
    if camera_id not in camera_service.cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    try:
        # Get the latest detection results
        results = traffic_service.get_latest_results(camera_id)
        
        # Get the current frame
        frame = await camera_service.get_frame(camera_id)
        if frame is None:
            raise HTTPException(status_code=404, detail="No frame available")
        
        # If we have detection results, draw them on the frame
        if results and "results" in results:
            frame = traffic_service.draw_detections(frame, results["results"]["detections"])
        
        # Convert frame to JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        return StreamingResponse(
            io.BytesIO(buffer.tobytes()),
            media_type="image/jpeg"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 