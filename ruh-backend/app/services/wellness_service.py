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
    
    def _analyze_mood(self, mood_text):
        """Analyze mood from text input."""
        mood_lower = mood_text.lower()
        
        # Define mood categories with emojis and keywords
        mood_patterns = {
            "very_positive": {
                "keywords": ["😄", "😊", "🥰", "😍", "🤩", "ecstatic", "amazing", "fantastic", "wonderful", "joyful", "blissful"],
                "score": 9,
                "category": "Very Positive"
            },
            "positive": {
                "keywords": ["😀", "🙂", "😌", "happy", "good", "great", "cheerful", "content", "pleased", "upbeat"],
                "score": 7,
                "category": "Positive"
            },
            "neutral": {
                "keywords": ["😐", "😑", "neutral", "okay", "fine", "average", "normal", "stable"],
                "score": 5,
                "category": "Neutral"
            },
            "negative": {
                "keywords": ["😔", "😞", "😟", "🙁", "sad", "down", "low", "upset", "disappointed", "troubled"],
                "score": 3,
                "category": "Negative"
            },
            "very_negative": {
                "keywords": ["😭", "😢", "😰", "😨", "devastated", "terrible", "awful", "depressed", "hopeless", "overwhelmed"],
                "score": 1,
                "category": "Very Negative"
            }
        }
        
        # Analyze mood
        detected_mood = "neutral"
        mood_score = 5
        
        for mood_type, pattern in mood_patterns.items():
            for keyword in pattern["keywords"]:
                if keyword in mood_lower:
                    detected_mood = mood_type
                    mood_score = pattern["score"]
                    break
            if detected_mood != "neutral":
                break
        
        return {
            "raw_mood": mood_text,
            "detected_category": mood_patterns[detected_mood]["category"],
            "mood_score": mood_score,
            "needs_attention": mood_score <= 3
        }
    
    def _analyze_energy_level(self, energy_level):
        """Analyze energy level (1-10 scale)."""
        if energy_level >= 8:
            category = "High Energy"
            status = "excellent"
        elif energy_level >= 6:
            category = "Good Energy"
            status = "good"
        elif energy_level >= 4:
            category = "Moderate Energy"
            status = "fair"
        else:
            category = "Low Energy"
            status = "needs_attention"
        
        return {
            "level": energy_level,
            "category": category,
            "status": status,
            "needs_attention": energy_level <= 3
        }
    
    def _analyze_stress_level(self, stress_level):
        """Analyze stress level (1-10 scale)."""
        if stress_level <= 2:
            category = "Very Low Stress"
            status = "excellent"
        elif stress_level <= 4:
            category = "Low Stress"
            status = "good"
        elif stress_level <= 6:
            category = "Moderate Stress"
            status = "fair"
        elif stress_level <= 8:
            category = "High Stress"
            status = "concerning"
        else:
            category = "Very High Stress"
            status = "needs_attention"
        
        return {
            "level": stress_level,
            "category": category,
            "status": status,
            "needs_attention": stress_level >= 7
        }
    
    def _calculate_wellness_score(self, energy_level, stress_level, mood_analysis):
        """Calculate overall wellness score (1-10 scale)."""
        # Weight the components
        energy_weight = 0.3
        stress_weight = 0.4  # Stress has higher impact (inverted)
        mood_weight = 0.3
        
        # Calculate weighted score
        energy_score = energy_level
        stress_score = 11 - stress_level  # Invert stress (lower stress = higher score)
        mood_score = mood_analysis["mood_score"]
        
        wellness_score = (
            energy_score * energy_weight +
            stress_score * stress_weight +
            mood_score * mood_weight
        )
        
        return round(wellness_score, 1)
    
    def _assess_spiritual_wellness(self, wellness_score, mood_analysis, stress_analysis):
        """Assess spiritual wellness based on overall state."""
        if wellness_score >= 7.5 and not mood_analysis["needs_attention"] and not stress_analysis["needs_attention"]:
            return "excellent"
        elif wellness_score >= 6.0 and not (mood_analysis["needs_attention"] and stress_analysis["needs_attention"]):
            return "good"
        elif wellness_score >= 4.0:
            return "fair"
        else:
            return "needs_attention"
    
    def _get_personalized_recommendations(self, mood_analysis, energy_analysis, stress_analysis):
        """Get personalized recommendations based on analysis."""
        recommendations = []
        
        # Mood-based recommendations
        if mood_analysis["needs_attention"]:
            recommendations.extend([
                {"type": "spiritual", "text": "Recite Surah Ad-Duha for comfort and hope"},
                {"type": "practice", "text": "Make dua during quiet moments for peace of heart"},
                {"type": "action", "text": "Reach out to a trusted friend or family member"}
            ])
        
        # Energy-based recommendations
        if energy_analysis["needs_attention"]:
            recommendations.extend([
                {"type": "physical", "text": "Take short walks while making dhikr"},
                {"type": "spiritual", "text": "Perform wudu to refresh yourself spiritually"},
                {"type": "practice", "text": "Get adequate rest and maintain regular prayer times"}
            ])
        
        # Stress-based recommendations
        if stress_analysis["needs_attention"]:
            recommendations.extend([
                {"type": "spiritual", "text": "Recite 'La hawla wa la quwwata illa billah' for strength"},
                {"type": "practice", "text": "Practice deep breathing while saying 'SubhanAllah'"},
                {"type": "action", "text": "Break down overwhelming tasks into smaller steps"}
            ])
        
        # General positive recommendations
        if not any([mood_analysis["needs_attention"], energy_analysis["needs_attention"], stress_analysis["needs_attention"]]):
            recommendations.extend([
                {"type": "gratitude", "text": "Express gratitude through extra dhikr and dua"},
                {"type": "sharing", "text": "Share your positive energy by helping others"},
                {"type": "spiritual", "text": "Use this good state to increase your worship"}
            ])
        
        return recommendations[:5]  # Limit to 5 recommendations

    def get_tracked_progress(self, user_id, limit=20, offset=0):
        """
        Retrieve tracked progress for a user with trend analysis.

        Args:
            user_id (str): The ID of the user.
            limit (int): Maximum number of entries to return.
            offset (int): Number of entries to skip.

        Returns:
            dict: The tracked progress data with trend analysis for the user.
        """
        try:
            # Query the database for the user's progress (ordered by timestamp desc)
            progress_query = self.db.query(WellnessProgress).filter_by(user_id=user_id)
            total_entries = progress_query.count()
            
            progress = progress_query.order_by(WellnessProgress.timestamp.desc()).offset(offset).limit(limit).all()

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
            
            # Add trend analysis if we have enough data
            trend_analysis = None
            if len(progress) >= 2:
                trend_analysis = self._analyze_wellness_trends(progress)

            return {
                "status": "success",
                "user_id": user_id,
                "total_entries": total_entries,
                "wellness_history": progress_list,
                "trend_analysis": trend_analysis
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }
    
    def _analyze_wellness_trends(self, progress_data):
        """Analyze trends in wellness data over time."""
        if len(progress_data) < 2:
            return None
        
        # Extract numerical data for trend analysis
        energy_levels = [p.energy_level for p in progress_data if p.energy_level is not None]
        stress_levels = [p.stress_level for p in progress_data if p.stress_level is not None]
        
        # Analyze mood trends
        mood_scores = []
        for p in progress_data:
            if p.mood:
                mood_analysis = self._analyze_mood(p.mood)
                mood_scores.append(mood_analysis["mood_score"])
        
        trends = {}
        
        # Energy trend analysis
        if len(energy_levels) >= 2:
            energy_trend = self._calculate_trend(energy_levels)
            trends["energy"] = {
                "direction": energy_trend["direction"],
                "change": energy_trend["change"],
                "average": round(sum(energy_levels) / len(energy_levels), 1),
                "latest": energy_levels[0],  # Most recent first
                "status": "improving" if energy_trend["direction"] == "increasing" else "declining" if energy_trend["direction"] == "decreasing" else "stable"
            }
        
        # Stress trend analysis
        if len(stress_levels) >= 2:
            stress_trend = self._calculate_trend(stress_levels)
            trends["stress"] = {
                "direction": stress_trend["direction"],
                "change": stress_trend["change"],
                "average": round(sum(stress_levels) / len(stress_levels), 1),
                "latest": stress_levels[0],  # Most recent first
                "status": "improving" if stress_trend["direction"] == "decreasing" else "worsening" if stress_trend["direction"] == "increasing" else "stable"
            }
        
        # Mood trend analysis
        if len(mood_scores) >= 2:
            mood_trend = self._calculate_trend(mood_scores)
            trends["mood"] = {
                "direction": mood_trend["direction"],
                "change": mood_trend["change"],
                "average": round(sum(mood_scores) / len(mood_scores), 1),
                "latest": mood_scores[0],  # Most recent first
                "status": "improving" if mood_trend["direction"] == "increasing" else "declining" if mood_trend["direction"] == "decreasing" else "stable"
            }
        
        # Overall wellness trend
        overall_status = self._assess_overall_trend(trends)
        
        return {
            "trends": trends,
            "overall_status": overall_status,
            "data_points": len(progress_data),
            "recommendations": self._get_trend_based_recommendations(trends)
        }
    
    def _calculate_trend(self, values):
        """Calculate trend direction and magnitude for a list of values."""
        if len(values) < 2:
            return {"direction": "stable", "change": 0}
        
        # Simple trend calculation using first and last values
        recent_avg = sum(values[:3]) / min(3, len(values))  # Average of 3 most recent
        older_avg = sum(values[-3:]) / min(3, len(values))  # Average of 3 oldest
        
        change = recent_avg - older_avg
        
        if abs(change) < 0.5:
            direction = "stable"
        elif change > 0:
            direction = "increasing"
        else:
            direction = "decreasing"
        
        return {
            "direction": direction,
            "change": round(change, 1)
        }
    
    def _assess_overall_trend(self, trends):
        """Assess overall wellness trend based on individual metrics."""
        positive_trends = 0
        negative_trends = 0
        total_trends = 0
        
        for metric, trend_data in trends.items():
            total_trends += 1
            if metric == "stress":
                # For stress, decreasing is positive
                if trend_data["status"] == "improving":
                    positive_trends += 1
                elif trend_data["status"] == "worsening":
                    negative_trends += 1
            else:
                # For energy and mood, increasing is positive
                if trend_data["status"] == "improving":
                    positive_trends += 1
                elif trend_data["status"] in ["declining", "worsening"]:
                    negative_trends += 1
        
        if positive_trends > negative_trends:
            return "improving"
        elif negative_trends > positive_trends:
            return "declining"
        else:
            return "stable"
    
    def _get_trend_based_recommendations(self, trends):
        """Get recommendations based on wellness trends."""
        recommendations = []
        
        # Energy trend recommendations
        if "energy" in trends and trends["energy"]["status"] == "declining":
            recommendations.extend([
                {"type": "physical", "text": "Consider increasing physical activity with Islamic exercises like walking to the mosque"},
                {"type": "spiritual", "text": "Maintain consistent prayer times to regulate your daily rhythm"}
            ])
        
        # Stress trend recommendations
        if "stress" in trends and trends["stress"]["status"] == "worsening":
            recommendations.extend([
                {"type": "spiritual", "text": "Increase dhikr and remembrance of Allah during stressful moments"},
                {"type": "practice", "text": "Practice istighfar (seeking forgiveness) to find inner peace"}
            ])
        
        # Mood trend recommendations
        if "mood" in trends and trends["mood"]["status"] == "declining":
            recommendations.extend([
                {"type": "spiritual", "text": "Read Surah Ash-Sharh for comfort during difficult times"},
                {"type": "community", "text": "Connect with your Muslim community for support and companionship"}
            ])
        
        # Positive trend reinforcement
        if all(trend.get("status") in ["improving", "stable"] for trend in trends.values()):
            recommendations.extend([
                {"type": "gratitude", "text": "Continue your positive practices and express gratitude to Allah"},
                {"type": "sharing", "text": "Share your wellness journey to inspire others in your community"}
            ])
        
        return recommendations[:4]  # Limit to 4 recommendations

    def process_wellness_checkin(self, **data):
        """
        Process a wellness check-in by storing the data only.
        Analysis is now separate and triggered on user request.

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

            # Store the wellness check-in data without analysis
            user_id = data["user_id"]
            progress_data = {
                "mood": data["mood"],
                "energy_level": data["energy_level"],
                "stress_level": data["stress_level"],
                "notes": notes,
                "analysis": None  # No analysis during check-in
            }

            # Debug: Print progress data before storing
            print(f"Storing check-in for user {user_id}: {progress_data}")

            track_result = self.track_wellness_progress(user_id, progress_data)
            if track_result.get("status") != "success":
                print(f"Failed to track progress: {track_result}")
                return {
                    "status": "error",
                    "message": "Failed to store check-in data"
                }

            return {
                "status": "success",
                "message": "Wellness check-in submitted successfully.",
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
    
    def _generate_pattern_based_guidance(self, mood_analysis, energy_analysis, stress_analysis, detected_categories):
        """Generate Quranic guidance based on analyzed wellness patterns."""
        try:
            # Determine primary wellness concern
            primary_concern = self._identify_primary_concern(mood_analysis, energy_analysis, stress_analysis)
            
            # Create contextual input for guidance
            context_input = self._create_wellness_context(primary_concern, mood_analysis, energy_analysis, stress_analysis)
            
            # Get relevant verses based on wellness patterns
            relevant_verses = self._get_pattern_verses(primary_concern, detected_categories)
            
            # Generate personalized guidance
            if relevant_verses:
                guidance = self._generate_wellness_guidance(context_input, detected_categories, relevant_verses)
            else:
                guidance = self._get_default_spiritual_guidance(primary_concern)
            
            return {
                "primary_concern": primary_concern,
                "guidance": guidance,
                "relevant_verses": relevant_verses[:2],  # Top 2 verses
                "spiritual_practices": self._get_spiritual_practices(primary_concern)
            }
            
        except Exception as e:
            print(f"Error generating pattern-based guidance: {e}")
            return {
                "primary_concern": "general_wellness",
                "guidance": "Remember that Allah is always with you. Turn to Him in prayer and find comfort in His words.",
                "relevant_verses": [],
                "spiritual_practices": ["Regular prayer (Salah)", "Dhikr (remembrance of Allah)", "Reading Quran"]
            }
    
    def _identify_primary_concern(self, mood_analysis, energy_analysis, stress_analysis):
        """Identify the primary wellness concern based on analysis."""
        concerns = []
        
        # Check stress level
        if stress_analysis.get('level', 'low') in ['high', 'very_high']:
            concerns.append(('stress', stress_analysis.get('score', 0)))
        
        # Check mood
        if mood_analysis.get('category', 'neutral') in ['negative', 'very_negative']:
            concerns.append(('mood', abs(mood_analysis.get('score', 0))))
        
        # Check energy
        if energy_analysis.get('level', 'moderate') in ['low', 'very_low']:
            concerns.append(('energy', abs(energy_analysis.get('score', 0))))
        
        # Return the highest scoring concern or default
        if concerns:
            return max(concerns, key=lambda x: x[1])[0]
        return 'general_wellness'
    
    def _create_wellness_context(self, primary_concern, mood_analysis, energy_analysis, stress_analysis):
        """Create contextual input for guidance generation."""
        context_map = {
            'stress': f"I'm feeling overwhelmed and stressed. My stress level is {stress_analysis.get('level', 'moderate')}.",
            'mood': f"I'm struggling with my mood and feeling {mood_analysis.get('category', 'neutral')}.",
            'energy': f"I'm feeling low on energy and motivation. My energy level is {energy_analysis.get('level', 'moderate')}.",
            'general_wellness': "I want to improve my overall wellness and spiritual connection."
        }
        return context_map.get(primary_concern, context_map['general_wellness'])
    
    def _get_pattern_verses(self, primary_concern, detected_categories):
        """Get verses relevant to the identified wellness pattern."""
        # Map concerns to category themes
        concern_themes = {
            'stress': ['anxiety', 'peace', 'trust', 'patience'],
            'mood': ['hope', 'gratitude', 'patience', 'mercy'],
            'energy': ['strength', 'motivation', 'purpose', 'guidance'],
            'general_wellness': ['peace', 'guidance', 'gratitude', 'strength']
        }
        
        themes = concern_themes.get(primary_concern, concern_themes['general_wellness'])
        verses = []
        
        # Search for verses using themes
        for theme in themes[:2]:  # Use top 2 themes
            try:
                theme_verses = self.verse_service.search_verses_by_theme(theme, max_results=2)
                verses.extend(theme_verses)
            except Exception as e:
                print(f"Error searching verses for theme {theme}: {e}")
                continue
        
        return verses[:3]  # Return top 3 verses
    
    def _get_default_spiritual_guidance(self, primary_concern):
        """Get default spiritual guidance when verses are not available."""
        guidance_map = {
            'stress': "When you feel overwhelmed, remember Allah's promise: 'And whoever relies upon Allah - then He is sufficient for him.' (Quran 65:3). Take time for prayer and dhikr to find peace.",
            'mood': "In times of difficulty, remember that Allah is Ar-Rahman (The Most Merciful). Turn to Him in prayer and remember that after hardship comes ease (Quran 94:6).",
            'energy': "When you feel weak, remember that Allah gives strength to those who seek it. 'And it is He who created the heavens and earth in truth. And the day He says, \"Be,\" and it is, His word is the truth.' (Quran 6:73)",
            'general_wellness': "Seek balance in all aspects of life, as Islam teaches moderation. Remember Allah in all your affairs and trust in His wisdom."
        }
        return guidance_map.get(primary_concern, guidance_map['general_wellness'])
    
    def _get_spiritual_practices(self, primary_concern):
        """Get recommended spiritual practices based on primary concern."""
        practices_map = {
            'stress': [
                "Recite 'La hawla wa la quwwata illa billah' (There is no power except with Allah)",
                "Perform Salat al-Hajah (Prayer of Need)",
                "Practice deep breathing with dhikr"
            ],
            'mood': [
                "Recite Surah Al-Fatiha with reflection",
                "Practice gratitude by listing Allah's blessings",
                "Seek forgiveness through Istighfar"
            ],
            'energy': [
                "Recite Surah Al-Falaq and An-Nas for protection and strength",
                "Make du'a for guidance and energy",
                "Engage in dhikr during daily activities"
            ],
            'general_wellness': [
                "Maintain regular prayer times",
                "Read Quran daily with contemplation",
                "Practice dhikr throughout the day"
            ]
        }
        return practices_map.get(primary_concern, practices_map['general_wellness'])

    def analyze_wellness_with_ai(self, user_id: str, min_checkins: int = 3) -> Dict[str, Any]:
        """
        Analyze wellness patterns using AI after ensuring sufficient check-ins.
        Generates Islamic perspective themes and recommends relevant Quranic verses.

        Args:
            user_id: The user ID to analyze
            min_checkins: Minimum number of check-ins required for analysis

        Returns:
            dict: AI-powered analysis with Islamic themes and verse recommendations
        """
        try:
            # Get user's check-in history
            history_result = self.get_tracked_progress(user_id, limit=50, offset=0)
            checkins = history_result.get("wellness_history", [])
            
            # Validate minimum check-ins requirement
            if len(checkins) < min_checkins:
                return {
                    "status": "insufficient_data",
                    "message": f"Analysis requires at least {min_checkins} check-ins. You have {len(checkins)}.",
                    "current_checkins": len(checkins),
                    "required_checkins": min_checkins
                }
            
            # Prepare data for AI analysis
            analysis_data = self._prepare_checkin_data_for_ai(checkins)
            
            # Generate AI analysis with Islamic perspective
            ai_analysis = self._generate_ai_wellness_analysis(analysis_data)
            
            if ai_analysis.get("status") != "success":
                return ai_analysis
            
            # Extract themes from AI analysis
            themes = ai_analysis.get("themes", [])
            
            # Find relevant Quranic verses using semantic search
            verse_recommendations = self._find_verses_for_themes(themes)
            
            # Combine analysis with verse recommendations
            comprehensive_analysis = {
                "status": "success",
                "user_id": user_id,
                "analysis_date": checkins[0].get("timestamp") if checkins else None,
                "data_points": len(checkins),
                "ai_analysis": ai_analysis.get("analysis", {}),
                "islamic_themes": themes,
                "verse_recommendations": verse_recommendations,
                "spiritual_guidance": ai_analysis.get("spiritual_guidance", ""),
                "recommendations": ai_analysis.get("recommendations", [])
            }
            
            return comprehensive_analysis
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Analysis failed: {str(e)}"
            }

    def _prepare_checkin_data_for_ai(self, checkins: List[Dict]) -> Dict[str, Any]:
        """
        Prepare check-in data for AI analysis by extracting patterns and trends.
        """
        if not checkins:
            return {}
        
        # Extract mood patterns
        moods = [checkin.get("mood", "") for checkin in checkins]
        energy_levels = [checkin.get("energy_level", 5) for checkin in checkins if checkin.get("energy_level")]
        stress_levels = [checkin.get("stress_level", 5) for checkin in checkins if checkin.get("stress_level")]
        notes = [checkin.get("notes", "") for checkin in checkins if checkin.get("notes")]
        
        # Calculate averages and trends
        avg_energy = sum(energy_levels) / len(energy_levels) if energy_levels else 5
        avg_stress = sum(stress_levels) / len(stress_levels) if stress_levels else 5
        
        # Recent vs older comparison (last 3 vs previous)
        recent_energy = energy_levels[:3] if len(energy_levels) >= 3 else energy_levels
        recent_stress = stress_levels[:3] if len(stress_levels) >= 3 else stress_levels
        
        return {
            "total_checkins": len(checkins),
            "mood_patterns": moods,
            "energy_levels": energy_levels,
            "stress_levels": stress_levels,
            "notes": notes,
            "averages": {
                "energy": round(avg_energy, 1),
                "stress": round(avg_stress, 1)
            },
            "recent_patterns": {
                "energy": recent_energy,
                "stress": recent_stress,
                "moods": moods[:3] if len(moods) >= 3 else moods
            }
        }

    def _generate_ai_wellness_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered wellness analysis using Groq."""
        try:
            prompt = self._create_islamic_wellness_prompt(data)
            
            # Use the correct method from groq_client
            response = groq_client.generate_response(
                prompt=prompt,
                max_tokens=800,
                temperature=0.7
            )
            
            return self._parse_ai_wellness_response(response)
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            return {
                "status": "error",
                "message": f"AI analysis failed: {str(e)}"
            }

    def _create_islamic_wellness_prompt(self, data: Dict[str, Any]) -> str:
        """
        Create a comprehensive prompt for AI wellness analysis from Islamic perspective.
        """
        prompt = f"""
Analyze the following wellness data from an Islamic perspective and provide comprehensive guidance:

**Wellness Data Summary:**
- Total check-ins: {data.get('total_checkins', 0)}
- Average energy level: {data.get('averages', {}).get('energy', 'N/A')}/10
- Average stress level: {data.get('averages', {}).get('stress', 'N/A')}/10
- Recent mood patterns: {', '.join(data.get('recent_patterns', {}).get('moods', []))}
- User notes: {'; '.join([note for note in data.get('notes', []) if note])}

**Analysis Requirements:**
1. **Spiritual Themes**: Identify 2-3 key Islamic themes relevant to this person's wellness journey (e.g., patience/sabr, gratitude/shukr, trust in Allah/tawakkul, inner peace/sakina, etc.)

2. **Wellness Assessment**: Provide a compassionate assessment of their spiritual and emotional state from an Islamic perspective

3. **Spiritual Guidance**: Offer specific Islamic guidance and practices that would benefit them

4. **Practical Recommendations**: Suggest 3-4 actionable steps rooted in Islamic teachings

**Response Format:**
Please structure your response as follows:

THEMES: [List 2-3 key Islamic themes, separated by commas]

ANALYSIS: [Your comprehensive wellness assessment from Islamic perspective]

SPIRITUAL_GUIDANCE: [Specific spiritual guidance and practices]

RECOMMENDATIONS: [List 3-4 practical recommendations, each on a new line starting with "-"]

Focus on compassion, hope, and practical Islamic solutions. Remember that every soul goes through trials and that Allah is always merciful and forgiving.
"""
        return prompt

    def _parse_ai_wellness_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the AI response to extract structured data.
        """
        try:
            # Initialize result structure
            result = {
                "themes": [],
                "analysis": "",
                "spiritual_guidance": "",
                "recommendations": []
            }
            
            # Split response into sections
            sections = response.split('\n\n')
            current_section = None
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                    
                if section.startswith('THEMES:'):
                    themes_text = section.replace('THEMES:', '').strip()
                    result["themes"] = [theme.strip() for theme in themes_text.split(',') if theme.strip()]
                    
                elif section.startswith('ANALYSIS:'):
                    result["analysis"] = section.replace('ANALYSIS:', '').strip()
                    
                elif section.startswith('SPIRITUAL_GUIDANCE:'):
                    result["spiritual_guidance"] = section.replace('SPIRITUAL_GUIDANCE:', '').strip()
                    
                elif section.startswith('RECOMMENDATIONS:'):
                    recs_text = section.replace('RECOMMENDATIONS:', '').strip()
                    # Extract recommendations (lines starting with -)
                    recs = [line.strip().lstrip('- ') for line in recs_text.split('\n') if line.strip().startswith('-')]
                    result["recommendations"] = recs
            
            return result
            
        except Exception as e:
            # Fallback: return raw response if parsing fails
            return {
                "themes": ["spiritual_growth", "inner_peace"],
                "analysis": response,
                "spiritual_guidance": "Continue your spiritual journey with patience and trust in Allah.",
                "recommendations": ["Maintain regular prayers", "Practice gratitude daily", "Seek knowledge", "Connect with community"]
            }

    def _find_verses_for_themes(self, themes: List[str], max_verses_per_theme: int = 2) -> List[Dict[str, Any]]:
        """
        Find relevant Quranic verses for the identified themes using semantic search.
        """
        try:
            if not themes:
                return []
            
            verse_recommendations = []
            
            for theme in themes[:3]:  # Limit to top 3 themes
                # Create search query for the theme
                search_query = f"Islamic {theme} spiritual guidance wellness"
                
                # Use existing verse search functionality
                theme_verses = self._find_wellness_verses(search_query, [], max_verses_per_theme)
                
                for verse in theme_verses:
                    verse_recommendations.append({
                        "theme": theme,
                        "verse": verse,
                        "relevance": "high"
                    })
            
            return verse_recommendations[:6]  # Limit total verses
            
        except Exception as e:
            print(f"Error finding verses for themes: {str(e)}")
            return []

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
        """Analyze wellness check-in data comprehensively."""
        try:
            # Extract check-in data
            mood = data.get("mood", "")
            energy_level = data.get("energy_level", 5)
            stress_level = data.get("stress_level", 5)
            notes = data.get("notes", "")
            
            # Analyze mood patterns
            mood_analysis = self._analyze_mood(mood)
            
            # Analyze energy levels
            energy_analysis = self._analyze_energy_level(energy_level)
            
            # Analyze stress levels
            stress_analysis = self._analyze_stress_level(stress_level)
            
            # Detect wellness categories from notes and mood
            detected_categories = []
            if notes:
                detected_categories = self._detect_wellness_categories(notes)
            
            # Generate overall wellness score (1-10 scale)
            wellness_score = self._calculate_wellness_score(energy_level, stress_level, mood_analysis)
            
            # Determine spiritual wellness based on overall state
            spiritual_wellness = self._assess_spiritual_wellness(wellness_score, mood_analysis, stress_analysis)
            
            # Generate personalized recommendations
            recommendations = self._get_personalized_recommendations(mood_analysis, energy_analysis, stress_analysis)
            
            # Generate Quranic guidance based on wellness patterns
            spiritual_guidance = self._generate_pattern_based_guidance(
                mood_analysis, energy_analysis, stress_analysis, detected_categories
            )
            
            # Create comprehensive analysis
            analysis = {
                "wellness_score": wellness_score,
                "mood_analysis": mood_analysis,
                "energy_analysis": energy_analysis,
                "stress_analysis": stress_analysis,
                "spiritual_wellness": spiritual_wellness,
                "detected_categories": detected_categories[:2],  # Top 2 categories
                "spiritual_guidance": spiritual_guidance,
                "recommendations": recommendations
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