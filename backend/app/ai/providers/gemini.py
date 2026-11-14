import os
from google import genai
from google.genai import types

class GeminiProvider:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment variables.")
        
        # Initialize the official Google GenAI client
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

    def generate_response(self, prompt: str, system_instruction: str = None) -> str:
        """Generates a text response using Gemini."""
        config = None
        if system_instruction:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
            )
            
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config,
        )
        return response.text