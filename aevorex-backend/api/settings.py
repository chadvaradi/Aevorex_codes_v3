"""
Application settings using Pydantic Settings
"""
from dotenv import load_dotenv
import os
from typing import List

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # Basic app settings
        self.env = os.getenv("ENV", "local")
        self.api_title = os.getenv("API_TITLE", "Aevorex Backend")
        self.api_version = os.getenv("API_VERSION", "0.1.0")
        
        # CORS settings
        cors_origins_str = os.getenv("CORS_ORIGINS", "*")
        self.cors_origins = [origin.strip() for origin in cors_origins_str.split(',') if origin.strip()]
        
        # API Keys
        self.eodhd_api_key = os.getenv("EODHD_API_KEY", "").strip()
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        # Gemini API key with fallback
        self.google_api_key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GEMINI_API_KEY_SECOND", "").strip()
        
        # LLM settings
        self.llm_provider = os.getenv("LLM_PROVIDER", "openrouter")
        self.default_model = os.getenv("DEFAULT_MODEL", "openrouter/gpt-4o-mini")
        
        # Image storage settings
        self.image_output_dir = os.getenv("IMAGE_OUTPUT_DIR", "static/images")
        self.image_base_url = os.getenv("IMAGE_BASE_URL", "http://localhost:8000/static/images")
        self.image_include_b64 = os.getenv("IMAGE_INCLUDE_B64", "false").lower() in ("true", "1", "yes")
        
        # Database settings (for future use)
        self.database_url = os.getenv("DATABASE_URL", "")
        
        # JWT settings (for future use)
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")


# Global settings instance
settings = Settings()
