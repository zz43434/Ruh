"""
Embedding Service for generating vector embeddings for verses and user queries.
Uses sentence-transformers for multilingual support including Arabic text.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Tuple
from pathlib import Path


class EmbeddingService:
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize the embedding service with a multilingual model that supports Arabic.
        
        Args:
            model_name: The sentence-transformer model to use. Default is multilingual model.
        """
        self.model_name = model_name
        self.model = None
        self.verse_embeddings = None
        self.verse_metadata = None
        self.embeddings_file = Path("app/data/verse_embeddings.pkl")
        
        # Initialize the model
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            self.model = SentenceTransformer(self.model_name)
            print(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            # Fallback to a smaller model if the default fails
            try:
                self.model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
                print("Loaded fallback embedding model")
            except Exception as e2:
                print(f"Error loading fallback model: {e2}")
                raise e2
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: The text to embed
            
        Returns:
            numpy array representing the text embedding
        """
        if not self.model:
            raise ValueError("Model not loaded")
        
        try:
            embedding = self.model.encode([text])
            return embedding[0]
        except Exception as e:
            print(f"Error generating embedding for text: {e}")
            raise e
    
    def find_similar_verses(self, query: str, top_k: int = 5, min_similarity: float = 0.1) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find verses most similar to the query using Qdrant vector database.
        
        Args:
            query: The user's query text
            top_k: Number of top similar verses to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of tuples (verse_metadata, similarity_score) sorted by similarity
        """
        from app.core.qdrant_client import qdrant
        
        # Generate embedding for the query
        query_embedding = self.generate_embedding(query)
        
        # Use Qdrant client to search for similar vectors
        collection_name = "quran_embeddings"
        
        # Search using Qdrant client
        search_results = qdrant.client.search(
            collection_name=collection_name,
            query_vector=query_embedding.tolist(),
            limit=top_k
        )
        
        results = []
        for result in search_results:
            similarity_score = result.score
            if similarity_score >= min_similarity:
                verse_data = result.payload
                results.append((verse_data, float(similarity_score)))
        
        return results
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current embeddings.
        
        Returns:
            Dictionary with embedding statistics
        """
        if self.verse_embeddings is None:
            return {"status": "No embeddings loaded"}
        
        return {
            "status": "Embeddings loaded",
            "num_verses": len(self.verse_metadata),
            "embedding_dimension": self.verse_embeddings.shape[1],
            "model_name": self.model_name,
            "embeddings_file": str(self.embeddings_file)
        }