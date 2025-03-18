import os
from typing import Any, Dict, List, Optional

from pydantic import field_validator, model_validator, computed_field, PostgresDsn
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Aplicación
    APP_NAME: str = "SEO Analyzer"
    
    # Entorno
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str
    
    # Alias para mantener compatibilidad
    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.DATABASE_URL
    
    @computed_field
    @property
    def API_V1_STR(self) -> str:
        return self.API_V1_PREFIX
    
    @computed_field
    @property
    def CORS_ORIGINS(self) -> List[str]:
        return self.ALLOWED_ORIGINS
    
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
    
    # Aliases para mantener compatibilidad
    @computed_field
    @property
    def CRAWLER_USER_AGENT(self) -> str:
        return self.USER_AGENT
    
    @computed_field
    @property
    def CRAWLER_MAX_RETRIES(self) -> int:
        return self.MAX_RETRIES
    
    @computed_field
    @property
    def CRAWLER_DEFAULT_TIMEOUT(self) -> int:
        return self.TIMEOUT
    
    @computed_field
    @property
    def CRAWLER_MAX_PARALLEL_REQUESTS(self) -> int:
        return self.MAX_PARALLEL_REQUESTS
    
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

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # Permitir campos extra
    }

# Instancia de configuración global
settings = Settings()