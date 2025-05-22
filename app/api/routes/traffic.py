from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
from typing import List, Dict
from app.services.yolo_service import yolo_service
from app.services.camera_service import camera_service
from app.services.detection_service import detection_service
import io

router = APIRouter()

@router.post("/start/{camera_id}")
async def start_detection(camera_id: str):
    """Start background detection for a camera"""
    if camera_id not in camera_service.cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    try:
        await detection_service.start_detection(camera_id)
        return {"message": f"Detection started for camera {camera_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop/{camera_id}")
async def stop_detection(camera_id: str):
    """Stop detection for a camera"""
    if camera_id not in camera_service.cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    try:
        await detection_service.stop_detection(camera_id)
        return {"message": f"Detection stopped for camera {camera_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/{camera_id}")
async def get_traffic_stats(camera_id: str):
    """Get traffic statistics for a camera"""
    if camera_id not in camera_service.cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    results = detection_service.get_latest_results(camera_id)
    if results is None:
        raise HTTPException(status_code=404, detail="No detection results available")
    
    return {
        "camera_id": camera_id,
        "timestamp": results["timestamp"],
        "fullness": results["results"]["fullness"],
        "total_vehicles": results["results"]["total_vehicles"],
        "detections": results["results"]["detections"]
    }

@router.get("/stream/{camera_id}")
async def stream_camera(camera_id: str):
    """Stream camera feed with detection overlay"""
    if camera_id not in camera_service.cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    try:
        # Get the latest detection results
        results = detection_service.get_latest_results(camera_id)
        
        # Get the current frame
        frame = await camera_service.get_frame(camera_id)
        if frame is None:
            raise HTTPException(status_code=404, detail="No frame available")
        
        # If we have detection results, draw them on the frame
        if results and "results" in results:
            frame = yolo_service.draw_detections(frame, results["results"]["detections"])
        
        # Convert frame to JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        return StreamingResponse(
            io.BytesIO(buffer.tobytes()),
            media_type="image/jpeg"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 