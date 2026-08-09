import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class GeminiService:
    """Unified LLM client using Groq API (free tier available)."""

    def __init__(self) -> None:
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key or "unsupported")

    def generate_response(self, prompt: str) -> str:
        """Send a prompt to Groq and return the generated text."""
        if not self.api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Get a free key at https://console.groq.com/keys "
                "and set it in the .env file."
            )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=500,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            raise RuntimeError(f"LLM API error: {exc}") from exc
