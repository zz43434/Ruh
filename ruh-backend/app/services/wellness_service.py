"""
Wellness Analysis Service for providing Quranic guidance on mental health and wellness topics.
Integrates with semantic search to find relevant verses for different wellness categories.
"""

from .verse_service import VerseService
from app.core.groq_client import groq_client
from app.models.database import get_db
from app.models.wellness_progress import WellnessProgress
from sqlalchemy.orm import Session
import json
import re
from datetime import datetime

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
            WellnessService._initialized = True
        self.db = db

    def get_wellness_history(self, user_id, limit=20, offset=0):
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
                    "timestamp": p.timestamp.isoformat() if p.timestamp else None
                }
                for p in progress
            ]

            return {
                "status": "success",
                "user_id": user_id,
                "total_entries": total_entries,
                "wellness_history": progress_list
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }
    
    def process_wellness_checkin(self, mood, energy_level, stress_level, notes="", user_id="default_user"):
        """
        Process a wellness check-in and save it to the database.
        
        Args:
            mood (str): The user's current mood
            energy_level (int): The user's energy level (1-10)
            stress_level (int): The user's stress level (1-10)
            notes (str, optional): Additional notes from the user
            user_id (str, optional): The ID of the user
            
        Returns:
            dict: The saved wellness check-in data with analysis
        """
        try:
            # Create a new wellness progress entry
            wellness_entry = WellnessProgress(
                user_id=user_id,
                mood=mood,
                energy_level=energy_level,
                stress_level=stress_level,
                notes=notes,
                timestamp=datetime.utcnow()
            )
            
            # Add to database and commit
            self.db.add(wellness_entry)
            self.db.commit()
            self.db.refresh(wellness_entry)
            
            # Return the saved data
            return {
                "status": "success",
                "message": "Wellness check-in recorded successfully",
                "data": {
                    "id": wellness_entry.id,
                    "user_id": wellness_entry.user_id,
                    "mood": wellness_entry.mood,
                    "energy_level": wellness_entry.energy_level,
                    "stress_level": wellness_entry.stress_level,
                    "notes": wellness_entry.notes,
                    "timestamp": wellness_entry.timestamp.isoformat()
                }
            }
        except Exception as e:
            # Rollback in case of error
            if self.db:
                self.db.rollback()
            return {
                "status": "error",
                "message": f"Failed to save wellness check-in: {str(e)}"
            }
            
    def analyze_with_groq(self, checkin_data):
        """
        Analyze the checkin data using Groq to provide guidance, recommendations, and themes.

        Args:
            checkin_data (list): The checkin data for a user.

        Returns:
            dict: The analysis results from Groq including guidance, recommendations, and themes.
        """
        try:
            # Format the checkin data for the prompt
            checkin_summary = json.dumps(checkin_data, indent=2)
            
            # System prompt to enforce JSON response
            system_prompt = """IMPORTANT: You MUST respond ONLY with a valid JSON object using this exact structure:
            {{
                "guidance": "Detailed personalized guidance based on Islamic principles",
                "recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"],
                "themes": ["Theme 1", "Theme 2", "Theme 3"]
            }}

            Do not include any explanations, markdown formatting, or text outside of the JSON structure."""
            
            # User prompt with specific instructions
            prompt = f"""
            Analyze the following wellness check-in data and provide:
            1. Personalized guidance based on Islamic principles
            2. Specific recommendations for improving wellness
            3. Key themes or patterns identified in the data

            Check-in Data:
            {checkin_summary}
            """
            
            response = groq_client.generate_response(
                system_prompt=system_prompt,
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3
            )
            
            content = response
            
            try:
                analysis_results = json.loads(content)
            except json.JSONDecodeError:
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    json_str = json_match.group(1)
                    try:
                        analysis_results = json.loads(json_str)
                    except json.JSONDecodeError:
                        analysis_results = {
                            "guidance": content,
                            "recommendations": [],
                            "themes": []
                        }
                else:
                    # Fallback if no JSON pattern found
                    analysis_results = {
                        "guidance": content,
                        "recommendations": [],
                        "themes": []
                    }
                
            return analysis_results
        except Exception as e:
            return {
                "status": "error",
                "message": f"An error occurred during Groq analysis: {str(e)}",
                "guidance": "We couldn't analyze your data at this time. Please try again later.",
                "recommendations": [],
                "themes": []
            }

    def clear_wellness_data(self, user_id: str) -> Dict:
        """Clear all wellness data for a user."""
        try:
            # Get count before deletion for reporting
            count = self.db.query(WellnessProgress).filter_by(user_id=user_id).count()
            
            # Delete all wellness progress entries for the user
            self.db.query(WellnessProgress).filter_by(user_id=user_id).delete()
            self.db.commit()
            
            return {
                "success": True,
                "message": f"Cleared {count} wellness entries for user {user_id}",
                "deleted_entries": count
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to clear wellness data: {str(e)}"
            }

    def clear_all_wellness_data(self) -> Dict:
        """Clear all wellness data for all users (admin function)."""
        try:
            # Get count before deletion for reporting
            count = self.db.query(WellnessProgress).count()
            
            # Delete all wellness progress entries
            self.db.query(WellnessProgress).delete()
            self.db.commit()
            
            return {
                "success": True,
                "message": f"Cleared all {count} wellness entries from the database",
                "deleted_entries": count
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to clear all wellness data: {str(e)}"
            }
