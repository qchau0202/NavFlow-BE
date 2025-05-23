from pydantic import BaseModel
from typing import List

class RouteRequest(BaseModel):
    start_id: str
    end_id: str
    num_paths: int = 3

class RouteResponse(BaseModel):
    paths: List[List[str]]
    costs: List[float] 