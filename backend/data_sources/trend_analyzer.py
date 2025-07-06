import asyncio
import aiohttp
import requests
import feedparser
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import json
import re
from asyncio_throttle import Throttler

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """
    Fetches real-time industry trends and skill data from multiple sources
    """
    
    def __init__(self):
        self.throttler = Throttler(rate_limit=10, period=1)  # 10 requests per second
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_github_trends(self, language: str = None, timeframe: str = "weekly") -> List[Dict[str, Any]]:
        """
        Fetch trending repositories from GitHub
        """
        try:
            async with self.throttler:
                url = "https://github.com/trending"
                if language:
                    url += f"/{language}"
                url += f"?since={timeframe}"
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        trends = []
                        repo_articles = soup.find_all('article', class_='Box-row')
                        
                        for article in repo_articles[:10]:  # Top 10
                            try:
                                repo_link = article.find('h2', class_='h3 lh-condensed')
                                if repo_link:
                                    repo_name = repo_link.get_text().strip().replace('\n', '').replace(' ', '')
                                    description_elem = article.find('p')
                                    description = description_elem.get_text().strip() if description_elem else ""
                                    
                                    # Extract language
                                    language_elem = article.find('span', {'itemprop': 'programmingLanguage'})
                                    lang = language_elem.get_text().strip() if language_elem else "Unknown"
                                    
                                    trends.append({
                                        "name": repo_name,
                                        "description": description,
                                        "language": lang,
                                        "source": "GitHub",
                                        "type": "repository"
                                    })
                            except Exception as e:
                                logger.warning(f"Failed to parse GitHub trend: {e}")
                                continue
                        
                        return trends
                    else:
                        logger.error(f"GitHub trends request failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Failed to fetch GitHub trends: {e}")
            return []
    
    async def get_tech_blog_posts(self, role: str) -> List[Dict[str, Any]]:
        """
        Fetch relevant tech blog posts for a specific role
        """
        try:
            # Define role-specific blog sources
            blog_sources = {
                "Data Engineer": [
                    "https://engineering.linkedin.com/blog/topic/data-engineering",
                    "https://netflixtechblog.com/tagged/data-engineering",
                    "https://medium.com/tag/data-engineering"
                ],
                "Data Architect": [
                    "https://engineering.linkedin.com/blog/topic/data-engineering",
                    "https://netflixtechblog.com/tagged/data-engineering",
                    "https://medium.com/tag/data-architecture"
                ],
                "Software Engineer": [
                    "https://engineering.fb.com/",
                    "https://netflixtechblog.com/",
                    "https://medium.com/tag/software-engineering"
                ],
                "Frontend Developer": [
                    "https://engineering.fb.com/",
                    "https://netflixtechblog.com/",
                    "https://medium.com/tag/frontend-development"
                ],
                "Data Scientist": [
                    "https://netflixtechblog.com/tagged/data-science",
                    "https://medium.com/tag/data-science",
                    "https://towardsdatascience.com/"
                ],
                "DevOps Engineer": [
                    "https://netflixtechblog.com/tagged/devops",
                    "https://medium.com/tag/devops",
                    "https://www.hashicorp.com/blog"
                ]
            }
            
            sources = blog_sources.get(role, blog_sources["Software Engineer"])
            all_posts = []
            
            for source in sources[:2]:  # Limit to 2 sources per role
                try:
                    async with self.throttler:
                        async with self.session.get(source) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                # Extract blog posts (this is a simplified version)
                                articles = soup.find_all(['article', 'div'], class_=re.compile(r'article|post|entry'))
                                
                                for article in articles[:5]:
                                    try:
                                        title_elem = article.find(['h1', 'h2', 'h3'])
                                        title = title_elem.get_text().strip() if title_elem else ""
                                        
                                        if title and len(title) > 10:
                                            all_posts.append({
                                                "title": title,
                                                "source": source,
                                                "type": "blog_post",
                                                "role": role
                                            })
                                    except Exception as e:
                                        continue
                                        
                except Exception as e:
                    logger.warning(f"Failed to fetch from {source}: {e}")
                    continue
            
            return all_posts
            
        except Exception as e:
            logger.error(f"Failed to fetch tech blog posts: {e}")
            return []
    
    async def get_learning_platform_trends(self) -> List[Dict[str, Any]]:
        """
        Fetch trending courses and skills from learning platforms
        """
        try:
            # Simulate fetching from learning platforms
            # In a real implementation, you'd use their APIs
            trends = [
                {
                    "skill": "Machine Learning",
                    "platform": "Coursera",
                    "trend": "increasing",
                    "courses_count": 150,
                    "type": "learning_trend"
                },
                {
                    "skill": "DevOps",
                    "platform": "Udemy",
                    "trend": "increasing",
                    "courses_count": 89,
                    "type": "learning_trend"
                },
                {
                    "skill": "Data Engineering",
                    "platform": "edX",
                    "trend": "increasing",
                    "courses_count": 45,
                    "type": "learning_trend"
                },
                {
                    "skill": "Cloud Computing",
                    "platform": "Coursera",
                    "trend": "increasing",
                    "courses_count": 120,
                    "type": "learning_trend"
                }
            ]
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to fetch learning platform trends: {e}")
            return []
    
    async def get_job_market_trends(self, role: str) -> List[Dict[str, Any]]:
        """
        Fetch job market trends for a specific role
        """
        try:
            # This would integrate with job APIs like Indeed, LinkedIn, etc.
            # For now, we'll return simulated data
            market_trends = {
                "Data Engineer": [
                    {"skill": "Apache Airflow", "demand": "high", "growth": "+25%"},
                    {"skill": "Snowflake", "demand": "high", "growth": "+30%"},
                    {"skill": "dbt", "demand": "medium", "growth": "+40%"},
                    {"skill": "Kubernetes", "demand": "medium", "growth": "+15%"}
                ],
                "Data Architect": [
                    {"skill": "Data Modeling", "demand": "high", "growth": "+20%"},
                    {"skill": "Snowflake", "demand": "high", "growth": "+30%"},
                    {"skill": "Data Governance", "demand": "high", "growth": "+35%"},
                    {"skill": "ETL Design", "demand": "medium", "growth": "+25%"}
                ],
                "Software Engineer": [
                    {"skill": "React", "demand": "high", "growth": "+20%"},
                    {"skill": "Python", "demand": "high", "growth": "+25%"},
                    {"skill": "TypeScript", "demand": "high", "growth": "+35%"},
                    {"skill": "Docker", "demand": "medium", "growth": "+18%"}
                ],
                "Frontend Developer": [
                    {"skill": "React", "demand": "high", "growth": "+25%"},
                    {"skill": "TypeScript", "demand": "high", "growth": "+40%"},
                    {"skill": "Next.js", "demand": "high", "growth": "+50%"},
                    {"skill": "Tailwind CSS", "demand": "medium", "growth": "+30%"}
                ],
                "Data Scientist": [
                    {"skill": "Machine Learning", "demand": "high", "growth": "+30%"},
                    {"skill": "Deep Learning", "demand": "high", "growth": "+40%"},
                    {"skill": "MLOps", "demand": "medium", "growth": "+50%"},
                    {"skill": "A/B Testing", "demand": "medium", "growth": "+20%"}
                ],
                "DevOps Engineer": [
                    {"skill": "Kubernetes", "demand": "high", "growth": "+35%"},
                    {"skill": "Terraform", "demand": "high", "growth": "+45%"},
                    {"skill": "AWS", "demand": "high", "growth": "+25%"},
                    {"skill": "GitOps", "demand": "medium", "growth": "+60%"}
                ]
            }
            
            return market_trends.get(role, market_trends["Software Engineer"])
            
        except Exception as e:
            logger.error(f"Failed to fetch job market trends: {e}")
            return []
    
    async def get_ai_trends(self) -> List[Dict[str, Any]]:
        """
        Fetch AI and ML trends from various sources
        """
        try:
            # Fetch from AI-focused RSS feeds and blogs
            ai_sources = [
                "https://feeds.feedburner.com/oreilly/ai",
                "https://distill.pub/rss.xml",
                # "https://blog.openai.com/rss/"
            ]
            
            all_trends = []
            
            for source in ai_sources:
                try:
                    async with self.throttler:
                        async with self.session.get(source) as response:
                            if response.status == 200:
                                content = await response.text()
                                feed = feedparser.parse(content)
                                
                                for entry in feed.entries[:5]:
                                    all_trends.append({
                                        "title": entry.title,
                                        "summary": entry.summary if hasattr(entry, 'summary') else "",
                                        "source": source,
                                        "type": "ai_trend",
                                        "published": entry.published if hasattr(entry, 'published') else ""
                                    })
                                    
                except Exception as e:
                    logger.warning(f"Failed to fetch from {source}: {e}")
                    continue
            
            return all_trends
            
        except Exception as e:
            logger.error(f"Failed to fetch AI trends: {e}")
            return []
    
    async def get_comprehensive_trends(self, role: str, skills: List[str]) -> Dict[str, Any]:
        """
        Fetch comprehensive trends for a specific role and skills
        """
        try:
            # Fetch all trend data concurrently
            tasks = [
                self.get_github_trends(),
                self.get_tech_blog_posts(role),
                self.get_learning_platform_trends(),
                self.get_job_market_trends(role),
                self.get_ai_trends()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            github_trends, blog_posts, learning_trends, job_trends, ai_trends = results
            
            # Filter and rank trends based on relevance
            relevant_trends = self._filter_relevant_trends(
                role, skills, github_trends, blog_posts, learning_trends, job_trends, ai_trends
            )
            
            # Add fallback trends if we have very few or no trends
            if len(relevant_trends) < 3:
                fallback_trends = self._get_fallback_trends(role, skills)
                relevant_trends.extend(fallback_trends)
            
            return {
                "role": role,
                "skills": skills,
                "timestamp": datetime.now().isoformat(),
                "trends": relevant_trends,
                "sources": {
                    "github": len(github_trends) if isinstance(github_trends, list) else 0,
                    "blogs": len(blog_posts) if isinstance(blog_posts, list) else 0,
                    "learning": len(learning_trends) if isinstance(learning_trends, list) else 0,
                    "job_market": len(job_trends) if isinstance(job_trends, list) else 0,
                    "ai": len(ai_trends) if isinstance(ai_trends, list) else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive trends: {e}")
            # Return fallback trends even if everything fails
            fallback_trends = self._get_fallback_trends(role, skills)
            return {
                "role": role,
                "skills": skills,
                "timestamp": datetime.now().isoformat(),
                "trends": fallback_trends,
                "sources": {"fallback": len(fallback_trends)},
                "error": str(e)
            }
    
    def _filter_relevant_trends(self, role: str, skills: List[str], *trend_lists) -> List[Dict[str, Any]]:
        """
        Filter and rank trends based on relevance to role and skills
        """
        relevant_trends = []
        
        for trend_list in trend_lists:
            if not isinstance(trend_list, list):
                continue
                
            for trend in trend_list:
                relevance_score = self._calculate_relevance(trend, role, skills)
                if relevance_score > 0.3:  # Minimum relevance threshold
                    trend["relevance_score"] = relevance_score
                    relevant_trends.append(trend)
        
        # Sort by relevance score
        relevant_trends.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return relevant_trends[:20]  # Return top 20 most relevant trends
    
    def _calculate_relevance(self, trend: Dict[str, Any], role: str, skills: List[str]) -> float:
        """
        Calculate relevance score for a trend based on role and skills
        """
        score = 0.0
        
        # Check role relevance
        if "role" in trend and trend["role"] == role:
            score += 0.4
        
        # Check skill relevance
        trend_text = f"{trend.get('title', '')} {trend.get('description', '')} {trend.get('skill', '')}".lower()
        for skill in skills:
            if skill.lower() in trend_text:
                score += 0.3
        
        # Check for emerging technologies
        emerging_keywords = ["ai", "ml", "machine learning", "deep learning", "cloud", "kubernetes", "docker", "microservices"]
        for keyword in emerging_keywords:
            if keyword in trend_text:
                score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _get_fallback_trends(self, role: str, skills: List[str]) -> List[Dict[str, Any]]:
        """
        Generate fallback trends when external sources fail
        """
        role_trends = {
            "Data Engineer": [
                {"title": "Data Engineering Best Practices", "description": "Modern data engineering practices and tools", "type": "fallback"},
                {"title": "Apache Airflow Adoption", "description": "Growing adoption of workflow orchestration tools", "type": "fallback"},
                {"title": "Cloud Data Platforms", "description": "Migration to cloud-based data platforms", "type": "fallback"}
            ],
            "Data Architect": [
                {"title": "Data Architecture Patterns", "description": "Modern data architecture design patterns", "type": "fallback"},
                {"title": "Data Governance", "description": "Importance of data governance in modern organizations", "type": "fallback"},
                {"title": "Data Mesh Architecture", "description": "Emerging data mesh architectural patterns", "type": "fallback"}
            ],
            "Software Engineer": [
                {"title": "Modern Software Development", "description": "Current trends in software development", "type": "fallback"},
                {"title": "Microservices Architecture", "description": "Microservices and distributed systems", "type": "fallback"},
                {"title": "Cloud-Native Development", "description": "Cloud-native application development", "type": "fallback"}
            ],
            "Frontend Developer": [
                {"title": "Modern Frontend Frameworks", "description": "Latest frontend development frameworks", "type": "fallback"},
                {"title": "Web Performance", "description": "Web performance optimization techniques", "type": "fallback"},
                {"title": "Progressive Web Apps", "description": "PWA development and adoption", "type": "fallback"}
            ],
            "Data Scientist": [
                {"title": "Machine Learning Trends", "description": "Current trends in machine learning", "type": "fallback"},
                {"title": "MLOps Practices", "description": "Machine learning operations and deployment", "type": "fallback"},
                {"title": "AI Ethics and Governance", "description": "Ethical considerations in AI development", "type": "fallback"}
            ],
            "DevOps Engineer": [
                {"title": "DevOps Best Practices", "description": "Modern DevOps practices and tools", "type": "fallback"},
                {"title": "Container Orchestration", "description": "Kubernetes and container management", "type": "fallback"},
                {"title": "Infrastructure as Code", "description": "IaC practices and tools", "type": "fallback"}
            ]
        }
        
        return role_trends.get(role, role_trends["Software Engineer"]) 