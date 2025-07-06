import os
import groq
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class GroqLLM:
    """
    Groq LLM client for open-source models (plain Python class)
    """
    def __init__(self, model_name: str = "llama3-8b-8192", temperature: float = 0.7, max_tokens: int = 2048, top_p: float = 1.0, frequency_penalty: float = 0.0, presence_penalty: float = 0.0):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        self._client = groq.Groq(api_key=api_key)
        logger.debug(f"Groq client initialized. Attributes: {dir(self._client)}")

    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        logger.debug(f"Type of self._client: {type(self._client)}, value: {self._client}")
        try:
            # Try chat.completions.create, fallback to completions.create if AttributeError
            try:
                response = self._client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    top_p=self.top_p,
                    frequency_penalty=self.frequency_penalty,
                    presence_penalty=self.presence_penalty,
                    stop=stop,
                    **kwargs
                )
            except AttributeError:
                logger.warning("self._client.chat not found, trying self._client.completions.create...")
                response = self._client.completions.create(
                    model=self.model_name,
                    prompt=prompt,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    top_p=self.top_p,
                    frequency_penalty=self.frequency_penalty,
                    presence_penalty=self.presence_penalty,
                    stop=stop,
                    **kwargs
                )
            text = None
            if hasattr(response, 'choices') and response.choices:
                if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                    text = response.choices[0].message.content
                elif hasattr(response.choices[0], 'text'):
                    text = response.choices[0].text
            if text is None:
                raise ValueError("Could not extract text from Groq response")
            return text
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            raise

class DynamicSkillRecommender:
    """
    Dynamic skill recommendation system using Groq LLMs
    """
    
    def __init__(self, model_name: str = "llama3-8b-8192"):
        """
        Initialize the dynamic skill recommender
        
        Args:
            model_name: Groq model to use (llama3-8b-8192, llama3-70b-8192, mixtral-8x7b-32768, etc.)
        """
        self.llm = GroqLLM(
            model_name=model_name,
            temperature=0.7,
            max_tokens=2048
        )
        
        # Available Groq models for different use cases
        self.available_models = {
            "fast": "llama3-8b-8192",      # Fast, good for real-time
            "balanced": "mixtral-8x7b-32768",  # Balanced performance
            "powerful": "llama3-70b-8192"   # Most powerful, slower
        }
    
    def get_upskill_recommendations(self, role: str, skills: List[str], 
                                  trends: List[Dict[str, Any]], 
                                  years_experience: int = None) -> Dict[str, Any]:
        """
        Generate dynamic upskill recommendations based on current trends
        """
        try:
            # Create context from trends
            trend_context = self._format_trends_for_prompt(trends)
            years_exp = years_experience if years_experience is not None else 1
            prompt = f"""
You are an expert career development advisor specializing in technical skill recommendations for {role} professionals.

Team Member Profile:
- Role: {role}
- Current Skills: {', '.join(skills)}
- Years of Experience: {years_exp}

Current Industry Trends and Insights:
{trend_context}

Based on the team member's current role, skills, and the latest industry trends, provide personalized upskilling recommendations that will help them advance in their current role. Focus on skills that are directly relevant to their role and will enhance their performance.

Consider:
1. Missing core skills for their role based on current industry standards
2. Advanced skills that would benefit their career progression
3. Emerging technologies and trends in their field
4. Their experience level when suggesting complexity
5. Market demand and job opportunities

Provide your response in the following JSON format:
{{
    "reasoning": "Brief explanation of why these skills are recommended based on current trends",
    "recommendations": [
        {{
            "skill_name": "Skill Name",
            "description": "Brief description of the skill and its importance",
            "priority": "High/Medium/Low",
            "learning_path": ["Step 1", "Step 2", "Step 3"],
            "estimated_time": "X weeks/months",
            "market_demand": "High/Medium/Low",
            "trend_relevance": "Why this skill is trending",
            "source_evidence": ["Trend 1", "Trend 2"]
        }}
    ]
}}

Focus on practical, actionable recommendations that reflect current industry needs and trends.
"""
            response = self.llm._call(prompt)
            return self._parse_recommendations(response)
        except Exception as e:
            logger.error(f"Failed to generate upskill recommendations: {e}")
            return {
                "reasoning": "Unable to generate recommendations due to an error",
                "recommendations": []
            }
    
    def get_crossskill_recommendations(self, role: str, skills: List[str], 
                                     trends: List[Dict[str, Any]], 
                                     years_experience: int = None,
                                     target_role: str = None) -> Dict[str, Any]:
        """
        Generate dynamic cross-skill recommendations based on current trends
        """
        try:
            # Create context from trends
            trend_context = self._format_trends_for_prompt(trends)
            years_exp = years_experience if years_experience is not None else 1
            
            # Build target role context
            target_context = ""
            if target_role:
                target_context = f"\nTarget Role: {target_role}\nFocus on skills that would help transition from {role} to {target_role} role."
            
            prompt = f"""
You are an expert career development advisor specializing in cross-functional skill development for {role} professionals.

Team Member Profile:
- Role: {role}
- Current Skills: {', '.join(skills)}
- Years of Experience: {years_exp}{target_context}

Current Industry Trends and Insights:
{trend_context}

Based on the team member's current role, skills, and the latest industry trends, provide cross-skilling recommendations that will help them expand their capabilities beyond their current role. Focus on skills from adjacent roles or complementary domains that would enhance their versatility and career opportunities.

Consider:
1. Skills from related roles that complement their current expertise
2. Emerging interdisciplinary skills in their industry
3. Skills that would make them more valuable in cross-functional teams
4. Their experience level when suggesting complexity
5. Skills that could lead to new career opportunities
6. Current market trends and emerging technologies
{f"7. Specific skills needed to transition to {target_role} role" if target_role else ""}

Provide your response in the following JSON format:
{{
    "reasoning": "Brief explanation of why these cross-skilling opportunities are recommended based on current trends",
    "recommendations": [
        {{
            "skill_name": "Skill Name",
            "description": "Brief description of the skill and how it complements their current role",
            "priority": "High/Medium/Low",
            "learning_path": ["Step 1", "Step 2", "Step 3"],
            "estimated_time": "X weeks/months",
            "market_demand": "High/Medium/Low",
            "trend_relevance": "Why this cross-skill is valuable",
            "source_evidence": ["Trend 1", "Trend 2"]
        }}
    ]
}}

Focus on skills that will broaden their perspective and make them more versatile team members based on current industry needs.
"""
            response = self.llm._call(prompt)
            return self._parse_recommendations(response)
        except Exception as e:
            logger.error(f"Failed to generate cross-skill recommendations: {e}")
            return {
                "reasoning": "Unable to generate recommendations due to an error",
                "recommendations": []
            }
    
    def _format_trends_for_prompt(self, trends: List[Dict[str, Any]]) -> str:
        """
        Format trends data for inclusion in LLM prompts
        """
        if not trends:
            return "No current trends data available."
        
        formatted_trends = []
        for i, trend in enumerate(trends[:10], 1):  # Limit to top 10 trends
            trend_type = trend.get("type", "trend")
            title = trend.get("title", trend.get("name", trend.get("skill", "")))
            description = trend.get("description", trend.get("summary", ""))
            source = trend.get("source", "Unknown")
            
            formatted_trends.append(f"{i}. {trend_type.upper()}: {title}")
            if description:
                formatted_trends.append(f"   Description: {description[:200]}...")
            formatted_trends.append(f"   Source: {source}")
            formatted_trends.append("")
        
        return "\n".join(formatted_trends)
    
    def _parse_recommendations(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured recommendations
        """
        try:
            # Try to extract JSON from the response
            import json
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                if isinstance(data, dict) and "recommendations" in data:
                    return data
                elif isinstance(data, list):
                    return {
                        "reasoning": "Generated recommendations based on current trends",
                        "recommendations": data
                    }
            
            # If JSON parsing fails, return a structured response
            return {
                "reasoning": "Generated recommendations based on current industry trends",
                "recommendations": [
                    {
                        "skill_name": "Skill Analysis Required",
                        "description": "Please review the LLM response for detailed recommendations",
                        "priority": "Medium",
                        "learning_path": ["Review current trends", "Identify skill gaps", "Create learning plan"],
                        "estimated_time": "4-8 weeks",
                        "market_demand": "Medium",
                        "trend_relevance": "Based on current industry analysis",
                        "source_evidence": ["Industry trends", "Market analysis"]
                    }
                ],
                "raw_response": response
            }
            
        except Exception as e:
            logger.error(f"Failed to parse recommendations: {e}")
            return {
                "reasoning": "Generated recommendations based on current trends",
                "recommendations": [],
                "error": str(e),
                "raw_response": response
            }
    
    def switch_model(self, model_type: str):
        """
        Switch to a different Groq model
        
        Args:
            model_type: "fast", "balanced", or "powerful"
        """
        if model_type in self.available_models:
            model_name = self.available_models[model_type]
            self.llm = GroqLLM(
                model_name=model_name,
                temperature=0.7,
                max_tokens=2048
            )
            logger.info(f"Switched to {model_name} model")
        else:
            raise ValueError(f"Invalid model type. Available: {list(self.available_models.keys())}") 