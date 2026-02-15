from langgraph.graph import StateGraph, END

from app.state import WorkflowState
from app.agents.validator import validate_url
from app.agents.metadata_agent import extract_metadata
from app.agents.content_agent import extract_content
from app.agents.json_agent import build_structured_json
from app.agents.llm_agent import run_llm_analysis
from app.agents.story_agent import run_story_writer


def _route_after_validation(state: WorkflowState) -> str:
    if state.get("error") or not state.get("is_valid"):
        return "end"
    return "extract_metadata"


def _route_on_error(next_node: str):
    def _router(state: WorkflowState) -> str:
        return "end" if state.get("error") else next_node
    return _router


def build_workflow() -> StateGraph:
    graph = StateGraph(WorkflowState)

    graph.add_node("validate_url",      validate_url)
    graph.add_node("extract_metadata",  extract_metadata)
    graph.add_node("extract_content",   extract_content)
    graph.add_node("build_json",        build_structured_json)
    graph.add_node("llm_analysis",      run_llm_analysis)
    graph.add_node("story_writer",      run_story_writer)   # ← new node

    graph.set_entry_point("validate_url")

    graph.add_conditional_edges(
        "validate_url",
        _route_after_validation,
        {"extract_metadata": "extract_metadata", "end": END},
    )
    graph.add_conditional_edges(
        "extract_metadata",
        _route_on_error("extract_content"),
        {"extract_content": "extract_content", "end": END},
    )
    graph.add_conditional_edges(
        "extract_content",
        _route_on_error("build_json"),
        {"build_json": "build_json", "end": END},
    )
    graph.add_conditional_edges(
        "build_json",
        _route_on_error("llm_analysis"),
        {"llm_analysis": "llm_analysis", "end": END},
    )
    graph.add_conditional_edges(
        "llm_analysis",
        _route_on_error("story_writer"),
        {"story_writer": "story_writer", "end": END},
    )

    graph.add_edge("story_writer", END)

    return graph.compile()