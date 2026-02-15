import os
import requests
from dotenv import load_dotenv
load_dotenv()
from app.logger import get_logger

logger = get_logger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
REQUEST_TIMEOUT = 120  # seconds — local LLMs can be slow on first call


def call_ollama(model: str, system_prompt: str, user_prompt: str) -> str:
    """
    Sends a chat completion request to a locally running Ollama instance.

    Args:
        model:         The Ollama model name (e.g. "llama3.2", "mistral", "gemma2")
        system_prompt: The system-level instruction for the LLM.
        user_prompt:   The user message containing the structured JSON payload.

    Returns:
        str: The LLM's response text.

    Raises:
        requests.HTTPError: If the Ollama API returns an error status.
        ValueError: If the response structure is unexpected.
    """
    endpoint = f"{OLLAMA_BASE_URL}/api/chat"

    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
    }

    logger.debug("Calling Ollama endpoint %s model=%s", endpoint, model)
    response = requests.post(endpoint, json=payload, timeout=REQUEST_TIMEOUT)
    try:
        response.raise_for_status()
    except Exception:
        logger.exception("Ollama API request failed with status %s: %s", response.status_code if response is not None else None, response.text if response is not None else None)
        raise

    data = response.json()

    # Ollama /api/chat response shape: {"message": {"role": "assistant", "content": "..."}}
    message = data.get("message", {})
    content = message.get("content", "")

    if not content:
        logger.error("Ollama returned empty content payload: %s", data)
        raise ValueError(f"Ollama returned an empty response. Full payload: {data}")

    return content.strip()


def list_available_models() -> list[str]:
    """
    Returns a list of model names currently available in the local Ollama instance.
    Useful for debugging and validation.
    """
    endpoint = f"{OLLAMA_BASE_URL}/api/tags"
    logger.debug("Listing available Ollama models from %s", endpoint)
    response = requests.get(endpoint, timeout=10)
    response.raise_for_status()
    data = response.json()
    return [m["name"] for m in data.get("models", [])]
