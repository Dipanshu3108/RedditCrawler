import json
import os
from pathlib import Path
from app.state import WorkflowState
from app.services.ollama_service import call_ollama
from app.logger import get_logger

logger = get_logger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_prompt(filename: str) -> str:
    """Load a prompt template from the prompts directory."""
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def run_llm_analysis(state: WorkflowState) -> WorkflowState:
    """
    Sends the structured JSON payload to the local Ollama LLM.

    Responsibilities:
    - Load system prompt from prompts/system_prompt.txt
    - Inject structured_json into the user prompt template
    - Call Ollama and capture the response

    Design principle:
    - LLM receives normalized structured data — never raw scraped HTML.

    Sets:
    - state["llm_response"]
    - state["error"] on failure
    """
    try:
        system_prompt = _load_prompt("system_prompt.txt")
        user_prompt_template = _load_prompt("user_prompt.txt")

        # Inject structured JSON into user prompt
        json_str = json.dumps(state["structured_json"], indent=2, ensure_ascii=False)
        user_prompt = user_prompt_template.replace("{{STRUCTURED_JSON}}", json_str)

        model = os.getenv("OLLAMA_MODEL_LOCAL", "")
        response = call_ollama(
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.5,
        )

        return {**state, "llm_response": response}

    except Exception as exc:
        logger.exception("LLM analysis failed for title=%s", state.get("title"))
        return {**state, "error": f"LLM analysis failed: {exc}"}
