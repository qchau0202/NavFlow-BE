"""
Test script for YOLO model
"""
import cv2
import numpy as np
from app.services.yolo_service import yolo_service
from app.services.camera_service import camera_service
import asyncio

async def test_camera_detection(camera_id: str):
    """Test detection on a camera feed"""
    # Get frame from camera
    frame = await camera_service.get_frame(camera_id)
    if frame is None:
        print(f"Could not get frame from camera {camera_id}")
        return

    # Perform detection
    results = await yolo_service.detect_traffic(frame)
    
    # Draw detections
    annotated_frame = yolo_service.draw_detections(frame, results["detections"])
    
    # Print results
    print(f"\nDetection Results for camera {camera_id}:")
    print(f"Total vehicles detected: {results['total_vehicles']}")
    print(f"Road fullness: {results['fullness']:.2f}%")
    print("\nDetections:")
    for det in results["detections"]:
        print(f"- {det['label']}: {det['confidence']:.2f}")

    # Save annotated image
    output_path = f"test_detection_{camera_id}.jpg"
    cv2.imwrite(output_path, annotated_frame)
    print(f"\nAnnotated image saved to {output_path}")

async def test_image_detection(image_path: str):
    """Test detection on a single image"""
    # Read image
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"Could not read image {image_path}")
        return

    # Perform detection
    results = await yolo_service.detect_traffic(frame)
    
    # Draw detections
    annotated_frame = yolo_service.draw_detections(frame, results["detections"])
    
    # Print results
    print(f"\nDetection Results for image {image_path}:")
    print(f"Total vehicles detected: {results['total_vehicles']}")
    print(f"Road fullness: {results['fullness']:.2f}%")
    print("\nDetections:")
    for det in results["detections"]:
        print(f"- {det['label']}: {det['confidence']:.2f}")

    # Save annotated image
    output_path = f"test_detection_{image_path.split('/')[-1]}"
    cv2.imwrite(output_path, annotated_frame)
    print(f"\nAnnotated image saved to {output_path}")

async def main():
    # Test with a camera
    print("\nTesting with camera...")
    camera_id = "test"  # Use your camera ID
    camera_service.add_camera(camera_id, "0")  # Use webcam for testing
    await test_camera_detection(camera_id)
    
    # Test with an image
    print("\nTesting with image...")
    image_path = "test_image.jpg"  # Replace with your test image path
    await test_image_detection(image_path)

if __name__ == "__main__":
    asyncio.run(main()) 