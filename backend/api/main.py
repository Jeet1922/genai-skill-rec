from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
from api.endpoints import recommend, ingest
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="GenAI Team Skill Recommendation System",
    description="AI-powered system for recommending role-based upskilling and cross-skilling to team members",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recommend.router, prefix="/api/v1", tags=["recommendations"])
app.include_router(ingest.router, prefix="/api/v1", tags=["ingestion"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GenAI Team Skill Recommendation System",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "recommendations": "/api/v1/recommend",
            "team_ingestion": "/api/v1/ingest/team",
            "document_ingestion": "/api/v1/ingest/documents"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "skill-recommendation-api",
        "version": "1.0.0"
    }

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": "The requested resource was not found",
            "path": str(request.url.path)
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "path": str(request.url.path)
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 