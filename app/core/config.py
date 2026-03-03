from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Project Metadata
    PROJECT_NAME: str = "CRM Intelligence Pipeline"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    
    # Database & Infrastructure
    DATABASE_URL: str = "sqlite:///./data/pipeline.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Transcription Settings
    WHISPER_MODEL: str = "small"  # tiny, base, small, medium, large-v3
    DEVICE: str = "cpu"          # Use "cuda" if you have a GPU
    
    # Pydantic configuration to read the .env file
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()