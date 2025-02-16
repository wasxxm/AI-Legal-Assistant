from pydantic import BaseModel
from google.genai import types
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Gemini Configuration
GENERATE_CONFIG = types.GenerateContentConfig(
    temperature=1,
    top_p=0.95,
    max_output_tokens=8192,
    response_modalities=["TEXT"],
    safety_settings=[
        types.SafetySetting(
            category="HARM_CATEGORY_HATE_SPEECH",
            threshold="OFF"
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="OFF"
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
            threshold="OFF"
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_HARASSMENT",
            threshold="OFF"
        )
    ]
)

class Settings(BaseModel):
    """Application settings"""
    APP_NAME: str = "Legal Case Analysis API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API for analyzing Pakistani legal cases using Google's Gemini AI"
    ALLOWED_ORIGIN: str = os.getenv("ALLOWED_ORIGIN", "http://localhost:3000")
    
    # Database settings
    DB_HOST: str = os.getenv("DB_HOST", "postgres")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "legal_db")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")

settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings 