from langgraph.graph import StateGraph, END
from typing import Dict, Any, List, TypedDict
from llm.groq_client import DynamicSkillRecommender
from data_sources.trend_analyzer import TrendAnalyzer
from models.schemas import SkillRecommendation
import logging

logger = logging.getLogger(__name__)

class DynamicCrossSkillState(TypedDict):
    """State for the dynamic cross-skill agent"""
    member_name: str
    role: str
    skills: List[str]
    years_experience: int
    target_role: str
    trends_data: Dict[str, Any]
    adjacent_roles: List[str]
    cross_opportunities: List[str]
    recommendations: List[Dict[str, Any]]
    reasoning: str
    context_sources: List[str]

class DynamicCrossSkillAgent:
    """
    Dynamic cross-skill agent using real-time trends and Groq LLMs
    """
    
    def __init__(self, model_name: str = "llama3-8b-8192"):
        """
        Initialize the dynamic cross-skill agent
        
        Args:
            model_name: Groq model to use
        """
        self.recommender = DynamicSkillRecommender(model_name)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create the state graph
        workflow = StateGraph(DynamicCrossSkillState)
        
        # Add nodes
        workflow.add_node("fetch_cross_trends", self._fetch_cross_skill_trends)
        workflow.add_node("identify_adjacent_roles", self._identify_adjacent_roles)
        workflow.add_node("analyze_cross_opportunities", self._analyze_cross_opportunities)
        workflow.add_node("generate_cross_recommendations", self._generate_cross_recommendations)
        workflow.add_node("validate_cross_recommendations", self._validate_cross_recommendations)
        
        # Define the flow
        workflow.set_entry_point("fetch_cross_trends")
        workflow.add_edge("fetch_cross_trends", "identify_adjacent_roles")
        workflow.add_edge("identify_adjacent_roles", "analyze_cross_opportunities")
        workflow.add_edge("analyze_cross_opportunities", "generate_cross_recommendations")
        workflow.add_edge("generate_cross_recommendations", "validate_cross_recommendations")
        workflow.add_edge("validate_cross_recommendations", END)
        
        return workflow.compile()
    
    async def _fetch_cross_skill_trends(self, state: DynamicCrossSkillState) -> DynamicCrossSkillState:
        """Fetch trends relevant for cross-skilling"""
        try:
            role = state["role"]
            skills = state["skills"]
            
            # Use TrendAnalyzer with async context manager
            async with TrendAnalyzer() as analyzer:
                # Fetch comprehensive trends with focus on cross-functional skills
                trends_data = await analyzer.get_comprehensive_trends(role, skills)
            
            # Filter for cross-skilling relevant trends
            cross_trends = []
            for trend in trends_data.get("trends", []):
                # Look for trends that suggest interdisciplinary skills
                trend_text = f"{trend.get('title', '')} {trend.get('description', '')}".lower()
                cross_keywords = [
                    "cross-functional", "interdisciplinary", "adjacent", "complementary",
                    "versatile", "multi-disciplinary", "hybrid", "full-stack"
                ]
                
                if any(keyword in trend_text for keyword in cross_keywords):
                    cross_trends.append(trend)
            
            # Add cross-skilling specific trends
            trends_data["cross_trends"] = cross_trends
            state["trends_data"] = trends_data
            
            logger.info(f"Fetched {len(cross_trends)} cross-skilling relevant trends")
            
        except Exception as e:
            logger.error(f"Failed to fetch cross-skill trends: {e}")
            state["trends_data"] = {
                "role": role,
                "skills": skills,
                "trends": [],
                "cross_trends": [],
                "sources": {},
                "error": str(e)
            }
        
        return state
    
    def _identify_adjacent_roles(self, state: DynamicCrossSkillState) -> DynamicCrossSkillState:
        """Identify roles adjacent to the current role"""
        try:
            role = state["role"]
            target_role = state.get("target_role")
            
            # If target_role is specified, use it directly
            if target_role:
                adjacent_roles = [target_role]
                logger.info(f"Using specified target role: {target_role}")
            else:
                # Define role adjacency mapping based on current industry trends
                role_adjacency = {
                    "Data Engineer": [
                        "Data Scientist", "Machine Learning Engineer", "DevOps Engineer", 
                        "Software Engineer", "Analytics Engineer", "Platform Engineer"
                    ],
                    "Software Engineer": [
                        "DevOps Engineer", "Data Engineer", "Frontend Developer", 
                        "Backend Developer", "Full Stack Developer", "Site Reliability Engineer"
                    ],
                    "Data Scientist": [
                        "Machine Learning Engineer", "Data Engineer", "Product Manager", 
                        "Software Engineer", "Research Scientist", "Analytics Engineer"
                    ],
                    "DevOps Engineer": [
                        "Software Engineer", "Data Engineer", "Site Reliability Engineer", 
                        "Platform Engineer", "Security Engineer", "Cloud Engineer"
                    ],
                    "Product Manager": [
                        "Data Scientist", "UX/UI Designer", "Business Analyst", 
                        "Software Engineer", "Product Marketing Manager", "Technical Product Manager"
                    ],
                    "UX/UI Designer": [
                        "Frontend Developer", "Product Manager", "Graphic Designer", 
                        "User Researcher", "Product Designer", "Interaction Designer"
                    ],
                    "Frontend Developer": [
                        "Backend Developer", "UX/UI Designer", "Mobile Developer", 
                        "Software Engineer", "Full Stack Developer", "Web Developer"
                    ],
                    "Backend Developer": [
                        "Frontend Developer", "DevOps Engineer", "Data Engineer", 
                        "Software Engineer", "API Developer", "Systems Engineer"
                    ],
                    "Machine Learning Engineer": [
                        "Data Scientist", "Software Engineer", "Data Engineer", 
                        "Research Scientist", "MLOps Engineer", "AI Engineer"
                    ],
                    "QA Engineer": [
                        "Software Engineer", "DevOps Engineer", "Test Automation Engineer", 
                        "Product Manager", "Software Test Engineer", "Quality Assurance Manager"
                    ]
                }
                
                adjacent_roles = role_adjacency.get(role, [
                    "Software Engineer", "Data Scientist", "DevOps Engineer", "Product Manager"
                ])
            
            state["adjacent_roles"] = adjacent_roles
            
            logger.info(f"Identified {len(adjacent_roles)} adjacent roles for {role}")
            
        except Exception as e:
            logger.error(f"Failed to identify adjacent roles: {e}")
            state["adjacent_roles"] = []
        
        return state
    
    def _analyze_cross_opportunities(self, state: DynamicCrossSkillState) -> DynamicCrossSkillState:
        """Analyze cross-skilling opportunities based on trends and adjacent roles"""
        try:
            trends = state["trends_data"].get("trends", [])
            cross_trends = state["trends_data"].get("cross_trends", [])
            adjacent_roles = state["adjacent_roles"]
            current_skills = set(state["skills"])
            
            # Extract cross-skilling opportunities from trends
            cross_opportunities = set()
            
            # From cross-specific trends
            for trend in cross_trends:
                if "skill" in trend:
                    cross_opportunities.add(trend["skill"])
                elif "title" in trend:
                    # Extract skills from trend titles
                    title = trend["title"].lower()
                    skill_keywords = [
                        "product management", "user experience", "devops", "data science",
                        "machine learning", "cloud computing", "security", "automation"
                    ]
                    for keyword in skill_keywords:
                        if keyword in title:
                            cross_opportunities.add(keyword.title())
            
            # From general trends that suggest cross-skilling
            for trend in trends:
                trend_text = f"{trend.get('title', '')} {trend.get('description', '')}".lower()
                
                # Look for emerging interdisciplinary skills
                emerging_skills = [
                    "mlops", "dataops", "devsecops", "platform engineering",
                    "site reliability engineering", "product analytics", "growth engineering"
                ]
                
                for skill in emerging_skills:
                    if skill in trend_text:
                        cross_opportunities.add(skill.title())
            
            # Filter out skills already possessed
            new_cross_opportunities = cross_opportunities - current_skills
            
            state["cross_opportunities"] = list(new_cross_opportunities)
            
            logger.info(f"Identified {len(new_cross_opportunities)} cross-skilling opportunities")
            
        except Exception as e:
            logger.error(f"Failed to analyze cross opportunities: {e}")
            state["cross_opportunities"] = []
        
        return state
    
    def _generate_cross_recommendations(self, state: DynamicCrossSkillState) -> DynamicCrossSkillState:
        """Generate cross-skill recommendations using Groq LLM"""
        try:
            role = state["role"]
            skills = state["skills"]
            trends = state["trends_data"].get("trends", [])
            cross_trends = state["trends_data"].get("cross_trends", [])
            adjacent_roles = state["adjacent_roles"]
            cross_opportunities = state["cross_opportunities"]
            years_experience = state["years_experience"]
            target_role = state.get("target_role")
            
            # Combine all trends for context
            all_trends = trends + cross_trends
            
            # Generate recommendations using the dynamic recommender
            result = self.recommender.get_crossskill_recommendations(
                role=role,
                skills=skills,
                trends=all_trends,
                years_experience=years_experience,
                target_role=target_role
            )
            
            state["recommendations"] = result.get("recommendations", [])
            state["reasoning"] = result.get("reasoning", "Generated cross-skilling recommendations based on current trends")
            
            # Extract context sources
            sources = state["trends_data"].get("sources", {})
            context_sources = []
            for source_type, count in sources.items():
                if count > 0:
                    context_sources.append(f"{source_type}: {count} items")
            
            state["context_sources"] = context_sources
            
            logger.info(f"Generated {len(state['recommendations'])} cross-skill recommendations")
            
        except Exception as e:
            logger.error(f"Failed to generate cross recommendations: {e}")
            state["recommendations"] = []
            state["reasoning"] = f"Failed to generate cross-skill recommendations: {str(e)}"
            state["context_sources"] = []
        
        return state
    
    def _validate_cross_recommendations(self, state: DynamicCrossSkillState) -> DynamicCrossSkillState:
        """Validate and rank cross-skill recommendations"""
        try:
            recommendations = state["recommendations"]
            
            # Filter out invalid recommendations
            valid_recommendations = []
            for rec in recommendations:
                if isinstance(rec, dict) and rec.get("skill_name"):
                    valid_recommendations.append(rec)
            
            # Sort by priority and cross-skill relevance
            priority_order = {"High": 3, "Medium": 2, "Low": 1}
            valid_recommendations.sort(
                key=lambda x: (
                    priority_order.get(x.get("priority", "Low"), 1),
                    x.get("market_demand", "Medium") == "High"
                ), 
                reverse=True
            )
            
            # Limit to top cross-skill recommendations (fewer than upskill)
            if len(valid_recommendations) > 4:
                valid_recommendations = valid_recommendations[:4]
            
            state["recommendations"] = valid_recommendations
            
            logger.info(f"Validated and ranked {len(valid_recommendations)} cross-skill recommendations")
            
        except Exception as e:
            logger.error(f"Failed to validate cross recommendations: {e}")
            state["recommendations"] = []
        
        return state
    
    async def run(self, member_name: str, role: str, skills: List[str], 
                 years_experience: int = None, target_role: str = None) -> Dict[str, Any]:
        """
        Run the dynamic cross-skill agent workflow
        
        Args:
            member_name: Team member's name
            role: Current role
            skills: Current skills
            years_experience: Years of experience
            target_role: Target role for cross-skilling (optional)
            
        Returns:
            Dictionary with recommendations and reasoning
        """
        try:
            # Initialize state
            initial_state = DynamicCrossSkillState(
                member_name=member_name,
                role=role,
                skills=skills,
                years_experience=years_experience or 1,
                target_role=target_role or "",
                trends_data={},
                adjacent_roles=[],
                cross_opportunities=[],
                recommendations=[],
                reasoning="",
                context_sources=[]
            )
            
            # Run the workflow
            result = await self.graph.ainvoke(initial_state)
            
            return {
                "recommendations": result.get("recommendations", []),
                "reasoning": result.get("reasoning", "Generated cross-skill recommendations based on current trends"),
                "context_sources": result.get("context_sources", []),
                "adjacent_roles": result.get("adjacent_roles", []),
                "target_role": target_role
            }
            
        except Exception as e:
            logger.error(f"Failed to run cross-skill agent: {e}")
            return {
                "recommendations": [],
                "reasoning": f"Failed to generate cross-skill recommendations: {str(e)}",
                "context_sources": [],
                "adjacent_roles": [],
                "target_role": target_role
            }
    
    def switch_model(self, model_type: str):
        """Switch to a different Groq model"""
        self.recommender.switch_model(model_type) 