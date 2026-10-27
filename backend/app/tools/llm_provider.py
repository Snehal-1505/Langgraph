import logging
import httpx
from typing import Optional, Dict, Any, Type
from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings

logger = logging.getLogger(__name__)


def check_ollama_status(base_url: str = settings.OLLAMA_BASE_URL) -> Dict[str, Any]:
    """Check whether local Ollama service is reachable and list installed models."""
    try:
        with httpx.Client(timeout=3.0) as client:
            resp = client.get(f"{base_url.rstrip('/')}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name") for m in data.get("models", [])]
                return {
                    "status": "ready",
                    "reachable": True,
                    "models": models,
                    "message": f"Ollama is online with {len(models)} model(s)."
                }
            return {
                "status": "unreachable",
                "reachable": False,
                "models": [],
                "message": f"Ollama returned HTTP status {resp.status_code}"
            }
    except Exception as e:
        return {
            "status": "unreachable",
            "reachable": False,
            "models": [],
            "message": f"Cannot connect to Ollama at {base_url}. Ensure Ollama is installed and running."
        }


class MockChatModel(BaseChatModel):
    """Deterministic mock chat model for unit tests and offline environments."""
    
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        from langchain_core.outputs import ChatResult, ChatGeneration
        from langchain_core.messages import AIMessage
        
        last_msg = messages[-1].content if messages else ""
        content = (
            "Mock LLM Response: Research synthesis completed successfully based on provided facts. "
            "Evidence supports the productivity and efficiency claims with documented limitations."
        )
        message = AIMessage(content=content)
        return ChatResult(generations=[ChatGeneration(message=message)])

    @property
    def _llm_type(self) -> str:
        return "mock"

    def with_structured_output(self, schema: Type[BaseModel], **kwargs):
        """Mock structured output generator returning instance of schema."""
        class StructuredMockWrapper:
            def __init__(self, target_schema):
                self.target_schema = target_schema

            async def ainvoke(self, input_val, **invoke_kwargs):
                return self.invoke(input_val, **invoke_kwargs)

            def invoke(self, input_val, **invoke_kwargs):
                # Construct sensible default instance based on schema field definitions
                fields = self.target_schema.model_fields
                data = {}
                for name, field in fields.items():
                    annotation = field.annotation
                    if annotation == str:
                        data[name] = f"Sample validated output for {name}"
                    elif annotation == int:
                        data[name] = 1
                    elif annotation == bool:
                        data[name] = True
                    elif getattr(annotation, "__origin__", None) is list:
                        data[name] = []
                    elif getattr(annotation, "__origin__", None) is dict:
                        data[name] = {}
                    else:
                        data[name] = None
                return self.target_schema.model_validate(data)

        return StructuredMockWrapper(schema)


def get_llm(temperature: float = 0.2) -> BaseChatModel:
    """
    Factory function to instantiate the configured LLM provider.
    Defaults to local Ollama.
    """
    provider = settings.LLM_PROVIDER.lower()

    if provider == "mock":
        return MockChatModel()

    if provider == "gemini":
        if not settings.GEMINI_API_KEY:
            logger.warning("Gemini API key is not configured. Falling back to mock model.")
            return MockChatModel()
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=temperature,
            timeout=settings.REQUEST_TIMEOUT_SECONDS
        )

    if provider == "groq":
        if not settings.GROQ_API_KEY:
            logger.warning("Groq API key is not configured. Falling back to mock model.")
            return MockChatModel()
        from langchain_groq import ChatGroq
        return ChatGroq(
            model_name=settings.GROQ_MODEL,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=temperature,
            timeout=settings.REQUEST_TIMEOUT_SECONDS
        )

    # Default to Ollama
    try:
        from langchain_ollama import ChatOllama
        return ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=temperature,
            timeout=settings.REQUEST_TIMEOUT_SECONDS
        )
    except Exception as e:
        logger.error(f"Failed to initialize ChatOllama: {e}. Falling back to mock provider.")
        return MockChatModel()
