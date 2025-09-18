import json
import random
import os
from typing import List, Dict, Optional, Tuple
from .embedding_service import EmbeddingService
from .vector_store import VectorStoreManager
from app.core.groq_client import groq_client
from app.core.prompts import PROMPT_TEMPLATES

class VerseService:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VerseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.verses_data = self._load_verses_data()
            self.translations_data = self._load_translations_data()
            self.all_verses = self._flatten_verses()
            
            # Initialize RAG components lazily
            self.embedding_service = None
            self.vector_store_manager = None
            self.verse_store = None
            
            VerseService._initialized = True

    def _load_verses_data(self) -> List[Dict]:
        """
        Load verses data from JSON file.
        """
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'quran_verses.json')
            with open(data_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print("Warning: quran_verses.json not found. Using empty data.")
            return []
        except json.JSONDecodeError:
            print("Warning: Invalid JSON in quran_verses.json. Using empty data.")
            return []

    def _load_translations_data(self) -> Dict:
        """
        Load translations data from quran_analysis.json file.
        """
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'quran_analysis.json')
            with open(data_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # Convert to dictionary for faster lookup
                translations = {}
                for item in data.get('analysis', []):
                    translations[item['verse']] = {
                        'translation': item['translation'],
                        'context': item.get('context', '')
                    }
                return translations
        except FileNotFoundError:
            print("Warning: quran_analysis.json not found. Using empty translations.")
            return {}
        except json.JSONDecodeError:
            print("Warning: Invalid JSON in quran_analysis.json. Using empty translations.")
            return {}

    def _flatten_verses(self) -> List[Dict]:
        """
        Flatten all verses from all surahs into a single list.
        """
        all_verses = []
        for surah in self.verses_data:
            for verse in surah.get('verses', []):
                # Use the verse_number directly as it's already in "surah:verse" format
                verse_id = verse['verse_number']
                
                # Get translation if available
                translation_data = self.translations_data.get(verse_id, {})
                
                verse_data = {
                    'verse_number': verse['verse_number'],
                    'arabic_text': verse['arabic_text'],
                    'surah_number': surah['surah_number'],
                    'surah_name': surah['name'],
                    'ayah_count': surah['ayah_count'],
                    'revelation_place': surah['revelation_place'],
                    'translation': translation_data.get('translation', ''),
                    'context': translation_data.get('context', '')
                }
                all_verses.append(verse_data)
        return all_verses

    def get_verse(self, verse_number: str) -> Optional[Dict]:
        """
        Retrieve a specific verse by its verse number (e.g., "1:1").
        """
        for verse in self.all_verses:
            if verse['verse_number'] == verse_number:
                return verse
        return None

    def get_verses(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """
        Get a paginated list of verses.
        """
        start_idx = offset
        end_idx = offset + limit
        return self.all_verses[start_idx:end_idx]

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
    
    def _keyword_search_fallback(self, theme: str, max_results: int = 5) -> List[Dict]:
        """
        Fallback keyword search method (original implementation).
        """
        matching_verses = []
        theme_lower = theme.lower()
        
        for verse in self.all_verses:
            # Simple keyword matching - can be enhanced with better Arabic search
            if (theme_lower in verse['arabic_text'].lower() or 
                theme_lower in verse['surah_name'].lower() or
                theme_lower in verse.get('translation', '').lower()):
                matching_verses.append(verse)
        
        # Limit results
        return matching_verses[:max_results]
    
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
    
    def _create_verse_embeddings(self):
        """
        Create embeddings for all verses and store them.
        """
        try:
            if not self.all_verses:
                print("No verses available for embedding creation")
                return
            
            print(f"Creating embeddings for {len(self.all_verses)} verses...")
            
            # Create embeddings using the embedding service
            self.embedding_service.create_verse_embeddings(self.all_verses)
            
            # Also store in vector store for future use
            vectors = self.embedding_service.verse_embeddings
            metadata = self.embedding_service.verse_metadata
            
            if vectors is not None and metadata:
                # Generate IDs for verses
                ids = [f"verse_{meta['verse_number']}" for meta in metadata]
                
                # Add to vector store
                self.verse_store.add_vectors(vectors, metadata, ids)
                self.verse_store.save()
                
                print("Successfully created and stored verse embeddings")
            
        except Exception as e:
            print(f"Error creating verse embeddings: {e}")
    
    def get_embedding_stats(self) -> Dict:
        """
        Get statistics about the embedding system.
        """
        # Only initialize if embeddings are needed
        self._ensure_embeddings_initialized()
        
        embedding_stats = self.embedding_service.get_embedding_stats()
        vector_store_stats = self.verse_store.get_stats()
        
        return {
            "embedding_service": embedding_stats,
            "vector_store": vector_store_stats
        }

    def get_all_verses(self) -> List[Dict]:
        """
        Retrieve all verses.
        """
        return self.all_verses

    def get_random_verse(self) -> Dict:
        """
        Get a random verse from the Quran.
        """
        if not self.all_verses:
            # Fallback if no data is loaded
            return {
                "verse_number": "65:3",
                "arabic_text": "وَمَن يَتَوَكَّلْ عَلَى ٱللَّهِ فَهُوَ حَسْبُهُۥٓ ۚ إِنَّ ٱللَّهَ بَـٰلِغُ أَمْرِهِۦ ۚ قَدْ جَعَلَ ٱللَّهُ لِكُلِّ شَىْءٍ قَدْرًا",
                "surah_name": "At-Talaq",
                "surah_number": 65,
                "ayah_count": 12,
                "revelation_place": "madinah"
            }
        
        return random.choice(self.all_verses)

    def get_surah_verses(self, surah_number: int) -> List[Dict]:
        """
        Get all verses from a specific surah.
        """
        return [verse for verse in self.all_verses if verse['surah_number'] == surah_number]

    def get_surah_info(self, surah_number: int) -> Optional[Dict]:
        """
        Get information about a specific surah.
        """
        for surah in self.verses_data:
            if surah['surah_number'] == surah_number:
                return {
                    'surah_number': surah['surah_number'],
                    'name': surah['name'],
                    'ayah_count': surah['ayah_count'],
                    'revelation_place': surah['revelation_place']
                }
        return None

    def get_all_chapters(self) -> List[Dict]:
        """
        Get a list of all chapters/surahs with basic information.
        """
        chapters = []
        for surah in self.verses_data:
            # Count verses with translations for this surah
            verses_with_translation = len([
                verse for verse in self.all_verses 
                if verse['surah_number'] == surah['surah_number'] and verse['translation']
            ])
            
            chapters.append({
                'surah_number': surah['surah_number'],
                'name': surah['name'],
                'ayah_count': surah['ayah_count'],
                'revelation_place': surah['revelation_place'],
                'verses_with_translation': verses_with_translation
            })
        return chapters

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

    def get_chapter_with_verses(self, surah_number: int, include_summary: bool = False, include_translations: bool = True) -> Optional[Dict]:
        """
        Get a chapter with all its verses. Optionally includes translations and summary.
        
        Args:
            surah_number: The chapter number
            include_summary: Whether to generate and include AI summary (default: False)
            include_translations: Whether to include translations (default: True)
        """
        surah_info = self.get_surah_info(surah_number)
        if not surah_info:
            return None
            
        # Get verses for this surah - optimize by filtering early
        if include_translations:
            # Include full verse data with translations
            all_surah_verses = [
                verse for verse in self.all_verses 
                if verse['surah_number'] == surah_number
            ]
        else:
            # Only include basic verse data without translations for better performance
            all_surah_verses = []
            for surah in self.verses_data:
                if surah['surah_number'] == surah_number:
                    for verse in surah.get('verses', []):
                        verse_data = {
                            'verse_number': verse['verse_number'],
                            'arabic_text': verse['arabic_text'],
                            'surah_number': surah['surah_number'],
                            'surah_name': surah['name'],
                            'ayah_count': surah['ayah_count'],
                            'revelation_place': surah['revelation_place']
                        }
                        all_surah_verses.append(verse_data)
                    break
        
        chapter_data = {
            'surah_number': surah_info['surah_number'],
            'name': surah_info['name'],
            'ayah_count': surah_info['ayah_count'],
            'revelation_place': surah_info['revelation_place'],
            'verses': all_surah_verses
        }
        
        # Only generate summary if explicitly requested
        if include_summary:
            chapter_data['summary'] = self._get_chapter_summary(surah_number)
        
        return chapter_data

    def _get_chapter_summary(self, surah_number: int) -> str:
        """
        Get a summary for a chapter using Groq AI generation.
        Falls back to hardcoded summaries if AI generation fails.
        """
        try:
            # Get chapter info
            surah_info = self.get_surah_info(surah_number)
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
            surah_info = self.get_surah_info(surah_number)
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