"""
Wellness Analysis Service for providing Quranic guidance on mental health and wellness topics.
Integrates with semantic search to find relevant verses for different wellness categories.
"""

from typing import List, Dict, Any, Optional, Tuple
from .verse_service import VerseService
from .embedding_service import EmbeddingService
from app.core.groq_client import groq_client
from app.models.database import get_db
from app.models.wellness_progress import WellnessProgress
from sqlalchemy.orm import Session
import json
import re

class WellnessService:
    _instance = None
    _initialized = False
    
    def __new__(cls, db: Session = None):
        if cls._instance is None:
            cls._instance = super(WellnessService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db: Session = None):
        if not self._initialized:
            self.verse_service = VerseService()
            self.embedding_service = None
            self._wellness_categories = self._initialize_wellness_categories()
            WellnessService._initialized = True
        self.db = db
    
    def _initialize_wellness_categories(self) -> Dict[str, Dict[str, Any]]:
        """Initialize wellness categories with their themes and search terms."""
        return {
            "anxiety_stress": {
                "name": "Anxiety & Stress Relief",
                "description": "Finding peace and tranquility through Quranic guidance",
                "themes": [
                    "peace and tranquility", "trust in Allah", "patience in hardship",
                    "relief from anxiety", "comfort in distress", "divine protection",
                    "inner peace", "calm heart", "serenity", "trust and reliance"
                ],
                "keywords": ["peace", "tranquility", "patience", "trust", "comfort", "protection", "calm"],
                "color": "#4CAF50",
                "icon": "🕊️"
            },
            "depression_sadness": {
                "name": "Depression & Sadness",
                "description": "Hope, healing, and spiritual upliftment from the Quran",
                "themes": [
                    "hope and optimism", "divine mercy", "healing and recovery",
                    "light after darkness", "comfort in grief", "spiritual strength",
                    "renewal of faith", "divine compassion", "overcoming despair"
                ],
                "keywords": ["hope", "mercy", "healing", "light", "comfort", "strength", "compassion"],
                "color": "#2196F3",
                "icon": "🌅"
            },
            "self_worth": {
                "name": "Self-Worth & Confidence",
                "description": "Understanding your value and purpose in Allah's creation",
                "themes": [
                    "human dignity", "purpose of creation", "divine love for humanity",
                    "individual worth", "spiritual potential", "noble character",
                    "self-respect", "confidence in faith", "personal growth"
                ],
                "keywords": ["dignity", "purpose", "creation", "worth", "potential", "character", "growth"],
                "color": "#FF9800",
                "icon": "⭐"
            },
            "relationships": {
                "name": "Relationships & Social Wellness",
                "description": "Building healthy relationships based on Islamic principles",
                "themes": [
                    "kindness and compassion", "forgiveness in relationships", "family bonds",
                    "friendship and brotherhood", "community support", "social justice",
                    "treating others well", "empathy and understanding", "conflict resolution"
                ],
                "keywords": ["kindness", "forgiveness", "family", "friendship", "community", "justice", "empathy"],
                "color": "#E91E63",
                "icon": "🤝"
            },
            "grief_loss": {
                "name": "Grief & Loss",
                "description": "Finding solace and understanding in times of loss",
                "themes": [
                    "comfort in loss", "eternal life", "divine wisdom in trials",
                    "patience in grief", "reunion in afterlife", "acceptance of fate",
                    "strength through faith", "healing from loss", "divine decree"
                ],
                "keywords": ["comfort", "eternal", "trials", "patience", "reunion", "acceptance", "healing"],
                "color": "#9C27B0",
                "icon": "🌙"
            },
            "anger_management": {
                "name": "Anger Management",
                "description": "Controlling anger and finding emotional balance through Islamic teachings",
                "themes": [
                    "controlling anger", "patience and forbearance", "forgiveness over revenge",
                    "emotional balance", "gentle response", "wisdom in conflict",
                    "self-control", "peaceful resolution", "restraint and moderation"
                ],
                "keywords": ["anger", "patience", "forgiveness", "balance", "control", "peace", "restraint"],
                "color": "#F44336",
                "icon": "🧘"
            },
            "gratitude_contentment": {
                "name": "Gratitude & Contentment",
                "description": "Cultivating thankfulness and satisfaction with Allah's blessings",
                "themes": [
                    "gratitude and thankfulness", "contentment with provisions", "counting blessings",
                    "satisfaction with fate", "appreciation of life", "spiritual wealth",
                    "inner richness", "divine generosity", "thankful heart"
                ],
                "keywords": ["gratitude", "thankfulness", "contentment", "blessings", "satisfaction", "wealth"],
                "color": "#8BC34A",
                "icon": "🙏"
            },
            "fear_worry": {
                "name": "Fear & Worry",
                "description": "Overcoming fears and worries through trust in Allah",
                "themes": [
                    "overcoming fear", "trust in divine plan", "courage and bravery",
                    "protection from harm", "faith over fear", "divine guidance",
                    "strength in weakness", "confidence in Allah", "fearlessness"
                ],
                "keywords": ["fear", "trust", "courage", "protection", "guidance", "strength", "confidence"],
                "color": "#607D8B",
                "icon": "🛡️"
            },
            "spiritual_growth": {
                "name": "Spiritual Growth",
                "description": "Developing spirituality and closeness to Allah",
                "themes": [
                    "spiritual development", "closeness to Allah", "purification of soul",
                    "remembrance of Allah", "spiritual discipline", "inner transformation",
                    "divine connection", "spiritual enlightenment", "soul purification"
                ],
                "keywords": ["spiritual", "closeness", "purification", "remembrance", "transformation", "connection"],
                "color": "#673AB7",
                "icon": "✨"
            },
            "life_purpose": {
                "name": "Life Purpose & Meaning",
                "description": "Understanding life's purpose and finding meaning through Islamic perspective",
                "themes": [
                    "purpose of life", "meaning and significance", "divine mission",
                    "life goals", "spiritual purpose", "worldly and eternal success",
                    "fulfilling potential", "serving humanity", "worship and service"
                ],
                "keywords": ["purpose", "meaning", "mission", "goals", "success", "potential", "service"],
                "color": "#795548",
                "icon": "🎯"
            }
        }

    def generate_wellness_report(self, user_id):
        """
        Generate a wellness report for a user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            dict: The wellness report.
        """
        return {
            "user_id": user_id,
            "report": {
                "summary": "User is in good health.",
                "recommendations": self.get_wellness_tips()
            }
        }

    def track_wellness_progress(self, user_id, progress_data):
        """
        Track wellness progress for a user.

        Args:
            user_id (str): The ID of the user.
            progress_data (dict): The progress data to track.

        Returns:
            dict: A response indicating the progress tracking result.
        """
        try:
            # Create a new WellnessProgress entry
            new_progress = WellnessProgress(
                user_id=user_id,
                mood=progress_data["mood"],
                energy_level=progress_data["energy_level"],
                stress_level=progress_data["stress_level"],
                notes=progress_data.get("notes"),
                analysis=progress_data.get("analysis")
            )

            # Add to the database session and commit
            self.db.add(new_progress)
            self.db.commit()
            self.db.refresh(new_progress)

            return {
                "status": "success",
                "message": f"Progress for user {user_id} tracked successfully.",
                "progress_data": progress_data
            }
        except Exception as e:
            self.db.rollback()
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }

    def get_tracked_progress(self, user_id):
        """
        Retrieve tracked progress for a user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            dict: The tracked progress data for the user.
        """
        try:
            # Query the database for the user's progress
            progress = self.db.query(WellnessProgress).filter_by(user_id=user_id).all()

            # Convert progress data to a list of dictionaries
            progress_list = [
                {
                    "id": p.id,
                    "mood": p.mood,
                    "energy_level": p.energy_level,
                    "stress_level": p.stress_level,
                    "notes": p.notes,
                    "analysis": p.analysis,
                    "timestamp": p.timestamp.isoformat() if p.timestamp else None
                }
                for p in progress
            ]

            return {
                "status": "success",
                "user_id": user_id,
                "progress": progress_list
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }

    def process_wellness_checkin(self, **data):
        """
        Process a wellness check-in.

        Args:
            **data: The keyword arguments for the wellness check-in.

        Returns:
            dict: A response indicating the result of the operation.
        """
        try:
            # Validate the input data
            required_fields = ["mood", "energy_level", "stress_level", "user_id"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

            # Validate optional fields
            notes = data.get("notes", None)  # Optional field

            # Example logic: Analyze the wellness data
            analysis_result = self.analyze_wellness_data(data)

            # Example logic: Track the wellness progress
            user_id = data["user_id"]
            progress_data = {
                "mood": data["mood"],
                "energy_level": data["energy_level"],
                "stress_level": data["stress_level"],
                "notes": notes,
                "analysis": analysis_result.get("analysis")
            }

            # Debug: Print progress data before storing
            print(f"Storing progress for user {user_id}: {progress_data}")

            self.track_wellness_progress(user_id, progress_data)

            return {
                "status": "success",
                "message": "Wellness check-in processed successfully.",
                "analysis": analysis_result.get("analysis"),
                "progress": progress_data
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }

    def analyze_with_groq(self, progress_data):
        """
        Analyze the tracked progress data using Groq.

        Args:
            progress_data (list): The tracked progress data for a user.

        Returns:
            dict: The analysis results from Groq.
        """
        try:
            # Example: Pass the data to Groq for analysis
            # Replace this with actual Groq client logic
            analysis_results = {
                "summary": "Analysis completed successfully.",
                "details": progress_data  # Replace with actual Groq analysis results
            }
            return analysis_results
        except Exception as e:
            return {
                "status": "error",
                "message": f"An error occurred during Groq analysis: {str(e)}"
            }

    def get_wellness_categories(self) -> List[Dict[str, Any]]:
        """Get all available wellness categories."""
        categories = []
        for category_id, category_data in self._wellness_categories.items():
            categories.append({
                "id": category_id,
                "name": category_data["name"],
                "description": category_data["description"],
                "color": category_data["color"],
                "icon": category_data["icon"]
            })
        return categories
    
    def analyze_wellness_need(self, user_input: str, max_verses: int = 5) -> Dict[str, Any]:
        """
        Analyze user input to determine wellness needs and provide relevant Quranic guidance.
        
        Args:
            user_input: User's description of their situation or feelings
            max_verses: Maximum number of verses to return
            
        Returns:
            Dictionary containing analysis results and recommended verses
        """
        try:
            # Detect relevant wellness categories
            detected_categories = self._detect_wellness_categories(user_input)
            
            # Find relevant verses using semantic search
            relevant_verses = self._find_wellness_verses(user_input, detected_categories, max_verses)
            
            # Generate personalized guidance
            guidance = self._generate_wellness_guidance(user_input, detected_categories, relevant_verses)
            
            return {
                "user_input": user_input,
                "detected_categories": detected_categories,
                "verses": relevant_verses,
                "guidance": guidance,
                "recommendations": self._get_wellness_recommendations(detected_categories)
            }
            
        except Exception as e:
            print(f"Error in wellness analysis: {e}")
            return {
                "user_input": user_input,
                "error": "Unable to analyze wellness needs at this time",
                "detected_categories": [],
                "verses": [],
                "guidance": "",
                "recommendations": []
            }
    
    def get_category_verses(self, category_id: str, max_verses: int = 10) -> Dict[str, Any]:
        """
        Get verses for a specific wellness category.
        
        Args:
            category_id: ID of the wellness category
            max_verses: Maximum number of verses to return
            
        Returns:
            Dictionary containing category info and relevant verses
        """
        if category_id not in self._wellness_categories:
            return {"error": "Invalid wellness category"}
        
        category = self._wellness_categories[category_id]
        
        # Search for verses using category themes
        all_verses = []
        for theme in category["themes"]:
            verses = self.verse_service.search_verses_by_theme(theme, max_results=3)
            all_verses.extend(verses)
        
        # Remove duplicates and limit results
        seen_verses = set()
        unique_verses = []
        for verse in all_verses:
            verse_key = verse.get('verse_number', verse.get('id', ''))
            if verse_key and verse_key not in seen_verses:
                seen_verses.add(verse_key)
                unique_verses.append(verse)
                if len(unique_verses) >= max_verses:
                    break
        
        return {
            "category": {
                "id": category_id,
                "name": category["name"],
                "description": category["description"],
                "color": category["color"],
                "icon": category["icon"]
            },
            "verses": unique_verses,
            "total_verses": len(unique_verses)
        }
    
    def _detect_wellness_categories(self, user_input: str) -> List[Dict[str, Any]]:
        """Detect which wellness categories are relevant to the user's input."""
        user_input_lower = user_input.lower()
        detected = []
        
        for category_id, category_data in self._wellness_categories.items():
            relevance_score = 0
            
            # Check keywords
            for keyword in category_data["keywords"]:
                if keyword in user_input_lower:
                    relevance_score += 2
            
            # Check themes (partial matching)
            for theme in category_data["themes"]:
                theme_words = theme.lower().split()
                for word in theme_words:
                    if len(word) > 3 and word in user_input_lower:
                        relevance_score += 1
            
            # If relevant, add to detected categories
            if relevance_score > 0:
                detected.append({
                    "id": category_id,
                    "name": category_data["name"],
                    "relevance_score": relevance_score,
                    "color": category_data["color"],
                    "icon": category_data["icon"]
                })
        
        # Sort by relevance score
        detected.sort(key=lambda x: x["relevance_score"], reverse=True)
        return detected[:3]  # Return top 3 most relevant categories
    
    def _find_wellness_verses(self, user_input: str, categories: List[Dict], max_verses: int) -> List[Dict]:
        """Find relevant verses using semantic search based on user input and detected categories."""
        all_verses = []
        
        # First, search directly with user input
        try:
            semantic_verses = self.verse_service.search_verses_semantic(
                user_input, 
                max_results=max_verses // 2, 
                min_similarity=0.2
            )
            for verse_data, similarity_score in semantic_verses:
                verse_data['similarity_score'] = similarity_score
                verse_data['source'] = 'direct_search'
                all_verses.append(verse_data)
        except Exception as e:
            print(f"Error in direct semantic search: {e}")
        
        # Then search using category themes
        for category in categories[:2]:  # Use top 2 categories
            category_data = self._wellness_categories.get(category["id"], {})
            for theme in category_data.get("themes", [])[:3]:  # Use top 3 themes per category
                try:
                    theme_verses = self.verse_service.search_verses_by_theme(theme, max_results=2)
                    for verse in theme_verses:
                        verse['source'] = f'category_{category["id"]}'
                        verse['theme'] = theme
                        all_verses.append(verse)
                except Exception as e:
                    print(f"Error searching theme '{theme}': {e}")
        
        # Remove duplicates and limit results
        seen_verses = set()
        unique_verses = []
        for verse in all_verses:
            verse_key = verse.get('verse_number', verse.get('id', ''))
            if verse_key and verse_key not in seen_verses:
                seen_verses.add(verse_key)
                unique_verses.append(verse)
                if len(unique_verses) >= max_verses:
                    break
        
        return unique_verses
    
    def _generate_wellness_guidance(self, user_input: str, categories: List[Dict], verses: List[Dict]) -> str:
        """Generate personalized wellness guidance using AI."""
        if not verses or not categories:
            return "May Allah grant you peace and guidance in your journey."
        
        try:
            # Prepare context for AI guidance
            category_names = [cat["name"] for cat in categories[:2]]
            verse_texts = []
            for verse in verses[:3]:
                verse_text = f"Surah {verse.get('surah_name', '')}: {verse.get('translation', '')}"
                verse_texts.append(verse_text)
            
            prompt = f"""
            Based on the user's concern: "{user_input}"
            
            Relevant wellness areas: {', '.join(category_names)}
            
            Relevant Quranic verses:
            {chr(10).join(verse_texts)}
            
            Provide compassionate, Islamic guidance (2-3 sentences) that:
            1. Acknowledges their feelings with empathy
            2. Connects their situation to the Quranic wisdom
            3. Offers hope and practical spiritual advice
            
            Keep it warm, supportive, and rooted in Islamic teachings.
            """
            
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating guidance: {e}")
            return "Remember that Allah is always with you. Turn to Him in prayer and find comfort in His words. May He ease your difficulties and grant you peace."
    
    def _get_wellness_recommendations(self, categories: List[Dict]) -> List[Dict[str, str]]:
        """Get wellness recommendations based on detected categories."""
        recommendations = []
        
        for category in categories[:2]:
            category_id = category["id"]
            
            if category_id == "anxiety_stress":
                recommendations.extend([
                    {"type": "practice", "text": "Practice dhikr (remembrance of Allah) regularly"},
                    {"type": "action", "text": "Perform wudu and pray when feeling anxious"},
                    {"type": "reading", "text": "Recite Surah Al-Fatiha and Ayat al-Kursi"}
                ])
            elif category_id == "depression_sadness":
                recommendations.extend([
                    {"type": "practice", "text": "Make dua during the blessed times (before Fajr, between Maghrib and Isha)"},
                    {"type": "action", "text": "Seek support from your Muslim community"},
                    {"type": "reading", "text": "Read about the stories of prophets and their trials"}
                ])
            elif category_id == "gratitude_contentment":
                recommendations.extend([
                    {"type": "practice", "text": "Keep a gratitude journal of Allah's blessings"},
                    {"type": "action", "text": "Give charity (sadaqah) regularly, even small amounts"},
                    {"type": "reading", "text": "Reflect on verses about Allah's countless blessings"}
                ])
            # Add more category-specific recommendations as needed
        
        return recommendations[:5]  # Limit to 5 recommendations

    # Legacy methods for backward compatibility
    def get_wellness_tips(self):
        """Legacy method - retrieve general wellness tips."""
        return [
            "Practice dhikr (remembrance of Allah) regularly",
            "Maintain regular prayers for spiritual wellness",
            "Read Quran daily for inner peace",
            "Practice gratitude for Allah's blessings"
        ]

    def analyze_wellness_data(self, data):
        """Legacy method - analyze wellness data."""
        try:
            # Enhanced analysis with Islamic perspective
            analysis = {
                "stress_level": "low" if data.get("stress", 5) < 5 else "high",
                "activity_score": data.get("steps", 0) * 0.1,
                "spiritual_wellness": "good" if data.get("prayer_consistency", 0) > 3 else "needs_improvement"
            }
            return {
                "status": "success",
                "analysis": analysis
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }