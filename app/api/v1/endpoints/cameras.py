from fastapi import APIRouter
from typing import List, Dict, Any
from ....services.camera_service import camera_service
import logging
import numpy as np

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_cameras():
    """Get list of all cameras"""
    return camera_service.get_all_cameras()

@router.post("/")
async def add_camera(camera: Dict[str, Any]):
    """Add a new camera"""
    return camera_service.add_camera(camera)

@router.delete("/{camera_id}")
async def remove_camera(camera_id: str):
    """Remove a camera"""
    return camera_service.remove_camera(camera_id)