import sys
from typing import List

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
 
    # BACKEND_CORS_ORIGINS is a comma-separated list of origins
    # e.g: http://localhost,http://localhost:4200,http://localhost:3000
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:8000",  # type: ignore
        "https://localhost:8000",  # type: ignore
    ]

    PROJECT_NAME: str = "Patient Survival API"

    class Config:
        case_sensitive = True

settings = Settings()