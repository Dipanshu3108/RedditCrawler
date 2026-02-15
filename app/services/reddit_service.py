import requests
from urllib.parse import urlparse, urlunparse
from app.logger import get_logger

logger = get_logger(__name__)

# Reddit's public JSON API requires a descriptive User-Agent
HEADERS = {
    "User-Agent": "reddit-langgraph-mvp/1.0 (LangGraph agentic pipeline; educational use)",
    "Accept": "application/json",
}

REQUEST_TIMEOUT = 15  # seconds


def _to_json_url(reddit_url: str) -> str:
    """
    Converts a Reddit post URL to its JSON API equivalent.

    Example:
        https://www.reddit.com/r/Python/comments/abc123/my_post/
        → https://www.reddit.com/r/Python/comments/abc123/my_post.json
    """
    parsed = urlparse(reddit_url)
    path = parsed.path.rstrip("/") + ".json"
    return urlunparse(parsed._replace(path=path, query="", fragment=""))


def fetch_reddit_post(url: str) -> dict:
    """
    Fetches Reddit post data using the public .json API endpoint.

    Returns:
        dict: The post's 'data' object from the Reddit API response.

    Raises:
        ValueError: If the response structure is unexpected.
        requests.HTTPError: If the HTTP request fails.
    """
    json_url = _to_json_url(url)

    logger.debug("Fetching Reddit JSON URL: %s", json_url)
    response = requests.get(json_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    try:
        response.raise_for_status()
    except Exception:
        logger.exception("Reddit API request failed for url=%s status=%s", json_url, response.status_code if response is not None else None)
        raise

    payload = response.json()

    # Reddit returns a list with [post_listing, comments_listing]
    if not isinstance(payload, list) or len(payload) < 1:
        raise ValueError("Unexpected Reddit API response structure.")

    post_listing = payload[0]
    children = post_listing.get("data", {}).get("children", [])

    if not children:
        raise ValueError("No post data found in Reddit API response.")

    post_data = children[0].get("data", {})

    if not post_data:
        raise ValueError("Post data object is empty.")

    return post_data
