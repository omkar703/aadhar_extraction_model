"""
Configuration management for the Aadhaar OCR application.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Model configuration
    MODEL_REPO_ID: str = "arnabdhar/YOLOv8-nano-aadhar-card"
    MODEL_FILENAME: str = "model.pt"
    MODEL_DIR: str = "./models"
    CONFIDENCE_THRESHOLD: float = 0.5
    
    # File upload configuration
    MAX_FILE_SIZE_MB: int = 10
    UPLOAD_DIR: str = "/tmp/uploads"
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png"}
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    RELOAD: bool = False
    
    # Logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # CORS configuration
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Tesseract configuration
    TESSERACT_CMD: Optional[str] = None  # Auto-detect if None
    TESSERACT_CONFIG: str = "--oem 3 --psm 6"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size from MB to bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    def ensure_directories(self):
        """Ensure required directories exist."""
        Path(self.MODEL_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.ensure_directories()
    return settings
