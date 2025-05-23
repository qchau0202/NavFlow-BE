import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base directories
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(BASE_DIR))
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Traffic Detection API"
    
    # Camera settings
    CAMERA_UPDATE_INTERVAL: int = 5  # seconds
    CAMERA_TIMEOUT: int = 10  # seconds
    
    # Model settings
    MODEL_DIR: str = os.path.join(BASE_DIR, "ml", "models", "trained")
    CONFIDENCE_THRESHOLD: float = 0.25
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list = ["*"]  # In production, replace with specific origins

    class Config:
        case_sensitive = True

# Create settings instance
settings = Settings() 