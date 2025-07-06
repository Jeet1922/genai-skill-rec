import pandas as pd
import json
import csv
from typing import List, Dict, Any, Optional
from models.schemas import TeamMember
import logging

logger = logging.getLogger(__name__)

class TeamParser:
    """
    Parser for team data files (CSV/JSON) with normalization and role-skill mapping
    """
    
    def __init__(self, role_skills_path: str = "data/static_role_skills.json"):
        """
        Initialize the parser with role-skill mapping
        
        Args:
            role_skills_path: Path to role-skill mapping JSON file
        """
        self.role_skills = self._load_role_skills(role_skills_path)
    
    def _load_role_skills(self, path: str) -> Dict[str, Any]:
        """Load role-skill mapping from JSON file"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Role skills file not found: {path}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load role skills: {e}")
            return {}
    
    def parse_csv(self, file_path: str) -> List[TeamMember]:
        """
        Parse team data from CSV file
        
        Expected columns: name, role, level, skills, years_experience (optional)
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of TeamMember objects
        """
        try:
            df = pd.read_csv(file_path)
            return self._parse_dataframe(df)
        except Exception as e:
            logger.error(f"Failed to parse CSV file: {e}")
            raise
    
    def parse_json(self, file_path: str) -> List[TeamMember]:
        """
        Parse team data from JSON file
        
        Expected format: list of objects with name, role, level, skills, years_experience
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            List of TeamMember objects
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                return [self._create_team_member(item) for item in data]
            else:
                raise ValueError("JSON file should contain a list of team members")
                
        except Exception as e:
            logger.error(f"Failed to parse JSON file: {e}")
            raise
    
    def parse_data(self, data: List[Dict[str, Any]]) -> List[TeamMember]:
        """
        Parse team data from list of dictionaries
        
        Args:
            data: List of dictionaries with team member data
            
        Returns:
            List of TeamMember objects
        """
        try:
            return [self._create_team_member(item) for item in data]
        except Exception as e:
            logger.error(f"Failed to parse data: {e}")
            raise
    
    def _parse_dataframe(self, df: pd.DataFrame) -> List[TeamMember]:
        """Parse pandas DataFrame into TeamMember objects"""
        team_members = []
        
        for _, row in df.iterrows():
            try:
                member = self._create_team_member(row.to_dict())
                team_members.append(member)
            except Exception as e:
                logger.warning(f"Failed to parse row {row.get('name', 'Unknown')}: {e}")
                continue
        
        return team_members
    
    def _create_team_member(self, data: Dict[str, Any]) -> TeamMember:
        """Create TeamMember object from dictionary data"""
        # Normalize and validate data
        name = self._normalize_string(data.get('name', ''))
        role = self._normalize_string(data.get('role', ''))
        level = self._normalize_level(data.get('level', ''))
        skills = self._normalize_skills(data.get('skills', []))
        years_experience = self._normalize_years(data.get('years_experience'))
        
        # Validate required fields
        if not name:
            raise ValueError("Name is required")
        if not role:
            raise ValueError("Role is required")
        if not skills:
            raise ValueError("At least one skill is required")
        
        return TeamMember(
            name=name,
            role=role,
            level=level,
            skills=skills,
            years_experience=years_experience
        )
    
    def _normalize_string(self, value: Any) -> str:
        """Normalize string values"""
        if value is None:
            return ""
        return str(value).strip()
    
    def _normalize_level(self, level: str) -> str:
        """Normalize experience level"""
        level = self._normalize_string(level).lower()
        
        level_mapping = {
            'junior': 'Junior',
            'mid': 'Mid',
            'mid-level': 'Mid',
            'senior': 'Senior',
            'lead': 'Lead',
            'principal': 'Lead',
            'staff': 'Lead'
        }
        
        return level_mapping.get(level, 'Mid')
    
    def _normalize_skills(self, skills: Any) -> List[str]:
        """Normalize skills list"""
        if isinstance(skills, str):
            # Handle comma-separated string
            skills = [skill.strip() for skill in skills.split(',') if skill.strip()]
        elif isinstance(skills, list):
            skills = [str(skill).strip() for skill in skills if skill]
        else:
            skills = []
        
        # Remove duplicates and sort
        return sorted(list(set(skills)))
    
    def _normalize_years(self, years: Any) -> Optional[int]:
        """Normalize years of experience"""
        if years is None:
            return None
        
        try:
            years_int = int(float(years))
            return max(0, years_int)  # Ensure non-negative
        except (ValueError, TypeError):
            return None
    
    def get_role_skills(self, role: str) -> Dict[str, List[str]]:
        """
        Get skill mapping for a specific role
        
        Args:
            role: Job role
            
        Returns:
            Dictionary with core_skills, advanced_skills, cross_skills
        """
        return self.role_skills.get(role, {
            "core_skills": [],
            "advanced_skills": [],
            "cross_skills": []
        })
    
    def get_available_roles(self) -> List[str]:
        """Get list of available roles in the mapping"""
        return list(self.role_skills.keys())
    
    def validate_team_data(self, team_members: List[TeamMember]) -> Dict[str, Any]:
        """
        Validate team data and provide insights
        
        Args:
            team_members: List of team members
            
        Returns:
            Validation results and insights
        """
        if not team_members:
            return {"valid": False, "errors": ["No team members provided"]}
        
        errors = []
        warnings = []
        insights = {
            "total_members": len(team_members),
            "roles": {},
            "levels": {},
            "skill_coverage": {}
        }
        
        for member in team_members:
            # Check role mapping
            if member.role not in self.role_skills:
                warnings.append(f"Role '{member.role}' not found in skill mapping")
            
            # Count roles and levels
            insights["roles"][member.role] = insights["roles"].get(member.role, 0) + 1
            insights["levels"][member.level] = insights["levels"].get(member.level, 0) + 1
            
            # Check skill coverage
            role_skills = self.get_role_skills(member.role)
            core_skills = set(role_skills.get("core_skills", []))
            member_skills = set(member.skills)
            
            missing_core = core_skills - member_skills
            if missing_core:
                warnings.append(f"{member.name} missing core skills: {', '.join(missing_core)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "insights": insights
        } 