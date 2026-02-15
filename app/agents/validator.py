import re
from app.state import WorkflowState
from app.logger import get_logger

logger = get_logger(__name__)

# Pattern: https://www.reddit.com/r/<subreddit>/comments/<post_id>/<slug>/
REDDIT_POST_PATTERN = re.compile(
    r"^https?://(www\.)?reddit\.com/r/[^/]+/comments/[a-z0-9]+(/[^/]*)?/?$",
    re.IGNORECASE,
)


def validate_url(state: WorkflowState) -> WorkflowState:
    """
    Validates the user-provided URL.

    Checks:
    - URL is non-empty
    - URL belongs to reddit.com
    - URL matches a post structure (not a profile, subreddit listing, or home page)

    Sets:
    - state["is_valid"]
    - state["error"] on failure
    """
    url = state.get("user_url", "").strip()

    if not url:
        logger.warning("Validation failed: no URL provided")
        return {**state, "is_valid": False, "error": "No URL provided."}

    if not REDDIT_POST_PATTERN.match(url):
        return {
            **state,
            "is_valid": False,
            "error": (
                f"Invalid Reddit post URL: '{url}'. "
                "Expected format: https://www.reddit.com/r/<subreddit>/comments/<id>/<slug>/"
            ),
        }

    return {**state, "is_valid": True}
