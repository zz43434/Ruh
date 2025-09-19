"""
Embedding Service for generating vector embeddings for verses and user queries.
Uses sentence-transformers for multilingual support including Arabic text.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple
import pickle
import os
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
    
    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            numpy array of shape (n_texts, embedding_dim)
        """
        if not self.model:
            raise ValueError("Model not loaded")
        
        try:
            embeddings = self.model.encode(texts, show_progress_bar=True)
            return embeddings
        except Exception as e:
            print(f"Error generating batch embeddings: {e}")
            raise e
    
    def create_verse_embeddings(self, verses: List[Dict[str, Any]]) -> None:
        """
        Create embeddings for all verses and save them to disk.
        
        Args:
            verses: List of verse dictionaries containing text and metadata
        """
        print(f"Creating embeddings for {len(verses)} verses...")
        
        # Prepare texts for embedding - combine Arabic text with translation for better semantic understanding
        texts = []
        metadata = []
        
        for verse in verses:
            # Combine Arabic text with English translation for richer semantic representation
            arabic_text = verse.get('arabic_text', '')
            translation = verse.get('translation', '')
            surah_name = verse.get('surah_name', '')
            
            # Create a combined text for embedding
            combined_text = f"{arabic_text} {translation} {surah_name}".strip()
            texts.append(combined_text)
            
            # Store metadata for retrieval
            metadata.append({
                'verse_number': verse.get('verse_number'),
                'arabic_text': arabic_text,
                'translation': translation,
                'surah_name': surah_name,
                'surah_number': verse.get('surah_number'),
                'context': verse.get('context', ''),
                'revelation_place': verse.get('revelation_place', ''),
                'ayah_count': verse.get('ayah_count', 0)
            })
        
        # Generate embeddings
        embeddings = self.generate_embeddings_batch(texts)
        
        # Store embeddings and metadata
        self.verse_embeddings = embeddings
        self.verse_metadata = metadata
        
        # Save to disk
        self._save_embeddings()
        print(f"Successfully created and saved embeddings for {len(verses)} verses")

    
    def _save_embeddings(self):
        """Save embeddings and metadata to disk."""
        try:
            # Ensure directory exists
            self.embeddings_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'embeddings': self.verse_embeddings,
                'metadata': self.verse_metadata,
                'model_name': self.model_name
            }
            
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(data, f)
            print(f"Saved embeddings to {self.embeddings_file}")
        except Exception as e:
            print(f"Error saving embeddings: {e}")
            raise e
    
    def find_similar_verses(self, query: str, top_k: int = 5, min_similarity: float = 0.1) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find verses most similar to the query using cosine similarity.
        
        Args:
            query: The user's query text
            top_k: Number of top similar verses to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of tuples (verse_metadata, similarity_score) sorted by similarity
        """
        
        # Generate embedding for the query
        query_embedding = self.generate_embedding(query)
        
        # Calculate cosine similarities
        similarities = cosine_similarity([query_embedding], self.verse_embeddings)[0]
        
        # Get top-k most similar verses
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            similarity_score = similarities[idx]
            if similarity_score >= min_similarity:
                verse_data = self.verse_metadata[idx].copy()
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