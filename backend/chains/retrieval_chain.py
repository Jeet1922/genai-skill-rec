from typing import List, Dict, Any, Tuple
from vectorizer.vectorstore import SkillVectorStore
import logging

logger = logging.getLogger(__name__)

class RetrievalChain:
    """
    RAG (Retrieval-Augmented Generation) chain for skill recommendations
    """
    
    def __init__(self, vectorstore: SkillVectorStore):
        """
        Initialize the retrieval chain
        
        Args:
            vectorstore: SkillVectorStore instance
        """
        self.vectorstore = vectorstore
    
    def retrieve_role_context(self, role: str, skills: List[str], k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for role-based recommendations
        
        Args:
            role: Job role
            skills: Current skills
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            # Search for role-specific documents
            role_query = f"{role} role requirements skills career development"
            role_docs = self.vectorstore.search(role_query, k=k//2)
            
            # Search for skill-specific documents
            skills_query = f"skills: {', '.join(skills)}"
            skills_docs = self.vectorstore.search(skills_query, k=k//2)
            
            # Combine and deduplicate
            all_docs = role_docs + skills_docs
            unique_docs = self._deduplicate_documents(all_docs)
            
            # Sort by relevance score
            unique_docs.sort(key=lambda x: x[1], reverse=True)
            
            # Format for chain consumption
            formatted_docs = []
            for doc, score, metadata in unique_docs[:k]:
                formatted_docs.append({
                    "content": doc,
                    "score": score,
                    "metadata": metadata
                })
            
            logger.debug(f"Retrieved {len(formatted_docs)} documents for role {role}")
            return formatted_docs
            
        except Exception as e:
            logger.error(f"Failed to retrieve role context: {e}")
            return []
    
    def retrieve_crossskill_context(self, role: str, skills: List[str], k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for cross-skilling recommendations
        
        Args:
            role: Current job role
            skills: Current skills
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            # Search for cross-functional skills
            cross_query = f"cross-functional skills interdisciplinary {role} adjacent roles"
            cross_docs = self.vectorstore.search(cross_query, k=k//2)
            
            # Search for emerging skills and trends
            trends_query = f"emerging skills technology trends career development"
            trends_docs = self.vectorstore.search(trends_query, k=k//2)
            
            # Combine and deduplicate
            all_docs = cross_docs + trends_docs
            unique_docs = self._deduplicate_documents(all_docs)
            
            # Sort by relevance score
            unique_docs.sort(key=lambda x: x[1], reverse=True)
            
            # Format for chain consumption
            formatted_docs = []
            for doc, score, metadata in unique_docs[:k]:
                formatted_docs.append({
                    "content": doc,
                    "score": score,
                    "metadata": metadata
                })
            
            logger.debug(f"Retrieved {len(formatted_docs)} documents for cross-skilling")
            return formatted_docs
            
        except Exception as e:
            logger.error(f"Failed to retrieve cross-skill context: {e}")
            return []
    
    def retrieve_skill_specific_context(self, skill_name: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve context for a specific skill
        
        Args:
            skill_name: Name of the skill
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            # Search for skill-specific information
            skill_query = f"{skill_name} learning resources tutorials best practices"
            skill_docs = self.vectorstore.search(skill_query, k=k)
            
            # Format for chain consumption
            formatted_docs = []
            for doc, score, metadata in skill_docs:
                formatted_docs.append({
                    "content": doc,
                    "score": score,
                    "metadata": metadata
                })
            
            logger.debug(f"Retrieved {len(formatted_docs)} documents for skill {skill_name}")
            return formatted_docs
            
        except Exception as e:
            logger.error(f"Failed to retrieve skill context: {e}")
            return []
    
    def retrieve_industry_trends(self, role: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve industry trends relevant to a role
        
        Args:
            role: Job role
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            # Search for industry trends
            trends_query = f"industry trends {role} technology evolution market changes"
            trends_docs = self.vectorstore.search(trends_query, k=k)
            
            # Format for chain consumption
            formatted_docs = []
            for doc, score, metadata in trends_docs:
                formatted_docs.append({
                    "content": doc,
                    "score": score,
                    "metadata": metadata
                })
            
            logger.debug(f"Retrieved {len(formatted_docs)} industry trend documents")
            return formatted_docs
            
        except Exception as e:
            logger.error(f"Failed to retrieve industry trends: {e}")
            return []
    
    def _deduplicate_documents(self, docs: List[Tuple[str, float, Dict[str, Any]]]) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Remove duplicate documents based on content similarity
        
        Args:
            docs: List of (document, score, metadata) tuples
            
        Returns:
            Deduplicated list
        """
        unique_docs = []
        seen_contents = set()
        
        for doc, score, metadata in docs:
            # Create a simple hash of the content for deduplication
            content_hash = hash(doc[:100])  # Use first 100 chars as hash
            
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                unique_docs.append((doc, score, metadata))
        
        return unique_docs
    
    def format_context_for_prompt(self, docs: List[Dict[str, Any]], max_length: int = 2000) -> str:
        """
        Format retrieved documents for inclusion in prompts
        
        Args:
            docs: List of document dictionaries
            max_length: Maximum total length of formatted context
            
        Returns:
            Formatted context string
        """
        if not docs:
            return "No relevant context available."
        
        formatted_parts = []
        current_length = 0
        
        for i, doc in enumerate(docs, 1):
            content = doc.get('content', '')
            source = doc.get('metadata', {}).get('source', f'Document {i}')
            score = doc.get('score', 0.0)
            
            # Truncate content if needed
            if len(content) > 300:
                content = content[:300] + "..."
            
            part = f"Source {i} ({source}, relevance: {score:.2f}): {content}"
            
            # Check if adding this part would exceed max length
            if current_length + len(part) > max_length:
                break
            
            formatted_parts.append(part)
            current_length += len(part)
        
        return "\n\n".join(formatted_parts)
    
    def get_recommendation_context(self, recommendation_type: str, role: str, 
                                 skills: List[str], years_experience: int = None) -> Dict[str, Any]:
        """
        Get comprehensive context for skill recommendations
        
        Args:
            recommendation_type: "upskill" or "cross_skill"
            role: Job role
            skills: Current skills
            years_experience: Years of experience
            
        Returns:
            Dictionary with formatted context and metadata
        """
        try:
            if recommendation_type == "upskill":
                role_docs = self.retrieve_role_context(role, skills, k=4)
                trends_docs = self.retrieve_industry_trends(role, k=2)
                all_docs = role_docs + trends_docs
            else:  # cross_skill
                cross_docs = self.retrieve_crossskill_context(role, skills, k=4)
                trends_docs = self.retrieve_industry_trends(role, k=2)
                all_docs = cross_docs + trends_docs
            
            # Format context
            context_text = self.format_context_for_prompt(all_docs)
            
            # Extract source information
            sources = []
            for doc in all_docs:
                source = doc.get('metadata', {}).get('source', 'Unknown')
                if source not in sources:
                    sources.append(source)
            
            return {
                "context": context_text,
                "sources": sources,
                "document_count": len(all_docs),
                "recommendation_type": recommendation_type
            }
            
        except Exception as e:
            logger.error(f"Failed to get recommendation context: {e}")
            return {
                "context": "No relevant context available.",
                "sources": [],
                "document_count": 0,
                "recommendation_type": recommendation_type
            } 