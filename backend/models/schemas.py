from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class RecommendationType(str, Enum):
    UPSKILL = "upskill"
    CROSS_SKILL = "cross_skill"

class TeamMember(BaseModel):
    name: str = Field(..., description="Team member's full name")
    role: str = Field(..., description="Current job role/title")
    level: str = Field(..., description="Experience level (Junior, Mid, Senior, Lead)")
    skills: List[str] = Field(..., description="List of current skills")
    years_experience: Optional[int] = Field(None, description="Years of experience")

class SkillRecommendation(BaseModel):
    skill_name: str = Field(..., description="Recommended skill name")
    description: str = Field(..., description="Description of the skill")
    priority: str = Field(..., description="Priority level (High, Medium, Low)")
    learning_path: List[str] = Field(..., description="Suggested learning path")
    estimated_time: str = Field(..., description="Estimated time to learn")
    source_documents: Optional[List[str]] = Field([], description="Source documents used")

class RecommendationRequest(BaseModel):
    member_name: str = Field(..., description="Team member's name")
    role: str = Field(..., description="Current role")
    skills: List[str] = Field(..., description="Current skills")
    recommendation_type: RecommendationType = Field(..., description="Type of recommendation")
    years_experience: Optional[int] = Field(None, description="Years of experience")
    target_role: Optional[str] = Field(None, description="Target role for cross-skill recommendations")

class RecommendationResponse(BaseModel):
    member_name: str = Field(..., description="Team member's name")
    recommendation_type: RecommendationType = Field(..., description="Type of recommendation")
    recommendations: List[SkillRecommendation] = Field(..., description="List of skill recommendations")
    reasoning: str = Field(..., description="AI reasoning for recommendations")
    total_recommendations: int = Field(..., description="Total number of recommendations")

class TeamUploadRequest(BaseModel):
    team_data: List[TeamMember] = Field(..., description="List of team members")

class TeamUploadResponse(BaseModel):
    message: str = Field(..., description="Upload status message")
    team_size: int = Field(..., description="Number of team members processed")
    roles_found: List[str] = Field(..., description="Unique roles found in the team")

class IngestRequest(BaseModel):
    file_path: str = Field(..., description="Path to document to ingest")
    document_type: str = Field(..., description="Type of document (pdf, docx, txt)")

class IngestResponse(BaseModel):
    message: str = Field(..., description="Ingestion status message")
    documents_processed: int = Field(..., description="Number of documents processed")
    chunks_created: int = Field(..., description="Number of text chunks created") 