from langgraph.graph import StateGraph, END
from typing import Dict, Any, List, TypedDict
from models.schemas import SkillRecommendation
from team_parser.utils import TeamUtils
import logging

logger = logging.getLogger(__name__)

class CrossSkillState(TypedDict):
    """State for the cross-skill agent"""
    member_name: str
    role: str
    skills: List[str]
    years_experience: int
    adjacent_roles: List[str]
    cross_skill_opportunities: List[str]
    industry_trends: List[str]
    recommendations: List[Dict[str, Any]]
    reasoning: str
    context_docs: List[Dict[str, Any]]

class CrossSkillAgent:
    """
    LangGraph-based agent for cross-skilling recommendations
    """
    
    def __init__(self, llm, vectorstore, team_parser):
        """
        Initialize the cross-skill agent
        
        Args:
            llm: Language model instance
            vectorstore: Vector store for document retrieval
            team_parser: Team parser for role-skill mapping
        """
        self.llm = llm
        self.vectorstore = vectorstore
        self.team_parser = team_parser
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create the state graph
        workflow = StateGraph(CrossSkillState)
        
        # Add nodes
        workflow.add_node("identify_adjacent_roles", self._identify_adjacent_roles)
        workflow.add_node("analyze_industry_trends", self._analyze_industry_trends)
        workflow.add_node("find_cross_opportunities", self._find_cross_opportunities)
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("validate_recommendations", self._validate_recommendations)
        
        # Define the flow
        workflow.set_entry_point("identify_adjacent_roles")
        workflow.add_edge("identify_adjacent_roles", "analyze_industry_trends")
        workflow.add_edge("analyze_industry_trends", "find_cross_opportunities")
        workflow.add_edge("find_cross_opportunities", "retrieve_context")
        workflow.add_edge("retrieve_context", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "validate_recommendations")
        workflow.add_edge("validate_recommendations", END)
        
        return workflow.compile()
    
    def _identify_adjacent_roles(self, state: CrossSkillState) -> CrossSkillState:
        """Identify roles adjacent to the current role"""
        try:
            role = state["role"]
            
            # Define role adjacency mapping
            role_adjacency = {
                "Data Engineer": ["Data Scientist", "DevOps Engineer", "Software Engineer", "Machine Learning Engineer"],
                "Software Engineer": ["DevOps Engineer", "Data Engineer", "Frontend Developer", "Backend Developer"],
                "Data Scientist": ["Machine Learning Engineer", "Data Engineer", "Product Manager", "Software Engineer"],
                "DevOps Engineer": ["Software Engineer", "Data Engineer", "Site Reliability Engineer", "Security Engineer"],
                "Product Manager": ["Data Scientist", "UX/UI Designer", "Business Analyst", "Software Engineer"],
                "UX/UI Designer": ["Frontend Developer", "Product Manager", "Graphic Designer", "User Researcher"],
                "Frontend Developer": ["Backend Developer", "UX/UI Designer", "Mobile Developer", "Software Engineer"],
                "Backend Developer": ["Frontend Developer", "DevOps Engineer", "Data Engineer", "Software Engineer"],
                "Machine Learning Engineer": ["Data Scientist", "Software Engineer", "Data Engineer", "Research Scientist"],
                "QA Engineer": ["Software Engineer", "DevOps Engineer", "Test Automation Engineer", "Product Manager"]
            }
            
            adjacent_roles = role_adjacency.get(role, [])
            
            # Add some generic adjacent roles if none found
            if not adjacent_roles:
                adjacent_roles = ["Software Engineer", "Product Manager", "Data Scientist"]
            
            state["adjacent_roles"] = adjacent_roles
            
            logger.debug(f"Identified {len(adjacent_roles)} adjacent roles for {role}")
            
        except Exception as e:
            logger.error(f"Failed to identify adjacent roles: {e}")
            state["adjacent_roles"] = []
        
        return state
    
    def _analyze_industry_trends(self, state: CrossSkillState) -> CrossSkillState:
        """Analyze industry trends for cross-skilling opportunities"""
        try:
            role = state["role"]
            
            # Define emerging trends by role
            role_trends = {
                "Data Engineer": ["MLOps", "Real-time Processing", "Data Governance", "Cloud Data Platforms"],
                "Software Engineer": ["AI/ML Integration", "Cloud Native", "Microservices", "Security"],
                "Data Scientist": ["MLOps", "AutoML", "Explainable AI", "Edge Computing"],
                "DevOps Engineer": ["GitOps", "Platform Engineering", "Security", "Observability"],
                "Product Manager": ["AI/ML Products", "Data-Driven Decision Making", "Platform Strategy", "User Research"],
                "UX/UI Designer": ["AI/ML Design", "Accessibility", "Design Systems", "User Research"],
                "Frontend Developer": ["AI/ML Frontend", "Web3", "Progressive Web Apps", "Performance"],
                "Backend Developer": ["AI/ML APIs", "GraphQL", "Event-Driven Architecture", "Security"],
                "Machine Learning Engineer": ["MLOps", "AutoML", "Edge ML", "ML Security"],
                "QA Engineer": ["Test Automation", "AI/ML Testing", "Performance Testing", "Security Testing"]
            }
            
            # Get trends for the role
            trends = role_trends.get(role, ["AI/ML", "Cloud Computing", "Security", "Automation"])
            
            # Add some universal trends
            universal_trends = ["AI/ML", "Cloud Computing", "Security", "Automation", "Data Literacy"]
            trends.extend([t for t in universal_trends if t not in trends])
            
            state["industry_trends"] = trends[:5]  # Limit to top 5
            
            logger.debug(f"Identified {len(state['industry_trends'])} industry trends")
            
        except Exception as e:
            logger.error(f"Failed to analyze industry trends: {e}")
            state["industry_trends"] = []
        
        return state
    
    def _find_cross_opportunities(self, state: CrossSkillState) -> CrossSkillState:
        """Find specific cross-skilling opportunities"""
        try:
            current_skills = set(state["skills"])
            adjacent_roles = state["adjacent_roles"]
            industry_trends = state["industry_trends"]
            
            # Get skills from adjacent roles
            adjacent_skills = set()
            for role in adjacent_roles:
                role_skills = self.team_parser.get_role_skills(role)
                adjacent_skills.update(role_skills.get("core_skills", []))
                adjacent_skills.update(role_skills.get("advanced_skills", []))
            
            # Find skills that complement current skills
            complementary_skills = []
            for skill in adjacent_skills:
                if skill not in current_skills:
                    # Check if it's complementary to current skills
                    if self._is_complementary_skill(skill, current_skills, state["role"]):
                        complementary_skills.append(skill)
            
            # Add industry trend skills
            trend_skills = []
            for trend in industry_trends:
                if trend not in current_skills and trend not in complementary_skills:
                    trend_skills.append(trend)
            
            # Combine and prioritize
            all_opportunities = complementary_skills + trend_skills
            
            # Limit to top opportunities
            state["cross_skill_opportunities"] = all_opportunities[:8]
            
            logger.debug(f"Found {len(state['cross_skill_opportunities'])} cross-skilling opportunities")
            
        except Exception as e:
            logger.error(f"Failed to find cross opportunities: {e}")
            state["cross_skill_opportunities"] = []
        
        return state
    
    def _is_complementary_skill(self, skill: str, current_skills: set, role: str) -> bool:
        """Check if a skill complements current skills"""
        # Define skill complementarity
        skill_complements = {
            "Python": ["Machine Learning", "Data Analysis", "Automation"],
            "JavaScript": ["Frontend Development", "Node.js", "React"],
            "SQL": ["Data Analysis", "Business Intelligence", "Data Engineering"],
            "Docker": ["DevOps", "Microservices", "Cloud Deployment"],
            "Machine Learning": ["Python", "Data Science", "Statistics"],
            "React": ["JavaScript", "Frontend Development", "UI/UX"],
            "AWS": ["Cloud Computing", "DevOps", "Scalability"],
            "Git": ["Version Control", "Collaboration", "DevOps"]
        }
        
        # Check if skill complements any current skill
        for current_skill in current_skills:
            complements = skill_complements.get(current_skill, [])
            if skill in complements:
                return True
        
        return False
    
    def _retrieve_context(self, state: CrossSkillState) -> CrossSkillState:
        """Retrieve relevant context for cross-skilling"""
        try:
            role = state["role"]
            opportunities = state["cross_skill_opportunities"]
            
            # Search for cross-functional skills
            cross_query = f"cross-functional skills interdisciplinary {role} adjacent roles"
            cross_docs = self.vectorstore.search(cross_query, k=3)
            
            # Search for emerging skills
            trends_query = f"emerging skills technology trends career development"
            trends_docs = self.vectorstore.search(trends_query, k=2)
            
            # Combine documents
            all_docs = cross_docs + trends_docs
            
            # Format for state
            formatted_docs = []
            for doc, score, metadata in all_docs:
                formatted_docs.append({
                    "content": doc,
                    "score": score,
                    "metadata": metadata
                })
            
            state["context_docs"] = formatted_docs
            
            logger.debug(f"Retrieved {len(formatted_docs)} context documents")
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            state["context_docs"] = []
        
        return state
    
    def _generate_recommendations(self, state: CrossSkillState) -> CrossSkillState:
        """Generate cross-skill recommendations using LLM"""
        try:
            from chains.skill_chain import SkillChains
            
            # Create cross-skill chain
            crossskill_chain = SkillChains.create_crossskill_chain(self.llm, self.vectorstore)
            
            # Generate recommendations
            result = crossskill_chain(
                member_name=state["member_name"],
                role=state["role"],
                skills=state["skills"],
                years_experience=state["years_experience"]
            )
            
            recommendations = result.get("recommendations", [])
            
            # Add identified opportunities if not already covered
            opportunities = state["cross_skill_opportunities"]
            for skill in opportunities[:3]:  # Add top 3 opportunities
                if not any(rec.get("skill_name", "").lower() == skill.lower() for rec in recommendations):
                    recommendations.append({
                        "skill_name": skill,
                        "description": f"Cross-functional skill that complements your {state['role']} expertise",
                        "priority": "Medium",
                        "learning_path": TeamUtils.generate_learning_path(skill, state["skills"], state["role"]),
                        "estimated_time": TeamUtils.estimate_learning_time(skill, "medium", state.get("level", "Mid")),
                        "source_documents": ["Cross-functional analysis"]
                    })
            
            state["recommendations"] = recommendations
            
            logger.debug(f"Generated {len(recommendations)} cross-skill recommendations")
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            state["recommendations"] = []
        
        return state
    
    def _validate_recommendations(self, state: CrossSkillState) -> CrossSkillState:
        """Validate and finalize cross-skill recommendations"""
        try:
            recommendations = state["recommendations"]
            
            # Sort by priority and relevance
            priority_order = {"High": 3, "Medium": 2, "Low": 1}
            recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "Low"), 1), reverse=True)
            
            # Limit to top 4 recommendations (cross-skilling should be more focused)
            if len(recommendations) > 4:
                recommendations = recommendations[:4]
            
            # Generate reasoning
            reasoning = self._generate_reasoning(state)
            
            state["recommendations"] = recommendations
            state["reasoning"] = reasoning
            
            logger.debug(f"Validated {len(recommendations)} cross-skill recommendations")
            
        except Exception as e:
            logger.error(f"Failed to validate recommendations: {e}")
            state["recommendations"] = []
            state["reasoning"] = "Failed to generate cross-skill recommendations due to an error."
        
        return state
    
    def _generate_reasoning(self, state: CrossSkillState) -> str:
        """Generate reasoning for cross-skill recommendations"""
        try:
            role = state["role"]
            adjacent_roles = state["adjacent_roles"]
            trends = state["industry_trends"]
            years_experience = state["years_experience"]
            
            reasoning_parts = []
            
            if adjacent_roles:
                reasoning_parts.append(f"Identified {len(adjacent_roles)} adjacent roles that complement your {role} expertise.")
            
            if trends:
                reasoning_parts.append(f"Considered {len(trends)} emerging industry trends for future-proofing your career.")
            
            if years_experience:
                if years_experience >= 5:
                    reasoning_parts.append("Your senior experience makes you well-positioned for cross-functional leadership roles.")
                elif years_experience >= 3:
                    reasoning_parts.append("Your mid-level experience is ideal for expanding into adjacent domains.")
                else:
                    reasoning_parts.append("Early in your career, focus on building a strong foundation before cross-skilling.")
            
            if not reasoning_parts:
                reasoning_parts.append(f"Generated cross-skilling opportunities to expand your {role} capabilities.")
            
            return " ".join(reasoning_parts)
            
        except Exception as e:
            logger.error(f"Failed to generate reasoning: {e}")
            return "Generated cross-skilling recommendations to broaden your professional capabilities."
    
    def run(self, member_name: str, role: str, skills: List[str], 
            years_experience: int = None) -> Dict[str, Any]:
        """
        Run the cross-skill agent workflow
        
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
            initial_state = CrossSkillState(
                member_name=member_name,
                role=role,
                skills=skills,
                years_experience=years_experience or 0,
                adjacent_roles=[],
                cross_skill_opportunities=[],
                industry_trends=[],
                recommendations=[],
                reasoning="",
                context_docs=[]
            )
            
            # Run the workflow
            final_state = self.graph.invoke(initial_state)
            
            # Format recommendations
            formatted_recommendations = []
            for rec in final_state["recommendations"]:
                formatted_recommendations.append(SkillRecommendation(
                    skill_name=rec.get("skill_name", ""),
                    description=rec.get("description", ""),
                    priority=rec.get("priority", "Medium"),
                    learning_path=rec.get("learning_path", []),
                    estimated_time=rec.get("estimated_time", "6-12 weeks"),
                    source_documents=rec.get("source_documents", [])
                ))
            
            return {
                "recommendations": formatted_recommendations,
                "reasoning": final_state["reasoning"],
                "context_sources": [doc.get("metadata", {}).get("source", "Unknown") 
                                  for doc in final_state["context_docs"]],
                "total_recommendations": len(formatted_recommendations)
            }
            
        except Exception as e:
            logger.error(f"Cross-skill agent failed: {e}")
            return {
                "recommendations": [],
                "reasoning": f"Failed to generate cross-skill recommendations: {str(e)}",
                "context_sources": [],
                "total_recommendations": 0
            } 