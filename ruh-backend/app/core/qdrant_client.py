import os
from typing import Tuple, List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from qdrant_client.models import ScrollResult

class QdrantClientWrapper:
    """
    Wrapper for Qdrant client to handle connection and common operations.
    """
    def __init__(self):
        # Get Qdrant connection parameters from environment or use defaults
        self.qdrant_host = os.environ.get("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.environ.get("QDRANT_PORT", 6333))
        self._client = None
    
    @property
    def client(self) -> QdrantClient:
        """
        Lazy initialization of the Qdrant client.
        """
        if self._client is None:
            print(f"Connecting to Qdrant at {self.qdrant_host}:{self.qdrant_port}")
            self._client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
        return self._client
    
    def get_collections(self) -> List[str]:
        """
        Get list of available collection names.
        """
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        print(f"Available collections: {collection_names}")
        return collection_names
    
    def find_collection(self, preferred_name: str = "quran_embeddings") -> Optional[str]:
        """
        Find a collection by name or return the first available collection.
        """
        collection_names = self.get_collections()
        
        if preferred_name in collection_names:
            return preferred_name
        
        # Try other possible collection names
        if len(collection_names) > 0:
            return collection_names[0]
        
        print("No collections found in Qdrant")
        return None
    
    def scroll_points(self, collection_name: str, batch_size: int = 100, scroll_filter=None, scroll_cursor=None) -> Tuple[List[PointStruct], Any]:
        """
        Scroll through points in a collection.
        """
        try:
            points, new_scroll_cursor = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=scroll_filter,
                limit=batch_size,
                offset=scroll_cursor
            )
            
            print(f"Retrieved {len(points)} points from Qdrant")
            return points, new_scroll_cursor
        except Exception as e:
            print(f"Error scrolling points: {e}")
            return [], None

# Create a singleton instance
qdrant = QdrantClientWrapper()