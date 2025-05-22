import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import traffic, cameras
from app.core.config import settings

app = FastAPI(
    title="NavFlow Traffic Detection API",
    description="Real-time traffic detection using YOLOv8",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(traffic.router, prefix="/api/v1/traffic", tags=["traffic"])
app.include_router(cameras.router, prefix="/api/v1/cameras", tags=["cameras"])

@app.get("/")
async def root():
    return {"message": "Welcome to NavFlow Traffic Detection API"} 