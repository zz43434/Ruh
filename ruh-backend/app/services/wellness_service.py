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
            WellnessService._initialized = True
        self.db = db

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
            
            # Create the prompt for Groq with specific instructions to return JSON
            prompt = f"""
            Analyze the following wellness check-in data and provide:
            1. Personalized guidance based on Islamic principles
            2. Specific recommendations for improving wellness
            3. Key themes or patterns identified in the data

            Check-in Data:
            {checkin_summary}

            IMPORTANT: You MUST respond ONLY with a valid JSON object using this exact structure:
            {{
                "guidance": "Detailed personalized guidance based on Islamic principles",
                "recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"],
                "themes": ["Theme 1", "Theme 2", "Theme 3"]
            }}

            Do not include any explanations, markdown formatting, or text outside of the JSON structure.
            """
            
            # Call Groq API
            response = groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Extract and parse the response
            content = response.choices[0].message.content
            
            # Try to extract JSON from the response
            try:
                # Look for JSON pattern in the response
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    json_str = json_match.group(1)
                    analysis_results = json.loads(json_str)
                else:
                    # Fallback if no JSON pattern found
                    analysis_results = {
                        "guidance": content,
                        "recommendations": [],
                        "themes": []
                    }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
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
