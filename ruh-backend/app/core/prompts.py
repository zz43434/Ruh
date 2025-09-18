# This file contains all prompt templates used in the application.

class PromptTemplates:
    def get_sentiment_prompt(self, user_message: str) -> str:
        return f"""
Analyze the sentiment and themes in this message: "{user_message}"

Respond with JSON containing:
{{
    "sentiment": "positive/negative/neutral",
    "themes": ["list", "of", "themes"]
}}
"""
    
    def get_chat_prompt(self, user_message: str, sentiment: str, themes: list, 
                       verse_text: str, surah_name: str, verse_number: int) -> str:
        return f"""
User message: "{user_message}"
Sentiment: {sentiment}
Themes: {', '.join(themes)}

Relevant Quranic verse:
"{verse_text}" - {surah_name}:{verse_number}

Provide a compassionate, supportive response that incorporates Islamic wisdom from this verse. Be empathetic and offer spiritual comfort.
"""

PROMPT_TEMPLATES = PromptTemplates()