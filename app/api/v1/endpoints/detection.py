from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict, List
from pydantic import BaseModel
from app.services.detection_service import detection_service

router = APIRouter()

class DetectionResult(BaseModel):
    camera_id: str
    results: Dict
    timestamp: str

@router.post("/detect/{camera_id}")
async def detect_vehicles(
    camera_id: str,
    image: UploadFile = File(...)
):
    """Process an image from a camera for vehicle detection"""
    try:
        # Read image file
        contents = await image.read()
        
        # Process image
        results = detection_service.process_image(contents)
        
        # Store results
        detection_service.store_results(camera_id, results)
        
        return {
            "camera_id": camera_id,
            "results": results,
            "timestamp": results["timestamp"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/traffic-data/{camera_id}")
async def get_traffic_data(camera_id: str):
    """Get latest traffic data for a specific camera"""
    try:
        results = detection_service.get_latest_results(camera_id)
        if not results:
            raise HTTPException(status_code=404, detail="No data available for this camera")
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/traffic-data")
async def get_all_traffic_data():
    """Get traffic data from all cameras"""
    try:
        return detection_service.get_all_results()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/activate-all")
async def activate_all_cameras():
    """Activate all cameras for detection"""
    try:
        detection_service.activate_all_cameras()
        return {"message": "All cameras activated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deactivate-all")
async def deactivate_all_cameras():
    """Deactivate all cameras"""
    try:
        detection_service.deactivate_all_cameras()
        return {"message": "All cameras deactivated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 