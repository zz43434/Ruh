import json
import random
import os
from typing import List, Dict, Optional

class VerseService:
    def __init__(self):
        self.verses_data = self._load_verses_data()
        self.translations_data = self._load_translations_data()
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
                'verses_with_translation': verses_with_translation,
                'summary': self._get_chapter_summary(surah['surah_number'])
            })
        return chapters

    def get_chapter_with_verses(self, surah_number: int) -> Optional[Dict]:
        """
        Get a chapter with all its verses. Shows translation if available, otherwise shows Arabic text only.
        """
        surah_info = self.get_surah_info(surah_number)
        if not surah_info:
            return None
            
        # Get all verses for this surah (whether they have translations or not)
        all_surah_verses = [
            verse for verse in self.all_verses 
            if verse['surah_number'] == surah_number
        ]
        
        return {
            'surah_number': surah_info['surah_number'],
            'name': surah_info['name'],
            'ayah_count': surah_info['ayah_count'],
            'revelation_place': surah_info['revelation_place'],
            'summary': self._get_chapter_summary(surah_number),
            'verses': all_surah_verses
        }

    def _get_chapter_summary(self, surah_number: int) -> str:
        """
        Get a summary for a chapter. This is a basic implementation.
        In a real app, you'd have a proper summary database.
        """
        summaries = {
            1: "The Opening - A prayer for guidance and the straight path. This chapter is recited in every unit of the Muslim prayer.",
            2: "The Cow - The longest chapter, covering various aspects of faith, law, and guidance for the Muslim community.",
            3: "The Family of Imran - Discusses the stories of Mary, Jesus, and emphasizes the unity of God's message.",
            4: "The Women - Addresses women's rights, family law, and social justice in Islamic society."
        }
        return summaries.get(surah_number, f"Chapter {surah_number} of the Holy Quran containing {self.get_surah_info(surah_number)['ayah_count'] if self.get_surah_info(surah_number) else 'several'} verses.")