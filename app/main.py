from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.services.yolo_service import download_model_from_github
from app.services.camera_service import camera_service
from app.core.camera_api import CAMERA_URLS
from app.core.mongo import verify_mongo_connection
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to NavFlow Traffic Detection API"}

@app.on_event("startup")
async def startup_event():
    try:
        # Download the model
        download_model_from_github()
        logger.info("Model downloaded successfully")
        
        # Initialize cameras from configuration
        for camera_id, url in CAMERA_URLS.items():
            camera_service.add_camera(camera_id, url)
        logger.info("Cameras initialized successfully")
        
        # Verify MongoDB connection
        verify_mongo_connection()
        logger.info("MongoDB connection verified")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise 