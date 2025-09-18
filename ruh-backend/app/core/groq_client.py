import os
import logging
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

class GroqClient:
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GroqClient, cls).__new__(cls)
            cls._instance._initialize_client()
        return cls._instance
    
    def _initialize_client(self):
        """Initialize the Groq client with API key from environment variables"""
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        try:
            self._client = Groq(api_key=api_key)
            logging.info("Groq client initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Groq client: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_response(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """
        Generate a response using Groq API with retry logic
        
        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum tokens to generate
            temperature: Creativity temperature (0.0 to 1.0)
        
        Returns:
            Generated text response
        """
        try:
            chat_completion = self._client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",  # Updated to supported model
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logging.error(f"Groq API call failed: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_structured_response(self, prompt: str, response_format: dict = None) -> dict:
        """
        Generate a structured response (JSON format) from Groq
        
        Args:
            prompt: Prompt with instructions for JSON output
            response_format: Optional response format specification
        
        Returns:
            Parsed JSON response or raw text if parsing fails
        """
        try:
            # Add JSON response instructions to prompt
            structured_prompt = f"{prompt}\n\nPlease respond with valid JSON only."
            
            response = self.generate_response(structured_prompt, max_tokens=300, temperature=0.3)
            
            # Try to parse JSON response
            try:
                import json
                return json.loads(response.strip())
            except json.JSONDecodeError:
                logging.warning("Failed to parse JSON response, returning raw text")
                return {"raw_response": response}
                
        except Exception as e:
            logging.error(f"Structured response generation failed: {e}")
            raise

# Global instance
groq_client = GroqClient()