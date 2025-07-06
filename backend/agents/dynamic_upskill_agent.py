from langgraph.graph import StateGraph, END
from typing import Dict, Any, List, TypedDict
from llm.groq_client import DynamicSkillRecommender
from data_sources.trend_analyzer import TrendAnalyzer
from models.schemas import SkillRecommendation
import logging

logger = logging.getLogger(__name__)

class DynamicAgentState(TypedDict):
    """State for the dynamic upskill agent"""
    member_name: str
    role: str
    skills: List[str]
    years_experience: int
    trends_data: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    reasoning: str
    context_sources: List[str]
    trending_skills: List[str]
    missing_trending_skills: List[str]

class DynamicUpskillAgent:
    """
    Dynamic upskill agent using real-time trends and Groq LLMs
    """
    
    def __init__(self, model_name: str = "llama3-8b-8192"):
        """
        Initialize the dynamic upskill agent
        
        Args:
            model_name: Groq model to use
        """
        self.recommender = DynamicSkillRecommender(model_name)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create the state graph
        workflow = StateGraph(DynamicAgentState)
        
        # Add nodes
        workflow.add_node("fetch_trends", self._fetch_real_time_trends)
        workflow.add_node("analyze_skill_gaps", self._analyze_skill_gaps)
        workflow.add_node("generate_recommendations", self._generate_dynamic_recommendations)
        workflow.add_node("validate_and_rank", self._validate_and_rank_recommendations)
        
        # Define the flow
        workflow.set_entry_point("fetch_trends")
        workflow.add_edge("fetch_trends", "analyze_skill_gaps")
        workflow.add_edge("analyze_skill_gaps", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "validate_and_rank")
        workflow.add_edge("validate_and_rank", END)
        
        return workflow.compile()
    
    async def _fetch_real_time_trends(self, state: DynamicAgentState) -> DynamicAgentState:
        """Fetch real-time industry trends"""
        try:
            role = state["role"]
            skills = state["skills"]
            
            # Use TrendAnalyzer with async context manager
            async with TrendAnalyzer() as analyzer:
                # Fetch comprehensive trends
                trends_data = await analyzer.get_comprehensive_trends(role, skills)
            
            state["trends_data"] = trends_data
            
            logger.info(f"Fetched {len(trends_data.get('trends', []))} trends for {role}")
            
        except Exception as e:
            logger.error(f"Failed to fetch trends: {e}")
            state["trends_data"] = {
                "role": role,
                "skills": skills,
                "trends": [],
                "sources": {},
                "error": str(e)
            }
        
        return state
    
    def _analyze_skill_gaps(self, state: DynamicAgentState) -> DynamicAgentState:
        """Analyze skill gaps based on current trends"""
        try:
            trends = state["trends_data"].get("trends", [])
            current_skills = set(state["skills"])
            
            # Extract trending skills from trends data
            trending_skills = set()
            for trend in trends:
                if "skill" in trend:
                    trending_skills.add(trend["skill"])
                elif "title" in trend:
                    # Extract skills from trend titles
                    title = trend["title"].lower()
                    # Add common skill keywords found in titles
                    skill_keywords = ["python", "javascript", "react", "docker", "kubernetes", "aws", "machine learning", "data science"]
                    for keyword in skill_keywords:
                        if keyword in title:
                            trending_skills.add(keyword.title())
            
            # Identify missing trending skills
            missing_trending_skills = trending_skills - current_skills
            
            # Add to state for recommendation generation
            state["trending_skills"] = list(trending_skills)
            state["missing_trending_skills"] = list(missing_trending_skills)
            
            logger.info(f"Identified {len(missing_trending_skills)} trending skills not in current skill set")
            
        except Exception as e:
            logger.error(f"Failed to analyze skill gaps: {e}")
            state["trending_skills"] = []
            state["missing_trending_skills"] = []
        
        return state
    
    def _generate_dynamic_recommendations(self, state: DynamicAgentState) -> DynamicAgentState:
        """Generate recommendations using Groq LLM and real-time trends"""
        try:
            role = state["role"]
            skills = state["skills"]
            trends = state["trends_data"].get("trends", [])
            years_experience = state["years_experience"]
            
            # Generate recommendations using the dynamic recommender
            result = self.recommender.get_upskill_recommendations(
                role=role,
                skills=skills,
                trends=trends,
                years_experience=years_experience
            )
            
            state["recommendations"] = result.get("recommendations", [])
            state["reasoning"] = result.get("reasoning", "Generated recommendations based on current trends")
            
            # Extract context sources
            sources = state["trends_data"].get("sources", {})
            context_sources = []
            for source_type, count in sources.items():
                if count > 0:
                    context_sources.append(f"{source_type}: {count} items")
            
            state["context_sources"] = context_sources
            
            logger.info(f"Generated {len(state['recommendations'])} dynamic recommendations")
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            state["recommendations"] = []
            state["reasoning"] = f"Failed to generate recommendations: {str(e)}"
            state["context_sources"] = []
        
        return state
    
    def _validate_and_rank_recommendations(self, state: DynamicAgentState) -> DynamicAgentState:
        """Validate and rank recommendations"""
        try:
            recommendations = state["recommendations"]
            
            # Filter out invalid recommendations
            valid_recommendations = []
            for rec in recommendations:
                if isinstance(rec, dict) and rec.get("skill_name"):
                    valid_recommendations.append(rec)
            
            # Sort by priority
            priority_order = {"High": 3, "Medium": 2, "Low": 1}
            valid_recommendations.sort(
                key=lambda x: priority_order.get(x.get("priority", "Low"), 1), 
                reverse=True
            )
            
            # Limit to top recommendations
            if len(valid_recommendations) > 5:
                valid_recommendations = valid_recommendations[:5]
            
            state["recommendations"] = valid_recommendations
            
            logger.info(f"Validated and ranked {len(valid_recommendations)} recommendations")
            
        except Exception as e:
            logger.error(f"Failed to validate recommendations: {e}")
            state["recommendations"] = []
        
        return state
    
    async def run(self, member_name: str, role: str, skills: List[str], 
                 years_experience: int = None) -> Dict[str, Any]:
        """
        Run the dynamic upskill agent workflow
        
        Args:
            member_name: Team member's name
            role: Current role
            skills: Current skills
            years_experience: Years of experience
            
        Returns:
            Dictionary with recommendations and metadata
        """
        try:
            # Initialize state
            initial_state = DynamicAgentState(
                member_name=member_name,
                role=role,
                skills=skills,
                years_experience=years_experience or 1,
                trends_data={},
                recommendations=[],
                reasoning="",
                context_sources=[],
                trending_skills=[],
                missing_trending_skills=[]
            )
            
            # Run the workflow (async)
            final_state = await self.graph.ainvoke(initial_state)
            
            # Format recommendations
            formatted_recommendations = []
            for rec in final_state["recommendations"]:
                if isinstance(rec, dict):
                    formatted_recommendations.append(SkillRecommendation(
                        skill_name=rec.get("skill_name", ""),
                        description=rec.get("description", ""),
                        priority=rec.get("priority", "Medium"),
                        learning_path=rec.get("learning_path", []),
                        estimated_time=rec.get("estimated_time", "4-8 weeks"),
                        source_documents=rec.get("source_evidence", [])
                    ))
            
            return {
                "recommendations": formatted_recommendations,
                "reasoning": final_state["reasoning"],
                "context_sources": final_state["context_sources"],
                "trends_analyzed": len(final_state["trends_data"].get("trends", [])),
                "total_recommendations": len(formatted_recommendations)
            }
            
        except Exception as e:
            logger.error(f"Dynamic upskill agent failed: {e}")
            return {
                "recommendations": [],
                "reasoning": f"Failed to generate recommendations: {str(e)}",
                "context_sources": [],
                "trends_analyzed": 0,
                "total_recommendations": 0
            }
    
    def switch_model(self, model_type: str):
        """Switch to a different Groq model"""
        self.recommender.switch_model(model_type) 