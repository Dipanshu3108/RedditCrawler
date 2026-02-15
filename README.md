# Reddit LangGraph MVP — Agentic Post Analysis Pipeline

A minimal agentic workflow built with **LangGraph** that accepts a Reddit post URL,
extracts metadata and content, structures it as JSON, and sends it to a **local LLM via Ollama** for analysis.

---

## Architecture

```
User Input
    ↓
URL Validation
    ↓
Metadata Extraction   (title, upvotes)
    ↓
Content Extraction    (cleaned post body)
    ↓
JSON Structuring      (normalized payload)
    ↓
LLM Analysis          (Ollama local model)
    ↓
Final Output
```

Each stage is an independent agent node in a LangGraph `StateGraph`. Errors at any stage
short-circuit execution and route directly to `END`.

---

## Project Structure

```
reddit-langgraph-mvp/
├── app/
│   ├── main.py              # CLI entry point
│   ├── workflow.py          # LangGraph graph definition
│   ├── state.py             # Shared WorkflowState TypedDict
│   ├── agents/
│   │   ├── validator.py     # URL validation
│   │   ├── metadata_agent.py  # Title & upvote extraction
│   │   ├── content_agent.py   # Post body extraction & cleaning
│   │   ├── json_agent.py      # Structured JSON assembly
│   │   └── llm_agent.py       # Ollama LLM call
│   ├── services/
│   │   ├── reddit_service.py  # Reddit public JSON API client
│   │   └── ollama_service.py  # Ollama REST API client
│   └── prompts/
│       ├── system_prompt.txt  # LLM system instruction
│       └── user_prompt.txt    # User message template
├── requirements.txt
└── README.md
```

---

## Prerequisites

### 1. Python 3.10+

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Ollama running locally

Install Ollama from https://ollama.com and pull a model:

```bash
# Install a model (choose one)
ollama pull llama3.2
ollama pull mistral
ollama pull gemma2

# Ensure Ollama is running
ollama serve
```

---

## Usage

### Interactive (prompts for URL)

```bash
python -m app.main
```

### Pass URL directly

```bash
python -m app.main --url "https://www.reddit.com/r/Python/comments/abc123/my_post/"
```

### Output as raw JSON

```bash
python -m app.main --url "https://www.reddit.com/r/..." --json
```

---

## Configuration

| Environment Variable | Default                   | Description                        |
|----------------------|---------------------------|------------------------------------|
| `OLLAMA_MODEL`       | `llama3.2`                | Ollama model to use for analysis   |
| `OLLAMA_BASE_URL`    | `http://localhost:11434`  | Ollama server base URL             |

Set via shell:

```bash
export OLLAMA_MODEL=mistral
python -m app.main --url "https://..."
```

---

## Customising Prompts

Edit the files in `app/prompts/` to change LLM behaviour:

- **`system_prompt.txt`** — High-level instructions for the LLM role and output format.
- **`user_prompt.txt`** — Message sent with the structured JSON. Use `{{STRUCTURED_JSON}}` as the injection placeholder.

---

## Shared State Fields

| Field             | Type    | Set by            |
|-------------------|---------|-------------------|
| `user_url`        | `str`   | Input stage       |
| `is_valid`        | `bool`  | validator         |
| `title`           | `str`   | metadata_agent    |
| `upvotes`         | `int`   | metadata_agent    |
| `content`         | `str`   | content_agent     |
| `structured_json` | `dict`  | json_agent        |
| `llm_response`    | `str`   | llm_agent         |
| `error`           | `str?`  | Any agent         |

---

## MVP Constraints

- Single Reddit post only (no batch processing)
- No Reddit authentication (public posts only via `.json` API)
- No comment scraping
- Single LLM call per run
- Sequential node execution

---

## Extending the Pipeline

- **Add comment scraping**: Create a `comments_agent.py` and inject comments into `structured_json`
- **Multiple LLM calls**: Fan out from `build_json` to parallel analysis nodes
- **Streaming output**: Switch `stream: False` to `stream: True` in `ollama_service.py`
- **Web UI**: Wrap `run_pipeline()` in a FastAPI endpoint
