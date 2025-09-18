import json
import random
import os
from typing import List, Dict, Optional

class VerseService:
    def __init__(self):
        self.verses_data = self._load_verses_data()
        self.all_verses = self._flatten_verses()

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

    def _flatten_verses(self) -> List[Dict]:
        """
        Flatten all verses from all surahs into a single list.
        """
        all_verses = []
        for surah in self.verses_data:
            for verse in surah.get('verses', []):
                verse_data = {
                    'verse_number': verse['verse_number'],
                    'arabic_text': verse['arabic_text'],
                    'surah_number': surah['surah_number'],
                    'surah_name': surah['name'],
                    'ayah_count': surah['ayah_count'],
                    'revelation_place': surah['revelation_place']
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
        Search for verses by theme or keyword in Arabic text.
        Note: This is a basic implementation. For production, consider using
        proper Arabic text search with stemming and semantic search.
        """
        if not theme:
            return []
        
        matching_verses = []
        theme_lower = theme.lower()
        
        for verse in self.all_verses:
            # Simple keyword matching - can be enhanced with better Arabic search
            if (theme_lower in verse['arabic_text'].lower() or 
                theme_lower in verse['surah_name'].lower()):
                matching_verses.append(verse)
        
        # Limit results
        return matching_verses[:max_results]

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