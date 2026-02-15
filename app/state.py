from typing import Optional
from typing_extensions import TypedDict


class WorkflowState(TypedDict):
    """Shared state passed between all LangGraph nodes."""
    user_url: str
    is_valid: bool
    title: str
    upvotes: int
    content: str
    structured_json: dict
    llm_response: str
    story: str          # ← new field
    error: Optional[str]


def initial_state(url: str) -> WorkflowState:
    return WorkflowState(
        user_url=url,
        is_valid=False,
        title="",
        upvotes=0,
        content="",
        structured_json={},
        llm_response="",
        story="",        # ← new field
        error=None,
    )