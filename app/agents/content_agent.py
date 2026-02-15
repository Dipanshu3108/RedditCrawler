import re
from app.state import WorkflowState
from app.services.reddit_service import fetch_reddit_post
from app.logger import get_logger

logger = get_logger(__name__)


def _clean_text(raw: str) -> str:
    """
    Removes HTML entities, Markdown artifacts, and normalizes whitespace.
    """
    # Decode common HTML entities
    html_entities = {
        "&amp;": "&", "&lt;": "<", "&gt;": ">",
        "&quot;": '"', "&#39;": "'", "&nbsp;": " ",
    }
    for entity, char in html_entities.items():
        raw = raw.replace(entity, char)

    # Strip Markdown links: [text](url) → text
    raw = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw)

    # Strip standalone URLs
    raw = re.sub(r"https?://\S+", "", raw)

    # Remove bold/italic markers
    raw = re.sub(r"(\*{1,3}|_{1,3})(.*?)\1", r"\2", raw)

    # Normalize whitespace and newlines
    raw = re.sub(r"\r\n|\r", "\n", raw)
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    raw = raw.strip()

    return raw


def extract_content(state: WorkflowState) -> WorkflowState:
    """
    Retrieves and cleans the main post body text.

    Tasks:
    - Extract selftext content from the Reddit post
    - Remove HTML/Markdown artifacts
    - Normalize spacing

    MVP scope:
    - Ignores comments
    - Ignores media attachments

    Sets:
    - state["content"]
    - state["error"] on failure
    """
    try:
        post_data = fetch_reddit_post(state["user_url"])
        raw_content = post_data.get("selftext", "")

        # Link posts have no selftext body
        if not raw_content or raw_content in ("[removed]", "[deleted]"):
            # Fall back to the post URL hint so the LLM still has context
            raw_content = f"[Link post — no text body. Post URL: {post_data.get('url', '')}]"

        cleaned = _clean_text(raw_content)
        return {**state, "content": cleaned}

    except Exception as exc:
        logger.exception("Content extraction failed for url=%s", state.get("user_url"))
        return {**state, "error": f"Content extraction failed: {exc}"}
