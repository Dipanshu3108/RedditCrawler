#!/usr/bin/env python3
"""
Reddit LangGraph MVP — Entry Point

Usage:
    python -m app.main
    python -m app.main --url "https://www.reddit.com/r/Python/comments/abc123/my_post/"

Environment variables:
    OLLAMA_MODEL     Ollama model to use (default: llama3.2)
    OLLAMA_BASE_URL  Ollama server URL   (default: http://localhost:11434)
"""

import argparse
import json
import sys
from app.logger import get_logger

logger = get_logger(__name__)

from app.state import initial_state
from app.workflow import build_workflow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reddit LangGraph MVP — Agentic post analysis pipeline"
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Reddit post URL to analyse (will prompt interactively if not provided)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output the full result as JSON instead of formatted text",
    )
    return parser.parse_args()


def run_pipeline(url: str) -> dict:
    """Execute the full LangGraph pipeline for a given URL."""
    state = initial_state(url)
    app = build_workflow()
    result = app.invoke(state)
    return result


def pretty_print(result: dict) -> None:
    print("\n" + "=" * 60)
    print("  REDDIT LANGGRAPH MVP — ANALYSIS RESULT")
    print("=" * 60)

    if result.get("error"):
        print(f"\n❌  Pipeline failed: {result['error']}")
        return

    print(f"\n📌  Title   : {result.get('title', 'N/A')}")
    print(f"⬆️   Upvotes : {result.get('upvotes', 0):,}")

    print("\n── Structured JSON Payload ──────────────────────────────")
    print(json.dumps(result.get("structured_json", {}), indent=2, ensure_ascii=False))

    print("\n── LLM Analysis ─────────────────────────────────────────")
    print(result.get("llm_response", "No response."))

    print("\n── Generated Story ──────────────────────────────────────")
    print(result.get("story", "No story generated."))

    print("=" * 60 + "\n")


def main() -> int:
    args = parse_args()

    url = args.url
    if not url:
        url = input("Enter a Reddit post URL: ").strip()

    if not url:
        logger.error("No URL provided by user")
        return 1
    logger.info("Running pipeline for: %s", url)
    result = run_pipeline(url)

    if args.output_json:
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        pretty_print(result)

    return 0 if not result.get("error") else 1


if __name__ == "__main__":
    sys.exit(main())
