from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import Dict, Any, List, TypedDict, Annotated
from models.schemas import SkillRecommendation
from team_parser.utils import TeamUtils
import logging

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State for the upskill agent"""
    member_name: str
    role: str
    skills: List[str]
    years_experience: int
    role_skills: Dict[str, List[str]]
    missing_core_skills: List[str]
    advanced_skills: List[str]
    recommendations: List[Dict[str, Any]]
    reasoning: str
    context_docs: List[Dict[str, Any]]

class UpskillAgent:
    """
    LangGraph-based agent for role-focused upskilling recommendations
    """
    
    def __init__(self, llm, vectorstore, team_parser):
        """
        Initialize the upskill agent
        
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
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_role", self._analyze_role)
        workflow.add_node("identify_gaps", self._identify_skill_gaps)
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("validate_recommendations", self._validate_recommendations)
        
        # Define the flow
        workflow.set_entry_point("analyze_role")
        workflow.add_edge("analyze_role", "identify_gaps")
        workflow.add_edge("identify_gaps", "retrieve_context")
        workflow.add_edge("retrieve_context", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "validate_recommendations")
        workflow.add_edge("validate_recommendations", END)
        
        return workflow.compile()
    
    def _analyze_role(self, state: AgentState) -> AgentState:
        """Analyze the team member's role and get role-specific skills"""
        try:
            role = state["role"]
            
            # Get role skills from the parser
            role_skills = self.team_parser.get_role_skills(role)
            
            # Update state
            state["role_skills"] = role_skills
            
            logger.debug(f"Analyzed role {role} with {len(role_skills.get('core_skills', []))} core skills")
            
        except Exception as e:
            logger.error(f"Failed to analyze role: {e}")
            state["role_skills"] = {"core_skills": [], "advanced_skills": [], "cross_skills": []}
        
        return state
    
    def _identify_skill_gaps(self, state: AgentState) -> AgentState:
        """Identify missing core skills and potential advanced skills"""
        try:
            current_skills = set(state["skills"])
            role_skills = state["role_skills"]
            years_experience = state["years_experience"]
            
            # Find missing core skills
            core_skills = set(role_skills.get("core_skills", []))
            missing_core = list(core_skills - current_skills)
            
            # Identify advanced skills based on experience
            advanced_skills = set(role_skills.get("advanced_skills", []))
            available_advanced = list(advanced_skills - current_skills)
            
            # Filter advanced skills based on experience level
            if years_experience and years_experience >= 3:
                recommended_advanced = available_advanced
            else:
                recommended_advanced = available_advanced[:2]  # Limit for junior/mid level
            
            state["missing_core_skills"] = missing_core
            state["advanced_skills"] = recommended_advanced
            
            logger.debug(f"Identified {len(missing_core)} missing core skills and {len(recommended_advanced)} advanced skills")
            
        except Exception as e:
            logger.error(f"Failed to identify skill gaps: {e}")
            state["missing_core_skills"] = []
            state["advanced_skills"] = []
        
        return state
    
    def _retrieve_context(self, state: AgentState) -> AgentState:
        """Retrieve relevant context documents"""
        try:
            role = state["role"]
            skills = state["skills"]
            
            # Search for role-specific documents
            role_query = f"{role} role skills career development requirements"
            role_docs = self.vectorstore.search(role_query, k=3)
            
            # Search for skill-specific documents
            skills_query = f"skills: {', '.join(skills)}"
            skills_docs = self.vectorstore.search(skills_query, k=2)
            
            # Combine documents
            all_docs = role_docs + skills_docs
            
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
    
    def _generate_recommendations(self, state: AgentState) -> AgentState:
        """Generate upskill recommendations using LLM"""
        try:
            from chains.skill_chain import SkillChains
            
            # Create upskill chain
            upskill_chain = SkillChains.create_upskill_chain(self.llm, self.vectorstore)
            
            # Generate recommendations
            result = upskill_chain(
                member_name=state["member_name"],
                role=state["role"],
                skills=state["skills"],
                years_experience=state["years_experience"]
            )
            
            recommendations = result.get("recommendations", [])
            
            # Add missing core skills as high priority if not already covered
            missing_core = state["missing_core_skills"]
            for skill in missing_core:
                if not any(rec.get("skill_name", "").lower() == skill.lower() for rec in recommendations):
                    recommendations.append({
                        "skill_name": skill,
                        "description": f"Core skill required for {state['role']} role",
                        "priority": "High",
                        "learning_path": TeamUtils.generate_learning_path(skill, state["skills"], state["role"]),
                        "estimated_time": TeamUtils.estimate_learning_time(skill, "basic", state.get("level", "Mid")),
                        "source_documents": ["Role requirements"]
                    })
            
            state["recommendations"] = recommendations
            
            logger.debug(f"Generated {len(recommendations)} upskill recommendations")
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            state["recommendations"] = []
        
        return state
    
    def _validate_recommendations(self, state: AgentState) -> AgentState:
        """Validate and finalize recommendations"""
        try:
            recommendations = state["recommendations"]
            
            # Sort by priority
            priority_order = {"High": 3, "Medium": 2, "Low": 1}
            recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "Low"), 1), reverse=True)
            
            # Limit to top 5 recommendations
            if len(recommendations) > 5:
                recommendations = recommendations[:5]
            
            # Generate reasoning
            reasoning = self._generate_reasoning(state)
            
            state["recommendations"] = recommendations
            state["reasoning"] = reasoning
            
            logger.debug(f"Validated {len(recommendations)} recommendations")
            
        except Exception as e:
            logger.error(f"Failed to validate recommendations: {e}")
            state["recommendations"] = []
            state["reasoning"] = "Failed to generate recommendations due to an error."
        
        return state
    
    def _generate_reasoning(self, state: AgentState) -> str:
        """Generate reasoning for the recommendations"""
        try:
            role = state["role"]
            missing_core = state["missing_core_skills"]
            advanced_skills = state["advanced_skills"]
            years_experience = state["years_experience"]
            
            reasoning_parts = []
            
            if missing_core:
                reasoning_parts.append(f"Identified {len(missing_core)} missing core skills for the {role} role.")
            
            if advanced_skills:
                reasoning_parts.append(f"Recommended {len(advanced_skills)} advanced skills for career progression.")
            
            if years_experience:
                if years_experience >= 5:
                    reasoning_parts.append("Given your senior experience level, focus on advanced skills and leadership capabilities.")
                elif years_experience >= 3:
                    reasoning_parts.append("With your mid-level experience, balance core skill development with advanced topics.")
                else:
                    reasoning_parts.append("As a junior professional, prioritize building strong foundational skills.")
            
            if not reasoning_parts:
                reasoning_parts.append(f"Generated personalized recommendations for {role} role advancement.")
            
            return " ".join(reasoning_parts)
            
        except Exception as e:
            logger.error(f"Failed to generate reasoning: {e}")
            return "Generated personalized skill recommendations based on your role and current skills."
    
    def run(self, member_name: str, role: str, skills: List[str], 
            years_experience: int = None) -> Dict[str, Any]:
        """
        Run the upskill agent workflow
        
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
            initial_state = AgentState(
                member_name=member_name,
                role=role,
                skills=skills,
                years_experience=years_experience or 0,
                role_skills={},
                missing_core_skills=[],
                advanced_skills=[],
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
                    estimated_time=rec.get("estimated_time", "4-8 weeks"),
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
            logger.error(f"Upskill agent failed: {e}")
            return {
                "recommendations": [],
                "reasoning": f"Failed to generate recommendations: {str(e)}",
                "context_sources": [],
                "total_recommendations": 0
            } 