import json
from app.state import WorkflowState
from app.logger import get_logger

logger = get_logger(__name__)

# Maximum character length for content sent to the LLM
MAX_CONTENT_LENGTH = 4000


def build_structured_json(state: WorkflowState) -> WorkflowState:
    """
    Transforms extracted post data into a standardized JSON structure
    that will be sent to the LLM.

    Rules:
    - No null/empty values allowed
    - Content is truncated if it exceeds MAX_CONTENT_LENGTH
    - Output is serialization-safe (pure Python dict)

    Sets:
    - state["structured_json"]
    - state["error"] on failure
    """
    try:
        title = state.get("title", "").strip()
        content = state.get("content", "").strip()

        if not title:
            return {**state, "error": "Cannot build JSON: title is empty."}

        if not content:
            content = "[No text content available for this post.]"

        # Truncate long content with a clear marker
        if len(content) > MAX_CONTENT_LENGTH:
            content = content[:MAX_CONTENT_LENGTH] + " ... [truncated]"

        payload = {
            "title": title,
            "content": content,
        }

        # Validate serialization before storing
        json.dumps(payload)

        return {**state, "structured_json": payload}

    except Exception as exc:
        logger.exception("JSON structuring failed for state title=%s", state.get("title"))
        return {**state, "error": f"JSON structuring failed: {exc}"}
