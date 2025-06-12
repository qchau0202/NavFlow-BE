from fastapi import APIRouter
from .endpoints import cameras, traffic, auth

api_router = APIRouter()

# Include all endpoint routers with clear prefixes
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(traffic.router, prefix="/traffic", tags=["traffic"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["cameras"]) 