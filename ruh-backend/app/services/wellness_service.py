from app.models.database import get_db
from app.models.wellness_progress import WellnessProgress
from sqlalchemy.orm import Session

class WellnessService:
    def __init__(self, db: Session):
        self.db = db

    def get_wellness_tips(self):
        """
        Retrieve wellness tips.

        Returns:
            list: A list of wellness tips.
        """
        return [
            "Stay hydrated.",
            "Exercise regularly.",
            "Get enough sleep.",
            "Practice mindfulness."
        ]

    def analyze_wellness_data(self, data):
        """
        Analyze wellness data.

        Args:
            data (dict): The wellness data to analyze.

        Returns:
            dict: Analysis results.
        """
        try:
            # Example analysis logic
            analysis = {
                "stress_level": "low" if data.get("stress") < 5 else "high",
                "activity_score": data.get("steps", 0) * 0.1
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