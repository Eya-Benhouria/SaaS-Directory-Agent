"""
Application configuration using Pydantic Settings
"""
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "SaaS Directory Submission Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/saas_directory"
    DATABASE_SYNC_URL: str = "postgresql://postgres:postgres@localhost:5432/saas_directory"
    
    # Redis (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None  # For Gemini (FREE tier available)
    GROQ_API_KEY: Optional[str] = None    # For Groq (FREE tier available)
    LLM_PROVIDER: str = "gemini"  # openai, anthropic, gemini, or groq
    LLM_MODEL: str = "gemini-1.5-flash"
    
    # Browser Automation
    BROWSER_HEADLESS: bool = True
    BROWSER_TIMEOUT: int = 30000  # milliseconds
    MAX_CONCURRENT_SUBMISSIONS: int = 3
    
    # Demo Mode - When enabled, simulates successful submissions without real API calls
    # Set to false when you have a valid LLM API key
    DEMO_MODE: bool = False
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    # CORS - Allow all localhost variants for development
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost,http://localhost:80,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:5173"
    
    @property
    def cors_origins_list(self) -> list:
        """Parse CORS origins from comma-separated string"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
