from fastapi import APIRouter
from app.api.v1.endpoints import traffic, auth

v1_router = APIRouter()

# Include all endpoint routers
v1_router.include_router(traffic.router, prefix="/traffic", tags=["traffic"])
v1_router.include_router(auth.router, prefix="/auth", tags=["auth"]) 