import os
from typing import Optional

class Config:
    """Application configuration"""
    
    # Groq API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Model Configuration
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "llama3-8b-8192")
    AVAILABLE_MODELS = {
        "fast": "llama3-8b-8192",
        "balanced": "mixtral-8x7b-32768", 
        "powerful": "llama3-70b-8192"
    }
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Rate Limiting
    TREND_FETCH_RATE_LIMIT: int = int(os.getenv("TREND_FETCH_RATE_LIMIT", "10"))
    TREND_FETCH_PERIOD: int = int(os.getenv("TREND_FETCH_PERIOD", "1"))
    
    # Vector Store Configuration
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "data/vectorstore/skill_index")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is required")
        return True
    
    @classmethod
    def get_model_name(cls, model_type: str) -> str:
        """Get model name by type"""
        return cls.AVAILABLE_MODELS.get(model_type, cls.DEFAULT_MODEL) 