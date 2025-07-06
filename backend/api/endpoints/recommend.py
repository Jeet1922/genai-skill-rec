from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.schemas import (
    RecommendationRequest, 
    RecommendationResponse, 
    SkillRecommendation,
    RecommendationType
)
from agents.dynamic_upskill_agent import DynamicUpskillAgent
from agents.dynamic_crossskill_agent import DynamicCrossSkillAgent
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instances (in production, use dependency injection)
_upskill_agent = None
_crossskill_agent = None

def get_upskill_agent():
    """Get or create dynamic upskill agent instance"""
    global _upskill_agent
    if _upskill_agent is None:
        # Check for Groq API key
        if not os.getenv("GROQ_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="GROQ_API_KEY environment variable is required for dynamic recommendations"
            )
        
        # Use Llama 3 8B for fast responses
        _upskill_agent = DynamicUpskillAgent(model_name="llama3-8b-8192")
    
    return _upskill_agent

def get_crossskill_agent():
    """Get or create dynamic cross-skill agent instance"""
    global _crossskill_agent
    if _crossskill_agent is None:
        # Check for Groq API key
        if not os.getenv("GROQ_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="GROQ_API_KEY environment variable is required for dynamic recommendations"
            )
        
        # Use Llama 3 8B for fast responses
        _crossskill_agent = DynamicCrossSkillAgent(model_name="llama3-8b-8192")
    
    return _crossskill_agent

@router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Generate dynamic skill recommendations for a team member using real-time trends
    
    Args:
        request: Recommendation request with member details and type
        
    Returns:
        RecommendationResponse with personalized skill suggestions based on current trends
    """
    try:
        logger.info(f"Generating {request.recommendation_type} recommendations for {request.member_name}")
        
        # Validate request
        if not request.skills:
            raise HTTPException(status_code=400, detail="At least one skill is required")
        
        if not request.role:
            raise HTTPException(status_code=400, detail="Role is required")
        
        # Validate target_role for cross-skill recommendations
        if request.recommendation_type == RecommendationType.CROSS_SKILL and not request.target_role:
            raise HTTPException(status_code=400, detail="Target role is required for cross-skill recommendations")
        
        # Get appropriate dynamic agent based on recommendation type
        if request.recommendation_type == RecommendationType.UPSKILL:
            agent = get_upskill_agent()
            result = await agent.run(
                member_name=request.member_name,
                role=request.role,
                skills=request.skills,
                years_experience=request.years_experience or 1
            )
        elif request.recommendation_type == RecommendationType.CROSS_SKILL:
            agent = get_crossskill_agent()
            result = await agent.run(
                member_name=request.member_name,
                role=request.role,
                skills=request.skills,
                years_experience=request.years_experience or 1,
                target_role=request.target_role
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid recommendation type")
        
        # Format recommendations
        recommendations = []
        for rec in result.get("recommendations", []):
            if isinstance(rec, dict):
                recommendations.append(SkillRecommendation(
                    skill_name=rec.get("skill_name", ""),
                    description=rec.get("description", ""),
                    priority=rec.get("priority", "Medium"),
                    learning_path=rec.get("learning_path", []),
                    estimated_time=rec.get("estimated_time", "4-8 weeks"),
                    source_documents=rec.get("source_documents", [])
                ))
            elif isinstance(rec, SkillRecommendation):
                recommendations.append(rec)
        
        response = RecommendationResponse(
            member_name=request.member_name,
            recommendation_type=request.recommendation_type,
            recommendations=recommendations,
            reasoning=result.get("reasoning", "Generated personalized recommendations based on current industry trends."),
            total_recommendations=len(recommendations)
        )
        
        logger.info(f"Generated {len(recommendations)} dynamic recommendations for {request.member_name}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    groq_key_status = "configured" if os.getenv("GROQ_API_KEY") else "missing"
    return {
        "status": "healthy", 
        "service": "dynamic-skill-recommendation-api",
        "groq_api_key": groq_key_status
    }

@router.get("/trends/{role}")
async def get_current_trends(role: str):
    """
    Get current industry trends for a specific role
    
    Args:
        role: Job role to get trends for
        
    Returns:
        Current trends data
    """
    try:
        from data_sources.trend_analyzer import TrendAnalyzer
        
        async with TrendAnalyzer() as analyzer:
            trends_data = await analyzer.get_comprehensive_trends(role, [])
            
        return {
            "role": role,
            "trends": trends_data.get("trends", []),
            "sources": trends_data.get("sources", {}),
            "timestamp": trends_data.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Failed to get trends: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")

@router.post("/switch-model")
async def switch_model(model_type: str, recommendation_type: str):
    """
    Switch to a different Groq model for recommendations
    
    Args:
        model_type: "fast", "balanced", or "powerful"
        recommendation_type: "upskill" or "cross_skill"
    """
    try:
        if recommendation_type == "upskill":
            agent = get_upskill_agent()
        elif recommendation_type == "cross_skill":
            agent = get_crossskill_agent()
        else:
            raise HTTPException(status_code=400, detail="Invalid recommendation type")
        
        agent.switch_model(model_type)
        
        return {
            "message": f"Switched to {model_type} model for {recommendation_type} recommendations",
            "model_type": model_type,
            "recommendation_type": recommendation_type
        }
        
    except Exception as e:
        logger.error(f"Failed to switch model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to switch model: {str(e)}") 