# config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sistema de Autenticación"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "dev-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 horas
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Añadir estos campos que están en tu archivo .env
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str
    FROM_NAME: str
    BASE_URL: str
    ENVIRONMENT: str
    
    # Para CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4200"
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()
