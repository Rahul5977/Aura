from decouple import config
from typing import List

class Settings:
    """Application settings and configuration."""
    
    # Database
    DATABASE_URL: str = config("DATABASE_URL", default="postgresql://postgres:postgres@localhost:5433/aura_db")
    
    # JWT Authentication
    SECRET_KEY: str = config("SECRET_KEY", default="your-super-secret-jwt-key-change-this-in-production")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    
    # Security
    ALLOWED_DOMAINS: List[str] = config("ALLOWED_DOMAINS", default="@iitbhilai.ac.in").split(",")
    
    # Application
    DEBUG: bool = config("DEBUG", default=True, cast=bool)
    PROJECT_NAME: str = "Aura ML Platform"
    VERSION: str = "1.0.0"

settings = Settings()