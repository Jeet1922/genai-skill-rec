#!/usr/bin/env python3
"""
Startup script for the GenAI Team Skill Recommendation System
"""
import sys
import os
import logging

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.main import app
import uvicorn

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 