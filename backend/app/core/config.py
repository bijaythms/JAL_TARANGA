"""
Jal Taranga Geospatial Platform - Core Configuration
Centralizes application settings, environment variable bindings, and filesystem paths.
"""

import os
from pathlib import Path
from typing import List

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field

    class Settings(BaseSettings):
        PROJECT_NAME: str = "Jal Taranga — India Geospatial Intelligence Engine"
        DESCRIPTION: str = "Comprehensive Earth-observation and hydrological modelling system for disaster resilience across India."
        VERSION: str = "23.0.0"
        API_PREFIX: str = "/api"

        # Security & Authentication
        ADMIN_SECRET_KEY: str = Field(default="VIP@DUK", validation_alias="ADMIN_SECRET_KEY")

        # Database Configuration
        DATABASE_URL: str = Field(default="postgresql://postgres:bijay@localhost:5432/vellam_db", validation_alias="DATABASE_URL")

        # Google Gemini AI Integration
        GEMINI_API_KEY: str = Field(default="", validation_alias="GEMINI_API_KEY")

        # Networking & Server Configuration
        HOST: str = os.getenv("HOST", "127.0.0.1")
        PORT: int = 8000
        CORS_ORIGINS: List[str] = ["*"]

        # Directories
        BASE_DIR: Path = Path(__file__).resolve().parent.parent
        DATA_DIR: Path = BASE_DIR / "data"
        FRONTEND_DIR: Path = BASE_DIR.parent.parent / "frontend"

        model_config = {
            "env_file": ".env",
            "extra": "ignore"
        }

except ImportError:
    # Fallback if pydantic-settings is not installed
    class Settings:  # type: ignore
        PROJECT_NAME: str = os.getenv(
            "PROJECT_NAME", "Jal Taranga — India Geospatial Intelligence Engine"
        )
        DESCRIPTION: str = (
            "Comprehensive Earth-observation and hydrological modelling system for disaster resilience across India."
        )
        VERSION: str = "23.0.0"
        API_PREFIX: str = "/api"

        ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY", "VIP@DUK")
        DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:bijay@localhost:5432/vellam_db")
        GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

        HOST: str = os.getenv("HOST", "127.0.0.1")
        PORT: int = int(os.getenv("PORT", "8000"))
        CORS_ORIGINS: List[str] = ["*"]

        BASE_DIR: Path = Path(__file__).resolve().parent.parent
        DATA_DIR: Path = BASE_DIR / "data"
        FRONTEND_DIR: Path = BASE_DIR.parent.parent / "frontend"


settings = Settings()
