from fastapi import APIRouter
from .endpoints import routing

router = APIRouter()
router.include_router(routing.router, prefix="", tags=["routing"])
