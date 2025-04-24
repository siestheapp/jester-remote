"""
Configuration management for the Jester application.
This module provides a centralized configuration system.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class."""
    
    # API settings
    API_TITLE = "Jester API"
    API_DESCRIPTION = "API for processing size guides and providing size recommendations"
    API_VERSION = "1.0.0"
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    OPENAI_VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4-vision-preview")
    
    # Database settings
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # File paths
    DATA_DIR = os.getenv("DATA_DIR", "data")
    LOGS_DIR = os.getenv("LOGS_DIR", "logs")
    UPLOADS_DIR = os.getenv("UPLOADS_DIR", "uploads")
    
    # Vector search settings
    VECTOR_DIMENSION = 1536  # OpenAI text-embedding-3-small dimension
    VECTOR_INDEX_PATH = os.path.join(DATA_DIR, "vector_index.faiss")
    VECTOR_METADATA_PATH = os.path.join(DATA_DIR, "vector_metadata.json")
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """Get all configuration values."""
        return {key: value for key, value in cls.__dict__.items() 
                if not key.startswith('_') and key.isupper()}
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return getattr(cls, key, default)

# Create configuration instance
config = Config() 