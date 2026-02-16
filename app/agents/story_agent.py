import os
from pathlib import Path
from app.state import WorkflowState
from app.services.ollama_service import call_ollama

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def run_story_writer(state: WorkflowState) -> WorkflowState:
    """
    Takes the structured JSON and LLM analysis and generates
    a polished, publishable horror short story.

    Requires:
    - state["structured_json"]
    - state["llm_response"]

    Sets:
    - state["story"]
    - state["error"] on failure
    """
    try:
        import json

        system_prompt = _load_prompt("story_system_prompt.txt")
        user_prompt_template = _load_prompt("story_user_prompt.txt")

        json_str = json.dumps(state["structured_json"], indent=2, ensure_ascii=False)
        llm_analysis = state.get("llm_response", "No analysis available.")

        user_prompt = (
            user_prompt_template
            .replace("{{STRUCTURED_JSON}}", json_str)
            .replace("{{LLM_ANALYSIS}}", llm_analysis)
        )

        model = os.getenv("OLLAMA_MODEL_CLOUD", "glm-5:cloud")
        api_key = os.getenv("OLLAMA_API_KEY", "")
        story = call_ollama(
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            api_key=api_key or None,
            temperature=0.7,
        )

        return {**state, "story": story}

    except Exception as exc:
        return {**state, "error": f"Story writer failed: {exc}"}