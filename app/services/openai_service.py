"""
OpenAI service for AI-powered features.
"""
from typing import Optional
from openai import OpenAI


class OpenAIService:
    """Service class for OpenAI API operations."""

    BEHAVIORAL_SYSTEM_PROMPT = """You are an expert behavioral interview coach specializing in Amazon's Leadership Principles. Your role is to evaluate behavioral stories and provide constructive feedback.

CRITICAL RULES:
1. The candidate should NEVER use "we" in their stories - they must use "I" to show personal ownership and impact
2. Stories should follow the STAR method (Situation, Task, Action, Result)
3. Focus on specific, measurable results and personal contributions
4. Look for leadership principles demonstration

Provide feedback in this format:
- Score: X/10
- Strengths: (2-3 key strengths)
- Areas for Improvement: (2-3 specific suggestions)
- Leadership Principles Demonstrated: (which Amazon LP this shows)
- Suggested Improvements: (specific suggestions to make the story stronger)

Be constructive but direct. Focus on making the story more compelling and interview-ready."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI service."""
        self.api_key = api_key
        self._client = None

    @property
    def client(self) -> OpenAI:
        """Get OpenAI client, creating if necessary."""
        if self._client is None:
            if not self.api_key:
                raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.")
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def is_configured(self) -> bool:
        """Check if OpenAI is properly configured."""
        return bool(self.api_key)

    def get_behavioral_feedback(self, question: str, story: str) -> str:
        """Get AI feedback on a behavioral interview story."""
        user_prompt = f"""Question: {question}

Candidate's Story: {story}

Please evaluate this behavioral story and provide detailed feedback."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.BEHAVIORAL_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        return response.choices[0].message.content
