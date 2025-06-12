from fastapi import APIRouter, HTTPException
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

# Traffic Detection Endpoints
@router.post("/detection/start-all")
async def start_all_detections():
    """Start background detection for all cameras"""
    try:
        # Initialize cameras if not already present
        for config in CAMERA_CONFIGS:
            if config["id"] not in camera_service.cameras:
                camera_service.add_camera(config["id"], config["url"])
        # Start detection for all cameras
        for config in CAMERA_CONFIGS:
            await traffic_service.start_detection(config["id"])
        return {"message": "Detection started for all cameras"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detection/stop-all")
async def stop_all_detections():
    """Stop detection for all cameras"""
    errors = []
    for config in CAMERA_CONFIGS:
        try:
            # Only stop if detection is active, otherwise skip
            if config["id"] in traffic_service.active_detections and traffic_service.active_detections[config["id"]]:
                await traffic_service.stop_detection(config["id"])
        except Exception as e:
            errors.append({"camera_id": config["id"], "error": str(e)})
    if errors:
        return {"message": "Some cameras failed to stop", "errors": errors}
    return {"message": "Detection stopped for all cameras"}

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

@router.get("/aggregated-stats")
async def get_aggregated_stats():
    """Get aggregated traffic statistics for all cameras"""
    results = list(traffic_service.latest_results.values())
    if not results:
        return {}
    # Aggregate stats
    total_fullness = 0
    total_flow_rate = 0
    total_vehicles = 0
    vehicle_types = {}
    confidence_scores = []
    detections = []
    timestamps = []
    camera_count = len(results)
    for entry in results:
        res = entry.get("results", {})
        total_fullness += res.get("fullness", 0)
        total_flow_rate += res.get("flow_rate", 0)
        total_vehicles += res.get("total_vehicles", 0)
        timestamps.append(entry.get("timestamp"))
        # Vehicle types
        for det in res.get("detections", []):
            label = det.get("label", "Unknown")
            vehicle_types[label] = vehicle_types.get(label, 0) + 1
            if det.get("confidence") is not None:
                confidence_scores.append(det["confidence"])
        detections.extend(res.get("detections", []))
    avg_conf = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    latest_timestamp = max(timestamps) if timestamps else None
    return {
        "fullness": total_fullness / camera_count if camera_count else 0,
        "flow_rate": total_flow_rate / camera_count if camera_count else 0,
        "total_vehicles": total_vehicles,
        "vehicle_types": vehicle_types,
        "average_confidence": avg_conf,
        "timestamp": latest_timestamp,
        "detections": detections[:10],
        "camera_count": camera_count,
    }

@router.get("/stats")
def get_all_camera_stats():
    """Get stats for all cameras (for HTTP polling)"""
    return traffic_service.get_all_stats() 