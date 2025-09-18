"""
Vector Store for managing verse embeddings with persistence and efficient retrieval.
Provides a simple in-memory vector database with disk persistence.
"""

import numpy as np
import pickle
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import threading
import time


class VectorStore:
    def __init__(self, storage_dir: str = "app/data/vector_store"):
        """
        Initialize the vector store.
        
        Args:
            storage_dir: Directory to store vector data
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Storage files
        self.vectors_file = self.storage_dir / "vectors.npy"
        self.metadata_file = self.storage_dir / "metadata.json"
        self.index_file = self.storage_dir / "index.json"
        
        # In-memory storage
        self.vectors = None
        self.metadata = []
        self.index = {}
        self.dimension = None
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Load existing data
        self.load()
    
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]], ids: Optional[List[str]] = None) -> List[str]:
        """
        Add vectors to the store.
        
        Args:
            vectors: Array of shape (n_vectors, dimension)
            metadata: List of metadata dictionaries for each vector
            ids: Optional list of IDs for the vectors
            
        Returns:
            List of assigned IDs
        """
        with self._lock:
            if len(vectors) != len(metadata):
                raise ValueError("Number of vectors must match number of metadata entries")
            
            # Initialize storage if empty
            if self.vectors is None:
                self.vectors = vectors.copy()
                self.dimension = vectors.shape[1]
            else:
                if vectors.shape[1] != self.dimension:
                    raise ValueError(f"Vector dimension {vectors.shape[1]} doesn't match store dimension {self.dimension}")
                self.vectors = np.vstack([self.vectors, vectors])
            
            # Generate IDs if not provided
            if ids is None:
                start_idx = len(self.metadata)
                ids = [f"verse_{start_idx + i}" for i in range(len(vectors))]
            
            # Add metadata and update index
            assigned_ids = []
            for i, (meta, vector_id) in enumerate(zip(metadata, ids)):
                # Add timestamp
                meta_with_timestamp = meta.copy()
                meta_with_timestamp['added_at'] = datetime.now().isoformat()
                meta_with_timestamp['id'] = vector_id
                
                self.metadata.append(meta_with_timestamp)
                self.index[vector_id] = len(self.metadata) - 1
                assigned_ids.append(vector_id)
            
            return assigned_ids
    
    def search(self, query_vector: np.ndarray, top_k: int = 5, min_similarity: float = 0.0, 
               filter_metadata: Optional[Dict[str, Any]] = None) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query vector of shape (dimension,)
            top_k: Number of top results to return
            min_similarity: Minimum cosine similarity threshold
            filter_metadata: Optional metadata filters
            
        Returns:
            List of tuples (id, metadata, similarity_score)
        """
        with self._lock:
            if self.vectors is None or len(self.vectors) == 0:
                return []
            
            # Calculate cosine similarities
            query_norm = np.linalg.norm(query_vector)
            if query_norm == 0:
                return []
            
            vector_norms = np.linalg.norm(self.vectors, axis=1)
            valid_indices = vector_norms > 0
            
            if not np.any(valid_indices):
                return []
            
            # Compute cosine similarity only for valid vectors
            similarities = np.zeros(len(self.vectors))
            valid_vectors = self.vectors[valid_indices]
            valid_norms = vector_norms[valid_indices]
            
            dot_products = np.dot(valid_vectors, query_vector)
            similarities[valid_indices] = dot_products / (valid_norms * query_norm)
            
            # Apply metadata filters
            valid_indices_list = []
            for i, meta in enumerate(self.metadata):
                if similarities[i] >= min_similarity:
                    if filter_metadata is None or self._matches_filter(meta, filter_metadata):
                        valid_indices_list.append(i)
            
            if not valid_indices_list:
                return []
            
            # Sort by similarity and get top-k
            valid_similarities = [(i, similarities[i]) for i in valid_indices_list]
            valid_similarities.sort(key=lambda x: x[1], reverse=True)
            
            results = []
            for i, similarity in valid_similarities[:top_k]:
                vector_id = self.metadata[i]['id']
                results.append((vector_id, self.metadata[i], float(similarity)))
            
            return results
    
    def get_by_id(self, vector_id: str) -> Optional[Tuple[np.ndarray, Dict[str, Any]]]:
        """
        Get vector and metadata by ID.
        
        Args:
            vector_id: The vector ID
            
        Returns:
            Tuple of (vector, metadata) or None if not found
        """
        with self._lock:
            if vector_id not in self.index:
                return None
            
            idx = self.index[vector_id]
            return self.vectors[idx], self.metadata[idx]
    
    def delete(self, vector_id: str) -> bool:
        """
        Delete a vector by ID.
        
        Args:
            vector_id: The vector ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if vector_id not in self.index:
                return False
            
            idx = self.index[vector_id]
            
            # Remove from vectors array
            self.vectors = np.delete(self.vectors, idx, axis=0)
            
            # Remove metadata
            del self.metadata[idx]
            
            # Rebuild index (indices shift after deletion)
            self.index = {}
            for i, meta in enumerate(self.metadata):
                self.index[meta['id']] = i
            
            return True
    
    def update_metadata(self, vector_id: str, new_metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for a vector.
        
        Args:
            vector_id: The vector ID
            new_metadata: New metadata dictionary
            
        Returns:
            True if updated, False if not found
        """
        with self._lock:
            if vector_id not in self.index:
                return False
            
            idx = self.index[vector_id]
            # Preserve ID and timestamp
            new_metadata['id'] = vector_id
            new_metadata['updated_at'] = datetime.now().isoformat()
            if 'added_at' in self.metadata[idx]:
                new_metadata['added_at'] = self.metadata[idx]['added_at']
            
            self.metadata[idx] = new_metadata
            return True
    
    def save(self) -> bool:
        """
        Save the vector store to disk.
        
        Returns:
            True if saved successfully
        """
        try:
            with self._lock:
                # Save vectors
                if self.vectors is not None:
                    np.save(self.vectors_file, self.vectors)
                
                # Save metadata
                with open(self.metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(self.metadata, f, ensure_ascii=False, indent=2)
                
                # Save index
                with open(self.index_file, 'w') as f:
                    json.dump(self.index, f, indent=2)
                
                return True
        except Exception as e:
            print(f"Error saving vector store: {e}")
            return False
    
    def load(self) -> bool:
        """
        Load the vector store from disk.
        
        Returns:
            True if loaded successfully
        """
        try:
            with self._lock:
                # Load vectors
                if self.vectors_file.exists():
                    self.vectors = np.load(self.vectors_file)
                    self.dimension = self.vectors.shape[1] if len(self.vectors) > 0 else None
                
                # Load metadata
                if self.metadata_file.exists():
                    with open(self.metadata_file, 'r', encoding='utf-8') as f:
                        self.metadata = json.load(f)
                
                # Load index
                if self.index_file.exists():
                    with open(self.index_file, 'r') as f:
                        self.index = json.load(f)
                
                return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False
    
    def clear(self) -> None:
        """Clear all data from the vector store."""
        with self._lock:
            self.vectors = None
            self.metadata = []
            self.index = {}
            self.dimension = None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with store statistics
        """
        with self._lock:
            return {
                'num_vectors': len(self.metadata),
                'dimension': self.dimension,
                'storage_dir': str(self.storage_dir),
                'memory_usage_mb': self._get_memory_usage(),
                'files_exist': {
                    'vectors': self.vectors_file.exists(),
                    'metadata': self.metadata_file.exists(),
                    'index': self.index_file.exists()
                }
            }
    
    def _matches_filter(self, metadata: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        """Check if metadata matches the filter criteria."""
        for key, value in filter_dict.items():
            if key not in metadata:
                return False
            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            elif metadata[key] != value:
                return False
        return True
    
    def _get_memory_usage(self) -> float:
        """Estimate memory usage in MB."""
        size = 0
        if self.vectors is not None:
            size += self.vectors.nbytes
        
        # Rough estimate for metadata (assuming average 1KB per entry)
        size += len(self.metadata) * 1024
        
        return size / (1024 * 1024)  # Convert to MB


class VectorStoreManager:
    """Manager class for handling multiple vector stores."""
    
    def __init__(self):
        self.stores = {}
    
    def get_store(self, name: str, storage_dir: Optional[str] = None) -> VectorStore:
        """
        Get or create a vector store.
        
        Args:
            name: Store name
            storage_dir: Optional custom storage directory
            
        Returns:
            VectorStore instance
        """
        if name not in self.stores:
            if storage_dir is None:
                storage_dir = f"app/data/vector_store_{name}"
            self.stores[name] = VectorStore(storage_dir)
        
        return self.stores[name]
    
    def save_all(self) -> Dict[str, bool]:
        """Save all stores to disk."""
        results = {}
        for name, store in self.stores.items():
            results[name] = store.save()
        return results
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all stores."""
        stats = {}
        for name, store in self.stores.items():
            stats[name] = store.get_stats()
        return stats