import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME", "tailor_jester")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# API configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Vector database configuration
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "data/processed/jester_knowledge.index")
CHUNKS_PATH = os.getenv("CHUNKS_PATH", "data/processed/faiss_chunks.json")

# Data paths
RAW_DATA_PATH = os.getenv("RAW_DATA_PATH", "data/raw")
PROCESSED_DATA_PATH = os.getenv("PROCESSED_DATA_PATH", "data/processed")
BACKUP_PATH = os.getenv("BACKUP_PATH", "data/backups")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_PATH = os.getenv("LOG_PATH", "logs")

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
