from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class SkillRecommendationParser(BaseOutputParser):
    """Parser for skill recommendation outputs"""
    
    def parse(self, text: str) -> List[Dict[str, Any]]:
        """Parse the LLM output into structured recommendations"""
        try:
            # Try to extract JSON from the response
            if "```json" in text:
                json_start = text.find("```json") + 7
                json_end = text.find("```", json_start)
                json_str = text[json_start:json_end].strip()
            elif "```" in text:
                json_start = text.find("```") + 3
                json_end = text.find("```", json_start)
                json_str = text[json_start:json_end].strip()
            else:
                json_str = text.strip()
            
            data = json.loads(json_str)
            
            if isinstance(data, dict) and "recommendations" in data:
                return data["recommendations"]
            elif isinstance(data, list):
                return data
            else:
                logger.warning(f"Unexpected JSON structure: {data}")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Raw text: {text}")
            return []
        except Exception as e:
            logger.error(f"Failed to parse recommendations: {e}")
            return []

class SkillChains:
    """Prompt templates and chains for skill recommendations"""
    
    # Upskill recommendation prompt
    UPSKILL_PROMPT = PromptTemplate(
        input_variables=["member_name", "role", "current_skills", "years_experience", "context_docs"],
        template="""
You are an expert career development advisor specializing in technical skill recommendations for {role} professionals.

Team Member: {member_name}
Current Role: {role}
Current Skills: {current_skills}
Years of Experience: {years_experience}

Context from industry sources:
{context_docs}

Based on the team member's current role and skills, provide personalized upskilling recommendations that will help them advance in their current role. Focus on skills that are directly relevant to their role and will enhance their performance.

Consider:
1. Missing core skills for their role
2. Advanced skills that would benefit their career progression
3. Industry trends and emerging technologies in their field
4. Their experience level when suggesting complexity

Provide your response in the following JSON format:
{{
    "reasoning": "Brief explanation of why these skills are recommended",
    "recommendations": [
        {{
            "skill_name": "Skill Name",
            "description": "Brief description of the skill and its importance",
            "priority": "High/Medium/Low",
            "learning_path": ["Step 1", "Step 2", "Step 3"],
            "estimated_time": "X weeks/months",
            "source_documents": ["Document 1", "Document 2"]
        }}
    ]
}}

Focus on practical, actionable recommendations that will have immediate impact on their role performance.
"""
    )
    
    # Cross-skill recommendation prompt
    CROSS_SKILL_PROMPT = PromptTemplate(
        input_variables=["member_name", "role", "current_skills", "years_experience", "context_docs"],
        template="""
You are an expert career development advisor specializing in cross-functional skill development for {role} professionals.

Team Member: {member_name}
Current Role: {role}
Current Skills: {current_skills}
Years of Experience: {years_experience}

Context from industry sources:
{context_docs}

Based on the team member's current role and skills, provide cross-skilling recommendations that will help them expand their capabilities beyond their current role. Focus on skills from adjacent roles or complementary domains that would enhance their versatility and career opportunities.

Consider:
1. Skills from related roles that complement their current expertise
2. Emerging interdisciplinary skills in their industry
3. Skills that would make them more valuable in cross-functional teams
4. Their experience level when suggesting complexity
5. Skills that could lead to new career opportunities

Provide your response in the following JSON format:
{{
    "reasoning": "Brief explanation of why these cross-skilling opportunities are recommended",
    "recommendations": [
        {{
            "skill_name": "Skill Name",
            "description": "Brief description of the skill and how it complements their current role",
            "priority": "High/Medium/Low",
            "learning_path": ["Step 1", "Step 2", "Step 3"],
            "estimated_time": "X weeks/months",
            "source_documents": ["Document 1", "Document 2"]
        }}
    ]
}}

Focus on skills that will broaden their perspective and make them more versatile team members.
"""
    )
    
    # Role analysis prompt
    ROLE_ANALYSIS_PROMPT = PromptTemplate(
        input_variables=["role", "current_skills", "context_docs"],
        template="""
You are an expert in analyzing technical roles and skill requirements.

Role: {role}
Current Skills: {current_skills}

Context from industry sources:
{context_docs}

Analyze this role and provide insights about:
1. Core competencies required for this role
2. Current skill gaps based on the provided skills
3. Industry trends affecting this role
4. Career progression opportunities

Provide your analysis in a clear, structured format that can be used for skill recommendations.
"""
    )
    
    # Skill validation prompt
    SKILL_VALIDATION_PROMPT = PromptTemplate(
        input_variables=["skill_name", "role", "context_docs"],
        template="""
You are validating whether a skill is relevant for a specific role.

Skill: {skill_name}
Role: {role}

Context from industry sources:
{context_docs}

Evaluate whether this skill is:
1. Essential for the role
2. Beneficial but not essential
3. Nice to have
4. Not relevant

Provide your assessment with reasoning in JSON format:
{{
    "relevance": "Essential/Beneficial/Nice to have/Not relevant",
    "reasoning": "Explanation of why this skill is relevant or not for the role",
    "priority": "High/Medium/Low",
    "learning_difficulty": "Easy/Medium/Hard"
}}
"""
    )
    
    @staticmethod
    def format_context_docs(docs: List[Dict[str, Any]]) -> str:
        """Format context documents for prompt inclusion"""
        if not docs:
            return "No additional context available."
        
        formatted_docs = []
        for i, doc in enumerate(docs, 1):
            content = doc.get('content', '')[:500]  # Limit length
            source = doc.get('metadata', {}).get('source', f'Document {i}')
            formatted_docs.append(f"Source {i} ({source}): {content}...")
        
        return "\n\n".join(formatted_docs)
    
    @staticmethod
    def create_upskill_chain(llm, vectorstore):
        """Create upskill recommendation chain"""
        from langchain.chains import LLMChain
        
        def upskill_chain(member_name: str, role: str, skills: List[str], 
                         years_experience: int = None) -> Dict[str, Any]:
            """Generate upskill recommendations"""
            try:
                # Get relevant context
                context_query = f"{role} role skills and career development"
                context_docs = vectorstore.search(context_query, k=3)
                context_text = SkillChains.format_context_docs(context_docs)
                
                # Create chain
                chain = LLMChain(
                    llm=llm,
                    prompt=SkillChains.UPSKILL_PROMPT,
                    output_parser=SkillRecommendationParser()
                )
                
                # Run chain
                result = chain.run({
                    "member_name": member_name,
                    "role": role,
                    "current_skills": ", ".join(skills),
                    "years_experience": years_experience or "Not specified",
                    "context_docs": context_text
                })
                
                return {
                    "recommendations": result,
                    "context_sources": [doc.get('metadata', {}).get('source', 'Unknown') for doc in context_docs]
                }
                
            except Exception as e:
                logger.error(f"Upskill chain failed: {e}")
                return {"recommendations": [], "context_sources": []}
        
        return upskill_chain
    
    @staticmethod
    def create_crossskill_chain(llm, vectorstore):
        """Create cross-skill recommendation chain"""
        from langchain.chains import LLMChain
        
        def crossskill_chain(member_name: str, role: str, skills: List[str], 
                           years_experience: int = None) -> Dict[str, Any]:
            """Generate cross-skill recommendations"""
            try:
                # Get relevant context
                context_query = f"cross-functional skills for {role} professionals"
                context_docs = vectorstore.search(context_query, k=3)
                context_text = SkillChains.format_context_docs(context_docs)
                
                # Create chain
                chain = LLMChain(
                    llm=llm,
                    prompt=SkillChains.CROSS_SKILL_PROMPT,
                    output_parser=SkillRecommendationParser()
                )
                
                # Run chain
                result = chain.run({
                    "member_name": member_name,
                    "role": role,
                    "current_skills": ", ".join(skills),
                    "years_experience": years_experience or "Not specified",
                    "context_docs": context_text
                })
                
                return {
                    "recommendations": result,
                    "context_sources": [doc.get('metadata', {}).get('source', 'Unknown') for doc in context_docs]
                }
                
            except Exception as e:
                logger.error(f"Cross-skill chain failed: {e}")
                return {"recommendations": [], "context_sources": []}
        
        return crossskill_chain 