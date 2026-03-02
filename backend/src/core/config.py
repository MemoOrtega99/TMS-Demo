"""
Configuración central de la aplicación
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator
import json


class Settings(BaseSettings):
    # ======================
    # Database
    # ======================
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "soluciones_tms"
    POSTGRES_USER: str = "soluciones_user"
    POSTGRES_PASSWORD: str = "demo_password_2026"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def DATABASE_URL_SYNC(self) -> str:
        """URL síncrona para Alembic"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # ======================
    # Redis
    # ======================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # ======================
    # Auth
    # ======================
    JWT_SECRET_KEY: str = "soluciones-tms-super-secret-key-2026-demo"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 horas para demo

    # ======================
    # CORS
    # ======================
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3002", "http://localhost:3001"]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    # ======================
    # AI (OpenRouter)
    # ======================
    OPENROUTER_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
