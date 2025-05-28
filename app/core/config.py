import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base directory
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Traffic Detection API"
    
    # Camera settings
    CAMERA_UPDATE_INTERVAL: int = 5  # seconds
    CAMERA_TIMEOUT: int = 5  # seconds
    
    # Model settings
    MODEL_DIR: str = os.path.join(BASE_DIR, "ml", "models", "trained")
    CONFIDENCE_THRESHOLD: float = 0.25
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list = ["*"]  # In production, replace with specific origins

    MONGO_URI: str = ""
    JWT_SECRET_KEY: str = ""

    class Config:
        case_sensitive = True
        env_file = ".env"

# Create settings instance
settings = Settings() 