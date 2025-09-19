from typing import List, Dict, Optional, Tuple
from .embedding_service import EmbeddingService
from .vector_store import VectorStoreManager
from app.core.groq_client import groq_client
from app.core.prompts import PROMPT_TEMPLATES
from app.core.qdrant_client import qdrant

class VerseService:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VerseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
        
            # Initialize RAG components lazily
            self.embedding_service = None
            self.vector_store_manager = None
            self.verse_store = None
            
            VerseService._initialized = True

    def search_verses_by_theme(self, theme: str, max_results: int = 5, sort_by: str = 'relevance') -> List[Dict]:
        """
        Search for verses by theme using semantic similarity (RAG).
        Maps results to include complete chapter information.
        Falls back to keyword matching if embeddings are not available.
        """
        if not theme:
            return []
        
        try:
            # Try semantic search first
            similar_verses = self.embedding_service.find_similar_verses(
                query=theme, 
                top_k=max_results, 
                min_similarity=0.1
            )
            
            if similar_verses:
                # Convert to the expected format with chapter information
                results = []
                for verse_data, similarity_score in similar_verses:
                    # Add similarity score to metadata for debugging/ranking
                    verse_data['similarity_score'] = similarity_score
                    
                    # Extract chapter information directly from verse data
                    surah_number = verse_data.get('surah_number')
                    if surah_number:
                        verse_data['chapter_info'] = {
                            'surah_number': surah_number,
                            'name': verse_data.get('surah_name', ''),
                            'revelation_place': verse_data.get('revelation_place', ''),
                            'verses_count': verse_data.get('verses_count', 0),
                            'summary': verse_data.get('surah_summary', '')
                        }
                    
                    results.append(verse_data)

                    print(results)
                return results
            
        except Exception as e:
            print(f"Semantic search failed, falling back to keyword search: {e}")
        
        # Fallback to keyword matching
        return self._keyword_search_fallback(theme, max_results)
    
    
    def _ensure_embeddings_initialized(self):
        """
        Lazy initialization of embedding components only when needed.
        """
        if self.embedding_service is None:
            self.embedding_service = EmbeddingService()
            self.vector_store_manager = VectorStoreManager()
            self.verse_store = self.vector_store_manager.get_store("verses")
    

    def get_first_entries_per_surah(self) -> List[Dict]:
        """
        Get all entries from the Qdrant vector database, grouped by surah number and ordered ascending.
        Returns a list of entries with surah information.
        """
        try:
            from app.core.qdrant_client import qdrant
            
            # Try to find the right collection
            collection_name = "quran_embeddings"
            # Verify collection exists
            if not collection_name:
                return []
            
            print(f"Using collection: {collection_name}")
            
            # Dictionary to store surah information and count verses
            surah_info = {}  # surah_number -> {surah_name, surah_number, number_of_verses, revelation_place}
            
            scroll_cursor = None
            
            while True:
                # Scroll through points
                try:
                    points, scroll_cursor = qdrant.scroll_points(
                        collection_name=collection_name,
                        batch_size=100,
                        scroll_filter=None,
                        scroll_cursor=scroll_cursor
                    )
                    
                    print(f"Retrieved {len(points)} points from Qdrant")
                    
                    if not points:
                        print("No points returned from scroll")
                        break
                    
                    for point in points:
                        # Process each point
                        if hasattr(point, 'payload') and point.payload:
                            surah_number = point.payload.get("surah_number")
                            
                            if surah_number:
                                if surah_number not in surah_info:
                                    # Create new entry for this surah
                                    surah_info[surah_number] = {
                                        "surah_name": point.payload.get("surah_name", ""),
                                        "surah_number": surah_number,
                                        "number_of_verses": 1,  # Start counting verses
                                        "revelation_place": point.payload.get("revelation_place", "")
                                    }
                                else:
                                    # Increment verse count for existing surah
                                    surah_info[surah_number]["number_of_verses"] += 1
                    
                    # Break if no more points
                    if not scroll_cursor:
                        print("No more scroll cursor, ending search")
                        break
                        
                except Exception as inner_e:
                    print(f"Error during scroll: {str(inner_e)}")
                    break
            
            # Convert dictionary to list and sort by surah number
            result = list(surah_info.values())
            result.sort(key=lambda x: x["surah_number"])
            
            print(f"Returning {len(result)} surah entries")
            return result
            
        except Exception as e:
            print(f"Error fetching entries from Qdrant: {str(e)}")
            return []
            
    def search_chapters_by_theme(self, theme: str, max_results: int = 10, sort_by: str = 'relevance') -> List[Dict]:
        """
        Search for chapters by theme using semantic similarity via find_similar_verses.
        Falls back to keyword matching if embeddings are not available.
        """
        
        try:
            # Initialize embedding service if needed
            if self.embedding_service is None:
                from .embedding_service import EmbeddingService
                self.embedding_service = EmbeddingService()
            
            # Use find_similar_verses to get semantically similar verses
            similar_verses = self.embedding_service.find_similar_verses(
                query=theme,
                top_k=max_results * 2,  # Get more results to aggregate by chapter
                min_similarity=0.1
            )
            
            # Extract chapter information from similar verses
            surah_info = {}
            for verse_data, similarity in similar_verses:
                surah_number = verse_data.get('surah_number')
                if not surah_number:
                    continue
                
                if surah_number not in surah_info:
                    surah_info[surah_number] = {
                        "surah_name": verse_data.get("surah_name", ""),
                        "surah_number": surah_number,
                        "number_of_verses": 1,  # Start counting verses
                        "revelation_place": verse_data.get("revelation_place", ""),
                        "similarity": similarity  # Keep similarity for sorting
                    }
                else:
                    # Increment verse count
                    surah_info[surah_number]["number_of_verses"] += 1
                    # Update similarity if this verse has higher score
                    if similarity > surah_info[surah_number]["similarity"]:
                        surah_info[surah_number]["similarity"] = similarity
            
            # Convert to list and sort
            results = list(surah_info.values())
            print(results)
            
            # Sort by relevance (similarity) or surah number
            if sort_by == 'relevance':
                results.sort(key=lambda x: x['similarity'], reverse=True)
            else:
                results.sort(key=lambda x: x['surah_number'])

            print(results)
            
                
            return results[:max_results]
            
        except Exception as e:
            print(f"Semantic chapter search failed, falling back to keyword search: {e}")
        
        # Fallback to keyword matching
        return self._keyword_search_chapters_fallback(theme, max_results)

    def _keyword_search_chapters_fallback(self, theme: str, max_results: int = 10) -> List[Dict]:
        """
        Fallback keyword search method for chapters.
        """
        matching_chapters = []
        theme_lower = theme.lower()
        
        for chapter in all_chapters:
            # Simple keyword matching
            if (theme_lower in chapter['name'].lower() or 
                theme_lower in chapter.get('summary', '').lower() or
                theme_lower in chapter['revelation_place'].lower()):
                matching_chapters.append(chapter)
        
        # Limit results
        return matching_chapters[:max_results]

    def get_chapter_with_verses(self, surah_number: int) -> Optional[Dict]:
        """
        Get a chapter with all its verses. Optionally includes translations and summary.
        Uses Qdrant client to fetch verses when available.
        
        Args:
            surah_number: The chapter number
            include_summary: Whether to generate and include AI summary (default: False)
            include_translations: Whether to include translations (default: True)
        """
        # Try to get verses from Qdrant
        all_surah_verses = self._get_verses_from_qdrant(surah_number) 
        print(all_surah_verses)

        surah_name = all_surah_verses[0]["surah_name"]
        ayah_count = len(all_surah_verses)
        revelation_place = all_surah_verses[0]["revelation_place"]
        surah_summary = all_surah_verses[0].get('surah_summary', '')
        print(surah_summary)
        chapter_data = {
            'surah_number': surah_number,
            'name': surah_name,
            'ayah_count': ayah_count,
            'revelation_place': revelation_place,   
            'verses': all_surah_verses,
            'surah_summary': surah_summary
        }
        
        return chapter_data
        
    def _get_verses_from_qdrant(self, surah_number: int) -> List[Dict]:
        """
        Get verses for a specific surah from Qdrant.
        
        Args:
            surah_number: The chapter number
            
        Returns:
            List of verse dictionaries
        """
        try:
            # Try to find the right collection
            collection_name = qdrant.find_collection("quran_embeddings")
            if not collection_name:
                return []
            
            # Filter for the specific surah
            surah_filter = {
                "must": [
                    {
                        "key": "surah_number",
                        "match": {"value": surah_number}
                    }
                ]
            }
            
            verses = []
            scroll_cursor = None
            
            while True:
                # Scroll through points
                points, scroll_cursor = qdrant.scroll_points(
                    collection_name=collection_name,
                    batch_size=100,
                    scroll_filter=surah_filter,
                    scroll_cursor=scroll_cursor
                )
                
                if not points:
                    break
                
                for point in points:
                    if hasattr(point, 'payload') and point.payload:
                        verse_data = {
                            'verse_number': point.payload.get('verse_number', ''),
                            'arabic_text': point.payload.get('arabic_text', ''),
                            'surah_number': point.payload.get('surah_number', surah_number),
                            'surah_name': point.payload.get('surah_name', ''),
                            'revelation_place': point.payload.get('revelation_place', ''),
                            'surah_summary': point.payload.get('surah_summary', ''),
                        }
                        
                        verses.append(verse_data)
                
                if not scroll_cursor:
                    break
            
            return verses
            
        except Exception as e:
            print(f"Error fetching verses from Qdrant: {str(e)}")
            return []
