"""
LLM Service - Groq API client.

Handles all communication with the LLM (Groq / OpenAI compatible).
"""

import json
from typing import Optional

from groq import Groq

from app.core.config import settings


class LLMService:
    """Service to interact with LLM provider (Groq)."""

    def __init__(self):
        """Initialize the LLM client."""
        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not set. Please add it to your .env file."
            )

        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.LLM_MODEL
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Send a chat completion request to the LLM.

        Args:
            system_prompt: The system message (role/instructions).
            user_prompt: The user message (actual query).
            temperature: Optional override for temperature.

        Returns:
            The LLM's response as a string.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=self.max_tokens,
        )

        return response.choices[0].message.content

    def chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
    ) -> dict:
        """
        Send a request and parse the response as JSON.

        Args:
            system_prompt: The system message.
            user_prompt: The user message.
            temperature: Optional override.

        Returns:
            Parsed JSON response as dict/list.
        """
        raw = self.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
        )

        # Clean markdown code blocks if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            # Remove ```json ... ``` wrapper
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()

        return json.loads(cleaned)


# Singleton instance
llm_service = LLMService()
