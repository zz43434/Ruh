import json
import random
import os
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
        Falls back to keyword matching if embeddings are not available.
        """
        if not theme:
            return []
        
        try:
            # Ensure embeddings are initialized only when needed
            self._ensure_embeddings_initialized()
            
            # Try semantic search first
            similar_verses = self.embedding_service.find_similar_verses(
                query=theme, 
                top_k=max_results, 
                min_similarity=0.1
            )
            
            if similar_verses:
                # Convert to the expected format
                results = []
                for verse_data, similarity_score in similar_verses:
                    # Add similarity score to metadata for debugging/ranking
                    verse_data['similarity_score'] = similarity_score
                    results.append(verse_data)
                return results
            
        except Exception as e:
            print(f"Semantic search failed, falling back to keyword search: {e}")
        
        # Fallback to keyword matching
        return self._keyword_search_fallback(theme, max_results)
    
    def search_verses_semantic(self, query: str, max_results: int = 5, min_similarity: float = 0.1) -> List[Tuple[Dict, float]]:
        """
        Search verses using semantic similarity.
        Returns list of tuples (verse_dict, similarity_score).
        """
        try:
            # Ensure embeddings are initialized only when needed
            self._ensure_embeddings_initialized()
            
            # Try semantic search first
            similar_verses = self.embedding_service.find_similar_verses(
                query, max_results, min_similarity
            )
            
            if similar_verses:
                return similar_verses
            else:
                # If no semantic results, return empty list
                return []
                
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    
    def _ensure_embeddings_initialized(self):
        """
        Lazy initialization of embedding components only when needed.
        """
        if self.embedding_service is None:
            self.embedding_service = EmbeddingService()
            self.vector_store_manager = VectorStoreManager()
            self.verse_store = self.vector_store_manager.get_store("verses")
            self._initialize_embeddings()
    
    def _initialize_embeddings(self):
        """
        Initialize embeddings for all verses. Creates embeddings if they don't exist.
        """
        try:
            # Try to load existing embeddings
            if not self.embedding_service.load_verse_embeddings():
                print("No existing embeddings found. Creating new embeddings...")
                self._create_verse_embeddings()
            else:
                print("Loaded existing verse embeddings")
                
        except Exception as e:
            print(f"Error initializing embeddings: {e}")
            print("Verse service will use keyword search as fallback")

    def get_first_entries_per_surah(self) -> List[Dict]:
        """
        Get all entries from the Qdrant vector database, grouped by surah number and ordered ascending.
        Returns a list of entries with surah information.
        """
        try:
            from app.core.qdrant_client import qdrant
            
            # Try to find the right collection
            collection_name = "quran_embeddings"
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
        Search for chapters by theme using semantic similarity.
        Falls back to keyword matching if embeddings are not available.
        """
        if not theme:
            return self.get_all_chapters()
        
        try:
            # Get all chapters first
            all_chapters = self.get_all_chapters()
            
            # Create search texts for each chapter (name + summary)
            chapter_texts = []
            for chapter in all_chapters:
                search_text = f"{chapter['name']} {chapter.get('summary', '')}"
                chapter_texts.append(search_text)
            
            # Use embedding service to find similar chapters
            if hasattr(self.embedding_service, 'model') and self.embedding_service.model:
                # Generate embedding for the search query
                query_embedding = self.embedding_service.model.encode([theme])
                
                # Generate embeddings for chapter texts
                chapter_embeddings = self.embedding_service.model.encode(chapter_texts)
                
                # Calculate similarities
                from sklearn.metrics.pairwise import cosine_similarity
                similarities = cosine_similarity(query_embedding, chapter_embeddings)[0]
                
                # Create results with similarity scores
                results = []
                for i, (chapter, similarity) in enumerate(zip(all_chapters, similarities)):
                    if similarity > 0.1:  # Minimum similarity threshold
                        chapter_copy = chapter.copy()
                        chapter_copy['similarity_score'] = float(similarity)
                        results.append(chapter_copy)
                
                # Sort by similarity score (descending)
                results.sort(key=lambda x: x['similarity_score'], reverse=True)
                
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
        all_chapters = self.get_all_chapters()
        
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

    def _get_chapter_summary(self, surah_number: int) -> str:
        """
        Get a summary for a chapter using Groq AI generation.
        Falls back to hardcoded summaries if AI generation fails.
        """
        try:
            # Get chapter info
            surah_info = null
            if not surah_info:
                return f"Chapter {surah_number} of the Holy Quran."
            
            # Get sample verses from the chapter for context
            verses = self.get_surah_verses(surah_number)
            verses_sample = ""
            if verses and len(verses) > 0:
                # Take first 2-3 verses as sample context
                sample_verses = verses[:min(3, len(verses))]
                verses_sample = "\n".join([
                    f"Verse {v['verse_number']}: {v.get('english_translation', v.get('arabic_text', ''))}"
                    for v in sample_verses
                ])
            
            # Generate summary using Groq
            prompt = PROMPT_TEMPLATES.get_chapter_summary_prompt(
                chapter_number=surah_number,
                chapter_name=surah_info['name'],
                verse_count=surah_info['ayah_count'],
                verses_sample=verses_sample
            )
            
            summary = groq_client.generate_response(prompt, max_tokens=200, temperature=0.7)
            
            # Clean up the response
            if summary and len(summary.strip()) > 10:
                return summary.strip()
            else:
                # Fallback to hardcoded if response is too short
                return self._get_fallback_summary(surah_number, surah_info)
                
        except Exception as e:
            import logging
            logging.error(f"Error generating summary for chapter {surah_number}: {e}")
            # Fallback to hardcoded summaries

            return self._get_fallback_summary(surah_number, surah_info)
    
    def _get_fallback_summary(self, surah_number: int, surah_info: Dict = None) -> str:
        """
        Fallback hardcoded summaries for when AI generation fails.
        """
        summaries = {
            1: "The Opening - A prayer for guidance and the straight path. This chapter is recited in every unit of the Muslim prayer.",
            2: "The Cow - The longest chapter, covering various aspects of faith, law, and guidance for the Muslim community.",
            3: "The Family of Imran - Discusses the stories of Mary, Jesus, and emphasizes the unity of God's message.",
            4: "The Women - Addresses women's rights, family law, and social justice in Islamic society."
        }
        
        if surah_number in summaries:
            return summaries[surah_number]
        
        if surah_info:
            return f"Chapter {surah_number} of the Holy Quran containing {surah_info['ayah_count']} verses."
        else:
            return f"Chapter {surah_number} of the Holy Quran."