from pydantic import BaseModel
from typing import List, Optional

class CameraModel(BaseModel):
    camera_id: str
    name: str
    coordinates: List[float]
    status: str
    url: Optional[str] = None
