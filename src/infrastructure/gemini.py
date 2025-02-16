from google import genai
from google.genai import types
import os
from src.core.config import GENERATE_CONFIG

def init_gemini_client():
    """Initialize the Gemini AI client"""
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    location = os.getenv("GOOGLE_LOCATION")
    if not project_id or not location:
        raise ValueError("Missing required environment variables: GOOGLE_PROJECT_ID, GOOGLE_LOCATION")
    
    return genai.Client(
        vertexai=True,
        project=project_id,
        location=location,
    )

def get_model_name():
    """Get the Gemini model name"""
    return os.getenv("MODEL_NAME", "gemini-2.0-flash-exp")  # Updated default model name

def generate_content_stream(client, contents, config=None):
    """
    Generate content using Gemini AI with streaming
    
    Args:
        client: Initialized Gemini client
        contents: List of Content objects
        config: Optional generation config
    
    Returns:
        Generator yielding content chunks from the model
    """
    if config is None:
        config = GENERATE_CONFIG
        
    return client.models.generate_content_stream(
        model=get_model_name(),
        contents=contents,
        config=config
    ) 