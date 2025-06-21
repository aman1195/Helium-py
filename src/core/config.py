import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, Any, Optional

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration."""
    
    def __init__(self):
        # LLM Configuration
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google").lower()  # 'google' or 'openai'
        
        # Google Gemini API (Required if using Google's LLM)
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        if not self.GOOGLE_API_KEY and self.LLM_PROVIDER == "google":
            raise ValueError("GOOGLE_API_KEY is required when using Google's LLM provider")
        
        # OpenAI API (Required if using OpenAI's LLM)
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not self.OPENAI_API_KEY and self.LLM_PROVIDER == "openai":
            raise ValueError("OPENAI_API_KEY is required when using OpenAI's LLM provider")
        
        # Vector Database Configuration
        self.VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chroma").lower()
        self.VECTOR_DB_PATH = os.path.abspath(os.getenv("VECTOR_DB_PATH", "./data/vector_db"))
        
        # Create vector DB directory if it doesn't exist
        os.makedirs(self.VECTOR_DB_PATH, exist_ok=True)
        
        # RAG Configuration
        self.CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
        self.CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
        
        # Application Settings
        self.DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # Web Search (Optional)
        self.SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
        self.SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration based on the selected provider."""
        if self.LLM_PROVIDER == "google":
            return {
                "api_key": self.GOOGLE_API_KEY,
                "model": "gemini-pro",
                "temperature": 0.7,
                "max_tokens": 2048
            }
        elif self.LLM_PROVIDER == "openai":
            return {
                "api_key": self.OPENAI_API_KEY,
                "model": "gpt-4-turbo-preview",
                "temperature": 0.7,
                "max_tokens": 2048
            }
        raise ValueError(f"Unsupported LLM provider: {self.LLM_PROVIDER}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary, excluding sensitive information."""
        return {
            "LLM_PROVIDER": self.LLM_PROVIDER,
            "VECTOR_DB_TYPE": self.VECTOR_DB_TYPE,
            "VECTOR_DB_PATH": self.VECTOR_DB_PATH,
            "CHUNK_SIZE": self.CHUNK_SIZE,
            "CHUNK_OVERLAP": self.CHUNK_OVERLAP,
            "DEBUG": self.DEBUG,
            "LOG_LEVEL": self.LOG_LEVEL,
            "HAS_SEARCH_API": bool(self.SEARCH_API_KEY and self.SEARCH_ENGINE_ID)
        }

# Create a singleton instance
config = Config()

# For backward compatibility
LLM_PROVIDER = config.LLM_PROVIDER
GOOGLE_API_KEY = config.GOOGLE_API_KEY
OPENAI_API_KEY = config.OPENAI_API_KEY
DEBUG = config.DEBUG
LOG_LEVEL = config.LOG_LEVEL
