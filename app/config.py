from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "My Backend API"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "mydb"

    # JWT
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS & Trusted Hosts
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # Supabase
    SUPABASE_URL: str = "https://your-project.supabase.co"
    SUPABASE_ANON_KEY: str = "your-supabase-anon-key"

    # DataForSEO
    DATAFORSEO_USERNAME: str = "your-dataforseo-username"
    DATAFORSEO_PASSWORD: str = "your-dataforseo-password"

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100   # max requests
    RATE_LIMIT_WINDOW: int = 60      # per X seconds

    # Request size limit (in bytes) — default 1MB
    MAX_REQUEST_SIZE: int = 1_048_576

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
