from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict
from app.services.camera_service import camera_service
from app.api.dependencies import verify_api_key
from camera_api import CAMERA_URLS

router = APIRouter()

@router.get("/", response_model=List[str])
async def list_cameras():
    """Get list of available cameras"""
    # Initialize cameras from CAMERA_URLS if not already in camera_service
    for camera_id, source in CAMERA_URLS.items():
        if camera_id not in camera_service.cameras:
            camera_service.add_camera(camera_id, source)
    return list(CAMERA_URLS.keys())

@router.post("/{camera_id}")
async def add_camera(
    camera_id: str,
    source: str = Query(None, description="Camera source URL or path")
):
    """Add a new camera"""
    try:
        camera_service.add_camera(camera_id, source)
        return {"message": f"Camera {camera_id} added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{camera_id}")
async def remove_camera(camera_id: str):
    """Remove a camera"""
    try:
        camera_service.remove_camera(camera_id)
        return {"message": f"Camera {camera_id} removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{camera_id}")
async def get_camera_status(camera_id: str):
    """Get camera status and last frame timestamp"""
    if camera_id not in camera_service.cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    return {
        "camera_id": camera_id,
        "is_active": camera_id in camera_service.cameras,
        "last_update": camera_service.last_update.get(camera_id),
        "source": camera_service.cameras[camera_id]
    } 