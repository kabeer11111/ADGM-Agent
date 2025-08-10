import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self, api_key=None, model="models/gemini-1.5-flash"):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API key not found.")
        
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(
            model,
            generation_config={
                "temperature": 0.0,
                "max_output_tokens": 1024,
                "stop_sequences": ["\n\n", "###"]
            },
            safety_settings=[
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}
            ]
        )

    def ask(self, prompt: str, context: str = "") -> str:
        try:
            messages = [{
                "role": "user",
                "parts": [prompt + "\n\nContext:\n" + (context or "No additional context.")]
            }]
            response = self.model.generate_content(messages)

            collected_parts = []
            if hasattr(response, "candidates") and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, "content") and getattr(candidate.content, "parts", None):
                        for part in candidate.content.parts:
                            if hasattr(part, "text") and part.text:
                                collected_parts.append(part.text)

            if collected_parts:
                return " ".join(collected_parts).strip()

        except Exception as e:
            print(f"[Gemini Error] {e}")

        return "[No suggestion available]"
