import re
from typing import List, Dict, Any, Set
import logging

logger = logging.getLogger(__name__)

class TeamUtils:
    """
    Utility functions for team data processing and skill analysis
    """
    
    @staticmethod
    def normalize_skill_name(skill: str) -> str:
        """
        Normalize skill names for consistent matching
        
        Args:
            skill: Raw skill name
            
        Returns:
            Normalized skill name
        """
        # Convert to lowercase and remove extra spaces
        normalized = re.sub(r'\s+', ' ', skill.lower().strip())
        
        # Common skill name mappings
        skill_mappings = {
            'javascript': 'JavaScript',
            'js': 'JavaScript',
            'python': 'Python',
            'java': 'Java',
            'sql': 'SQL',
            'html': 'HTML',
            'css': 'CSS',
            'react': 'React',
            'vue': 'Vue.js',
            'angular': 'Angular',
            'node.js': 'Node.js',
            'nodejs': 'Node.js',
            'docker': 'Docker',
            'kubernetes': 'Kubernetes',
            'k8s': 'Kubernetes',
            'aws': 'AWS',
            'amazon web services': 'AWS',
            'azure': 'Azure',
            'gcp': 'Google Cloud',
            'google cloud': 'Google Cloud',
            'machine learning': 'Machine Learning',
            'ml': 'Machine Learning',
            'deep learning': 'Deep Learning',
            'ai': 'Artificial Intelligence',
            'artificial intelligence': 'Artificial Intelligence',
            'data science': 'Data Science',
            'devops': 'DevOps',
            'ci/cd': 'CI/CD',
            'continuous integration': 'CI/CD',
            'agile': 'Agile',
            'scrum': 'Scrum',
            'kanban': 'Kanban'
        }
        
        return skill_mappings.get(normalized, skill.title())
    
    @staticmethod
    def calculate_skill_overlap(skills1: List[str], skills2: List[str]) -> float:
        """
        Calculate overlap between two skill sets
        
        Args:
            skills1: First set of skills
            skills2: Second set of skills
            
        Returns:
            Overlap percentage (0.0 to 1.0)
        """
        if not skills1 or not skills2:
            return 0.0
        
        set1 = set(skills1)
        set2 = set(skills2)
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union) if union else 0.0
    
    @staticmethod
    def find_missing_core_skills(member_skills: List[str], role_core_skills: List[str]) -> List[str]:
        """
        Find core skills that a team member is missing
        
        Args:
            member_skills: Team member's current skills
            role_core_skills: Core skills for their role
            
        Returns:
            List of missing core skills
        """
        member_skill_set = set(member_skills)
        core_skill_set = set(role_core_skills)
        
        return list(core_skill_set - member_skill_set)
    
    @staticmethod
    def suggest_skill_priorities(member_skills: List[str], role_skills: Dict[str, List[str]], 
                               years_experience: int = None) -> Dict[str, List[str]]:
        """
        Suggest skill priorities based on role and experience
        
        Args:
            member_skills: Current skills
            role_skills: Role skill mapping
            years_experience: Years of experience
            
        Returns:
            Dictionary with high, medium, low priority skills
        """
        member_skill_set = set(member_skills)
        core_skills = set(role_skills.get("core_skills", []))
        advanced_skills = set(role_skills.get("advanced_skills", []))
        cross_skills = set(role_skills.get("cross_skills", []))
        
        # Missing core skills are high priority
        high_priority = list(core_skills - member_skill_set)
        
        # Advanced skills based on experience
        if years_experience and years_experience >= 3:
            medium_priority = list(advanced_skills - member_skill_set)
        else:
            medium_priority = []
        
        # Cross-skilling opportunities
        low_priority = list(cross_skills - member_skill_set)
        
        return {
            "high": high_priority,
            "medium": medium_priority,
            "low": low_priority
        }
    
    @staticmethod
    def analyze_team_skill_distribution(team_members: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze skill distribution across the team
        
        Args:
            team_members: List of team member data
            
        Returns:
            Analysis results
        """
        all_skills = set()
        skill_counts = {}
        role_skill_mapping = {}
        
        for member in team_members:
            skills = member.get('skills', [])
            role = member.get('role', 'Unknown')
            
            # Track all skills
            all_skills.update(skills)
            
            # Count skill occurrences
            for skill in skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
            
            # Map roles to skills
            if role not in role_skill_mapping:
                role_skill_mapping[role] = set()
            role_skill_mapping[role].update(skills)
        
        # Find skills with low coverage (only 1 person has them)
        low_coverage_skills = [skill for skill, count in skill_counts.items() if count == 1]
        
        # Find skills with high coverage (most people have them)
        high_coverage_skills = [skill for skill, count in skill_counts.items() if count > len(team_members) * 0.7]
        
        return {
            "total_unique_skills": len(all_skills),
            "skill_counts": skill_counts,
            "role_skill_mapping": {role: list(skills) for role, skills in role_skill_mapping.items()},
            "low_coverage_skills": low_coverage_skills,
            "high_coverage_skills": high_coverage_skills,
            "team_size": len(team_members)
        }
    
    @staticmethod
    def generate_learning_path(skill: str, current_skills: List[str], 
                             role: str = None) -> List[str]:
        """
        Generate a learning path for a specific skill
        
        Args:
            skill: Target skill to learn
            current_skills: Current skills
            role: Team member's role
            
        Returns:
            List of learning steps
        """
        # Basic learning path template
        learning_paths = {
            "Python": [
                "Learn Python basics and syntax",
                "Practice with data structures and algorithms",
                "Learn popular libraries (pandas, numpy, matplotlib)",
                "Build small projects",
                "Learn testing and debugging",
                "Explore advanced topics (async, decorators)"
            ],
            "Machine Learning": [
                "Strengthen Python and statistics fundamentals",
                "Learn scikit-learn for basic ML",
                "Study data preprocessing and feature engineering",
                "Learn model evaluation and validation",
                "Explore deep learning with TensorFlow/PyTorch",
                "Practice with real-world datasets"
            ],
            "DevOps": [
                "Learn Linux fundamentals and shell scripting",
                "Master version control with Git",
                "Learn containerization with Docker",
                "Study CI/CD pipelines",
                "Learn cloud platforms (AWS/Azure/GCP)",
                "Explore monitoring and logging tools"
            ],
            "Data Engineering": [
                "Strengthen SQL and database fundamentals",
                "Learn ETL processes and data warehousing",
                "Master Apache Airflow for workflow orchestration",
                "Learn big data technologies (Spark, Hadoop)",
                "Study data modeling and architecture",
                "Explore cloud data platforms"
            ]
        }
        
        # Return specific path if available, otherwise generic
        if skill in learning_paths:
            return learning_paths[skill]
        else:
            return [
                f"Research {skill} fundamentals",
                f"Find online courses or tutorials for {skill}",
                f"Practice {skill} with hands-on projects",
                f"Build a portfolio project using {skill}",
                f"Seek mentorship or join {skill} communities",
                f"Apply {skill} in real-world scenarios"
            ]
    
    @staticmethod
    def estimate_learning_time(skill: str, complexity: str = "medium", 
                             current_level: str = "Mid") -> str:
        """
        Estimate learning time for a skill
        
        Args:
            skill: Skill to learn
            complexity: Skill complexity (basic, medium, advanced)
            current_level: Current experience level
            
        Returns:
            Estimated time string
        """
        # Base times in weeks
        base_times = {
            "basic": {"Junior": 4, "Mid": 2, "Senior": 1},
            "medium": {"Junior": 8, "Mid": 4, "Senior": 2},
            "advanced": {"Junior": 16, "Mid": 8, "Senior": 4}
        }
        
        weeks = base_times.get(complexity, {}).get(current_level, 4)
        
        if weeks == 1:
            return "1 week"
        elif weeks < 4:
            return f"{weeks} weeks"
        else:
            months = weeks // 4
            remaining_weeks = weeks % 4
            if remaining_weeks == 0:
                return f"{months} months"
            else:
                return f"{months} months, {remaining_weeks} weeks" 