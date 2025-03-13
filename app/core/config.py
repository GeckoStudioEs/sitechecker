import os
from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, validator, PostgresDsn

class Settings(BaseSettings):
    # Entorno
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: PostgresDsn
    
    # Redis
    REDIS_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Crawler Settings
    USER_AGENT: str
    RESPECT_ROBOTS_TXT: bool = True
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    DELAY: float = 0.5
    MAX_PARALLEL_REQUESTS: int = 5
    
    # Email
    EMAIL_BACKEND: str
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USER: str
    EMAIL_PASSWORD: str
    FROM_EMAIL: str
    USE_TLS: bool
    
    # API Keys
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # Límites del sistema
    MAX_CRAWL_PAGES: int = 500
    MAX_KEYWORDS_FREE: int = 100
    MAX_COMPETITORS: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia de configuración global
settings = Settings()