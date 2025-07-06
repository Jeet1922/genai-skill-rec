import numpy as np
import os
import pickle
from typing import List, Dict, Any, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from .embedder import SkillEmbedder
import logging

logger = logging.getLogger(__name__)

class SkillVectorStore:
    """
    Simple in-memory vector store for skill-related document retrieval using scikit-learn
    """
    
    def __init__(self, embedder: SkillEmbedder, persist_directory: str = "data/vectorstore"):
        """
        Initialize the vector store
        
        Args:
            embedder: SkillEmbedder instance
            persist_directory: Directory to persist vector store data
        """
        self.embedder = embedder
        self.persist_directory = persist_directory
        self.embeddings = []
        self.documents = []
        self.metadata = []
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Try to load existing data
        self._load_data()
        
        logger.info(f"Initialized vector store at {persist_directory}")
    
    def _load_data(self):
        """Load existing embeddings and documents if available"""
        try:
            embeddings_path = os.path.join(self.persist_directory, "embeddings.pkl")
            docs_path = os.path.join(self.persist_directory, "documents.pkl")
            meta_path = os.path.join(self.persist_directory, "metadata.pkl")
            
            if os.path.exists(embeddings_path):
                with open(embeddings_path, "rb") as f:
                    self.embeddings = pickle.load(f)
                
                with open(docs_path, "rb") as f:
                    self.documents = pickle.load(f)
                
                with open(meta_path, "rb") as f:
                    self.metadata = pickle.load(f)
                
                logger.info(f"Loaded existing data with {len(self.documents)} documents")
            else:
                logger.info("No existing data found, will create new store")
        except Exception as e:
            logger.warning(f"Failed to load existing data: {e}")
    
    def _save_data(self):
        """Save embeddings and documents"""
        try:
            embeddings_path = os.path.join(self.persist_directory, "embeddings.pkl")
            docs_path = os.path.join(self.persist_directory, "documents.pkl")
            meta_path = os.path.join(self.persist_directory, "metadata.pkl")
            
            with open(embeddings_path, "wb") as f:
                pickle.dump(self.embeddings, f)
            
            with open(docs_path, "wb") as f:
                pickle.dump(self.documents, f)
            
            with open(meta_path, "wb") as f:
                pickle.dump(self.metadata, f)
            
            logger.info(f"Saved data with {len(self.documents)} documents")
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
    
    def add_documents(self, documents: List[str], metadata: Optional[List[Dict[str, Any]]] = None):
        """
        Add documents to the vector store
        
        Args:
            documents: List of document texts
            metadata: List of metadata dictionaries for each document
        """
        if not documents:
            return
        
        try:
            # Generate embeddings
            embeddings = self.embedder.embed_text(documents)
            
            # Prepare metadata
            if metadata is None:
                metadata = [{"source": f"doc_{i}"} for i in range(len(documents))]
            
            # Add to store
            self.embeddings.extend(embeddings.tolist())
            self.documents.extend(documents)
            self.metadata.extend(metadata)
            
            logger.info(f"Added {len(documents)} documents to vector store")
            
            # Save data
            self._save_data()
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def search(self, query: str, k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of tuples: (document_text, similarity_score, metadata)
        """
        try:
            if not self.embeddings:
                return []
            
            # Generate query embedding
            query_embedding = self.embedder.embed_text(query)
            
            # Calculate similarities
            similarities = cosine_similarity([query_embedding], self.embeddings)[0]
            
            # Get top k results
            top_indices = np.argsort(similarities)[::-1][:k]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only include positive similarities
                    results.append((
                        self.documents[idx],
                        float(similarities[idx]),
                        self.metadata[idx] if idx < len(self.metadata) else {}
                    ))
            
            logger.debug(f"Search returned {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def search_skills(self, skills: List[str], k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for documents related to specific skills
        
        Args:
            skills: List of skills to search for
            k: Number of results to return
            
        Returns:
            List of tuples: (document_text, similarity_score, metadata)
        """
        query = f"skills: {', '.join(skills)}"
        return self.search(query, k)
    
    def search_role_skills(self, role: str, skills: List[str], k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for documents related to role and skills combination
        
        Args:
            role: Job role
            skills: List of skills
            k: Number of results to return
            
        Returns:
            List of tuples: (document_text, similarity_score, metadata)
        """
        query = f"{role} role with skills: {', '.join(skills)}"
        return self.search(query, k)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics
        
        Returns:
            Dictionary with stats
        """
        return {
            "total_documents": len(self.documents),
            "embedding_dimension": self.embedder.get_embedding_dimension()
        }
    
    def clear(self):
        """Clear all documents from the vector store"""
        self.embeddings = []
        self.documents = []
        self.metadata = []
        
        # Remove saved files
        for filename in ["embeddings.pkl", "documents.pkl", "metadata.pkl"]:
            try:
                os.remove(os.path.join(self.persist_directory, filename))
            except FileNotFoundError:
                pass
        
        logger.info("Cleared vector store") 