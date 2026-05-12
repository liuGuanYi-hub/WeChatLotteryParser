from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "微信抽奖解析器"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    OCR_CONFIDENCE_THRESHOLD: float = 0.8
    AVATAR_MIN_RADIUS: int = 30
    AVATAR_MAX_RADIUS: int = 80
    
    AVATAR_SIZE: int = 100
    
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: list = [".png", ".jpg", ".jpeg"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()