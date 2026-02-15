from app.state import WorkflowState
from app.services.reddit_service import fetch_reddit_post
from app.logger import get_logger

logger = get_logger(__name__)


def extract_metadata(state: WorkflowState) -> WorkflowState:
    """
    Fetches and extracts post metadata from Reddit.

    Extracts:
    - Post title
    - Upvote count (score)

    Only handles metadata — content parsing is delegated to content_agent.

    Sets:
    - state["title"]
    - state["upvotes"]
    - state["error"] on failure
    """
    try:
        post_data = fetch_reddit_post(state["user_url"])
        title = post_data.get("title", "").strip()
        upvotes = int(post_data.get("score", 0))

        if not title:
            return {**state, "error": "Could not extract post title from Reddit response."}

        return {**state, "title": title, "upvotes": upvotes}

    except Exception as exc:
        logger.exception("Metadata extraction failed for url=%s", state.get("user_url"))
        return {**state, "error": f"Metadata extraction failed: {exc}"}
