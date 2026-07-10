from ..config import settings
from .mock_provider import MockProvider
from .provider import LLMProvider


def get_provider() -> LLMProvider:
    if settings.llm_provider == "groq":
        if not settings.groq_api_key:
            print("[llm] LLM_PROVIDER=groq but GROQ_API_KEY is unset")
            return MockProvider()
        from .groq_provider import GroqProvider

        return GroqProvider()
    return MockProvider()
