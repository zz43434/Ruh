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
        
        # Ensure embeddings are initialized
        self._ensure_embeddings_initialized()
        
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
        return [] 
    
    
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
            
    def search_chapters_by_theme(self, theme: str, max_results: int = 10) -> List[Dict]:
        """
        Enhanced search for chapters by theme with explanations and improved scoring.
        """
        try:
            # Ensure embedding service is initialized
            self._ensure_embeddings_initialized()
            
            # Increase search scope for better results
            top_k = min(max_results * 8, 100)  # Get more verses for better aggregation
            
            print(f"Searching for theme: '{theme}' with top_k: {top_k}")
            
            # Use semantic search to find relevant verses
            similar_verses = self.embedding_service.find_similar_verses(theme, top_k=top_k)
            
            print(f"Found {len(similar_verses) if similar_verses else 0} similar verses")
            
            if not similar_verses:
                print("No similar verses found, falling back to keyword search")
                return self._keyword_search_chapters_fallback(theme, max_results)
            
            # Enhanced aggregation with better scoring
            chapter_info = {}
            theme_keywords = self._extract_theme_keywords(theme)
            
            print(f"Theme keywords: {theme_keywords}")
            
            for verse_tuple in similar_verses:
                verse, similarity_score = verse_tuple
                surah_number = verse.get('surah_number')
                
                # Use 'analysis' field for English text, fallback to 'arabic_text'
                verse_text = verse.get('analysis', '') or verse.get('arabic_text', '')
                verse_number = verse.get('verse_id', '').split(':')[-1] if verse.get('verse_id') else None
                
                print(f"Processing verse: surah={surah_number}, text_length={len(verse_text)}, similarity={similarity_score}")
                print(f"Verse text preview: '{verse_text[:100]}...' (length: {len(verse_text)})")
                
                if surah_number not in chapter_info:
                    chapter_info[surah_number] = {
                        'surah_name': verse.get('surah_name', ''),
                        'number_of_verses': verse.get('number_of_verses', 0),
                        'revelation_place': verse.get('revelation_place', ''),
                        'verses': [],
                        'total_similarity': 0,
                        'max_similarity': 0,
                        'verse_count': 0,
                        'themes_found': set(),
                        'contextual_score': 0
                    }
                
                # Enhanced similarity calculation using the actual similarity from the tuple
                # Boost score for direct keyword matches
                keyword_boost = sum(1 for keyword in theme_keywords if keyword in verse_text.lower()) * 0.1
                adjusted_similarity = min(similarity_score + keyword_boost, 1.0)
                
                # Calculate contextual relevance
                contextual_score = self._calculate_contextual_relevance(verse_text, theme, theme_keywords)
                
                chapter_info[surah_number]['verses'].append({
                    'verse_number': verse_number,
                    'text': verse_text,  # Use the extracted verse_text
                    'similarity': adjusted_similarity,
                    'contextual_score': contextual_score
                })
                
                chapter_info[surah_number]['total_similarity'] += adjusted_similarity
                chapter_info[surah_number]['max_similarity'] = max(
                    chapter_info[surah_number]['max_similarity'], 
                    adjusted_similarity
                )
                chapter_info[surah_number]['verse_count'] += 1
                chapter_info[surah_number]['contextual_score'] += contextual_score
                
                # Extract themes from this verse
                verse_themes = self._extract_themes_from_verse(verse_text, theme)
                print(f"Extracted themes for verse: {verse_themes}")
                chapter_info[surah_number]['themes_found'].update(verse_themes)
            
            print(f"Processed {len(chapter_info)} chapters")
            
            # Enhanced scoring and ranking
            surah_results = []
            for surah_number, info in chapter_info.items():
                if info['verse_count'] == 0:
                    continue
                
                # Multi-factor scoring
                avg_similarity = info['total_similarity'] / info['verse_count']
                max_similarity = info['max_similarity']
                verse_density = min(info['verse_count'] / info['number_of_verses'], 1.0) if info['number_of_verses'] > 0 else 0
                avg_contextual = info['contextual_score'] / info['verse_count']
                theme_diversity = len(info['themes_found'])
                
                # Weighted composite score
                composite_score = (
                    avg_similarity * 0.4 +           # Average relevance
                    max_similarity * 0.3 +           # Peak relevance
                    verse_density * 0.15 +           # Coverage within surah
                    avg_contextual * 0.1 +           # Contextual understanding
                    min(theme_diversity * 0.05, 0.05) # Theme diversity bonus
                )
                
                # Sort verses by similarity for better presentation
                info['verses'].sort(key=lambda v: v['similarity'], reverse=True)
                
                # Generate enhanced explanation
                relevance_explanation = self._generate_enhanced_relevance_explanation(
                    info, theme, avg_similarity, verse_density, theme_diversity
                )
                
                surah_results.append({
                    'surah_number': surah_number,
                    'surah_name': info['surah_name'],
                    'number_of_verses': info['number_of_verses'],
                    'revelation_place': info['revelation_place'],
                    'similarity': composite_score,
                    'matching_verses': info['verses'][:3],  # Top 3 most relevant verses
                    'themes_found': list(info['themes_found']),
                    'relevance_explanation': relevance_explanation,
                    'verse_coverage': f"{info['verse_count']} verses match",
                    'contextual_relevance': avg_contextual
                })
            
            # Sort by composite score and return top results
            surah_results.sort(key=lambda x: x['similarity'], reverse=True)
            
            print(f"Returning {len(surah_results)} results")
            
            return surah_results[:max_results]
            
        except Exception as e:
            print(f"Error in enhanced chapter search: {e}")
            import traceback
            traceback.print_exc()
            return self._keyword_search_chapters_fallback(theme, max_results)

    def _extract_theme_keywords(self, theme: str) -> List[str]:
        """Extract key terms from the search theme for enhanced matching."""
        # Simple keyword extraction - could be enhanced with NLP
        import re
        
        # Remove common stop words and extract meaningful terms
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
        words = re.findall(r'\b\w+\b', theme.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords

    def _calculate_contextual_relevance(self, verse_text: str, theme: str, theme_keywords: List[str]) -> float:
        """Calculate contextual relevance beyond simple keyword matching."""
        verse_lower = verse_text.lower()
        theme_lower = theme.lower()
        
        # Direct theme mention
        if theme_lower in verse_lower:
            return 0.8
        
        # Keyword density
        keyword_matches = sum(1 for keyword in theme_keywords if keyword in verse_lower)
        keyword_density = keyword_matches / max(len(theme_keywords), 1)
        
        # Semantic proximity (simplified)
        semantic_indicators = {
            'prayer': ['worship', 'devotion', 'praise', 'glorify', 'remember'],
            'guidance': ['path', 'way', 'direction', 'lead', 'guide'],
            'mercy': ['compassion', 'forgiveness', 'kindness', 'grace'],
            'patience': ['perseverance', 'endurance', 'steadfast', 'bear'],
            'faith': ['believe', 'trust', 'conviction', 'certainty'],
            'justice': ['fair', 'right', 'equity', 'balance'],
            'knowledge': ['wisdom', 'understanding', 'learn', 'teach']
        }
        
        semantic_score = 0
        for concept, indicators in semantic_indicators.items():
            if concept in theme_lower:
                semantic_score += sum(0.1 for indicator in indicators if indicator in verse_lower)
        
        return min(keyword_density * 0.6 + semantic_score, 1.0)

    def _extract_themes_from_verse(self, verse_text: str, search_theme: str) -> set:
        """Extract themes found in a verse based on the search theme and semantic analysis."""
        verse_lower = verse_text.lower()
        search_lower = search_theme.lower()
        themes_found = set()
        
        # Add the main search theme if found
        if search_lower in verse_lower:
            themes_found.add(search_theme)
        
        # Theme mapping for semantic analysis
        theme_patterns = {
            'prayer': ['pray', 'worship', 'devotion', 'praise', 'glorify', 'remember allah', 'salah'],
            'guidance': ['guide', 'path', 'way', 'direction', 'lead', 'straight path', 'guidance'],
            'mercy': ['mercy', 'compassion', 'forgiveness', 'kindness', 'grace', 'merciful'],
            'patience': ['patience', 'perseverance', 'endurance', 'steadfast', 'bear', 'patient'],
            'faith': ['faith', 'believe', 'trust', 'conviction', 'certainty', 'believers'],
            'justice': ['justice', 'fair', 'right', 'equity', 'balance', 'just'],
            'knowledge': ['knowledge', 'wisdom', 'understanding', 'learn', 'teach', 'know'],
            'charity': ['charity', 'give', 'spend', 'poor', 'needy', 'zakah'],
            'forgiveness': ['forgive', 'pardon', 'mercy', 'repent', 'repentance'],
            'gratitude': ['grateful', 'thank', 'praise', 'appreciate', 'blessing']
        }
        
        # Check for theme patterns in the verse
        for theme, patterns in theme_patterns.items():
            for pattern in patterns:
                if pattern in verse_lower:
                    themes_found.add(theme)
                    break
        
        return themes_found

    def _generate_enhanced_relevance_explanation(self, info: Dict, theme: str, avg_similarity: float, 
                                               verse_density: float, theme_diversity: int) -> str:
        """Generate a comprehensive explanation for why this surah is relevant."""
        surah_name = info['surah_name']
        verse_count = info['verse_count']
        themes = list(info['themes_found'])
        
        explanation_parts = []
        
        # Main relevance reason
        if avg_similarity > 0.8:
            explanation_parts.append(f"Surah {surah_name} is highly relevant to '{theme}'")
        elif avg_similarity > 0.6:
            explanation_parts.append(f"Surah {surah_name} has strong connections to '{theme}'")
        else:
            explanation_parts.append(f"Surah {surah_name} relates to '{theme}'")
        
        # Verse coverage
        if verse_count == 1:
            explanation_parts.append("with 1 matching verse")
        else:
            explanation_parts.append(f"with {verse_count} matching verses")
        
        # Theme diversity
        if themes:
            if len(themes) == 1:
                explanation_parts.append(f"focusing on {themes[0].lower()}")
            elif len(themes) == 2:
                explanation_parts.append(f"covering {themes[0].lower()} and {themes[1].lower()}")
            else:
                explanation_parts.append(f"covering multiple aspects including {', '.join(themes[:2]).lower()}")
        
        # Coverage density
        if verse_density > 0.1:
            explanation_parts.append("with substantial coverage throughout the chapter")
        elif verse_density > 0.05:
            explanation_parts.append("with moderate coverage in the chapter")
        
        return " ".join(explanation_parts) + "."

    def _keyword_search_chapters_fallback(self, theme: str, max_results: int = 10) -> List[Dict]:
        """
        Fallback keyword search method for chapters with basic explanations.
        """
        matching_chapters = []
        theme_lower = theme.lower()
        
        # Get all chapters data (you'll need to implement this or use existing data)
        all_chapters = self.get_all_chapters()  # This method needs to be implemented
        
        for chapter in all_chapters:
            match_reasons = []
            
            # Check name match
            if theme_lower in chapter['name'].lower():
                match_reasons.append(f"chapter name contains '{theme}'")
            
            # Check summary match
            if theme_lower in chapter.get('summary', '').lower():
                match_reasons.append(f"chapter summary mentions '{theme}'")
            
            # Check revelation place match
            if theme_lower in chapter['revelation_place'].lower():
                match_reasons.append(f"revealed in {chapter['revelation_place']}")
            
            if match_reasons:
                chapter_with_explanation = chapter.copy()
                chapter_with_explanation.update({
                    "relevance_explanation": f"Surah {chapter['name']} matches because " + " and ".join(match_reasons) + ".",
                    "matching_verses": [],
                    "themes_found": [theme.title()],
                    "similarity": 0.5  # Default similarity for keyword matches
                })
                matching_chapters.append(chapter_with_explanation)
        
        # Limit results
        return matching_chapters[:max_results]

    def get_all_chapters(self) -> List[Dict]:
        """
        Get basic information about all chapters for fallback search.
        This is a simplified version that returns chapter metadata.
        """
        try:
            # Use the existing method to get first entries per surah
            chapters = self.get_first_entries_per_surah()
            
            # Transform to match expected format
            all_chapters = []
            for chapter in chapters:
                all_chapters.append({
                    'name': chapter.get('surah_name', ''),
                    'surah_number': chapter.get('surah_number', 0),
                    'number_of_verses': chapter.get('number_of_verses', 0),
                    'revelation_place': chapter.get('revelation_place', ''),
                    'summary': ''  # Could be enhanced with actual summaries
                })
            
            return all_chapters
            
        except Exception as e:
            print(f"Error getting all chapters: {e}")
            return []

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
