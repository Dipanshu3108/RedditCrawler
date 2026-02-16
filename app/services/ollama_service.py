import os
import requests
from dotenv import load_dotenv
load_dotenv()
from app.logger import get_logger

logger = get_logger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_CLOUD_BASE_URL = os.getenv("OLLAMA_CLOUD_BASE_URL", "https://ollama.com")
REQUEST_TIMEOUT = 300  # seconds — cloud APIs can be slower than local LLMs


# def call_ollama(model: str, system_prompt: str, user_prompt: str) -> str:
    # """
    # Sends a chat completion request to a locally running Ollama instance.

    # Args:
    #     model:         The Ollama model name (e.g. "llama3.2", "mistral", "gemma2")
    #     system_prompt: The system-level instruction for the LLM.
    #     user_prompt:   The user message containing the structured JSON payload.

    # Returns:
    #     str: The LLM's response text.

    # Raises:
    #     requests.HTTPError: If the Ollama API returns an error status.
    #     ValueError: If the response structure is unexpected.
    # """
    # endpoint = f"{OLLAMA_BASE_URL}/api/chat"

    # payload = {
    #     "model": model,
    #     "stream": False,
    #     "messages": [
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user",   "content": user_prompt},
    #     ],
    # }
def call_ollama(
    model: str,
    system_prompt: str,
    user_prompt: str,
    api_key: str | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    top_k: int | None = None,
    min_p: float | None = None,
    typical_p: float | None = None,
    tfs_z: float | None = None,
    repeat_last_n: int | None = None,
    repeat_penalty: float | None = None,
    presence_penalty: float | None = None,
    frequency_penalty: float | None = None,
    mirostat: int | None = None,
    mirostat_tau: float | None = None,
    mirostat_eta: float | None = None,
    num_predict: int | None = None,
    seed: int | None = None,
    stop: list[str] | None = None,
    num_ctx: int | None = None,
    num_batch: int | None = None,
    num_thread: int | None = None,
    num_gpu: int | None = None,
    penalize_newline: bool | None = None,
) -> str:
    """
    Sends a chat completion request to a locally running Ollama instance.

    Args:
        model:         The Ollama model name (e.g. "llama3.2", "mistral", "gemma2")
        system_prompt: The system-level instruction for the LLM.
        user_prompt:   The user message containing the structured JSON payload.
        temperature:   Sampling temperature (0.0–1.0).
        top_p, top_k, min_p, typical_p, tfs_z: Sampling controls.
        repeat_last_n, repeat_penalty, presence_penalty, frequency_penalty: Repetition controls.
        mirostat, mirostat_tau, mirostat_eta: Mirostat controls.
        num_predict:   Max tokens to predict.
        seed:          RNG seed.
        stop:          Stop sequences.
        num_ctx:       Context size.
        num_batch:     Batch size.
        num_thread:    CPU threads.
        num_gpu:       GPU layers.
        penalize_newline: Penalize newlines.
    """
    base_url = OLLAMA_CLOUD_BASE_URL if api_key else OLLAMA_BASE_URL
    endpoint = f"{base_url}/api/chat"

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    options = {
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "min_p": min_p,
        "typical_p": typical_p,
        "tfs_z": tfs_z,
        "repeat_last_n": repeat_last_n,
        "repeat_penalty": repeat_penalty,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
        "mirostat": mirostat,
        "mirostat_tau": mirostat_tau,
        "mirostat_eta": mirostat_eta,
        "num_predict": num_predict,
        "seed": seed,
        "stop": stop,
        "num_ctx": num_ctx,
        "num_batch": num_batch,
        "num_thread": num_thread,
        "num_gpu": num_gpu,
        "penalize_newline": penalize_newline,
    }
    options = {k: v for k, v in options.items() if v is not None}

    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
    }

    if options:
        payload["options"] = options

    logger.debug("Calling Ollama endpoint %s model=%s", endpoint, model)
    response = requests.post(
        endpoint,
        json=payload,
        headers=headers if headers else None,
        timeout=REQUEST_TIMEOUT,
    )
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
