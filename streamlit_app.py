import streamlit as st
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="RedditStory — AI Story Pipeline",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:ital,wght@0,400;0,700;1,400&family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');

  /* ── Base reset ── */
  :root {
    --bg:        #0a0a0c;
    --surface:   #111116;
    --surface2:  #1a1a22;
    --border:    #2a2a38;
    --red:       #FF5F1F; /* primary orange accent */
    --red-dim:   #7a1e26;
    --amber:     #FF5F1F; /* keep amber aligned to orange */
    --green:     #39FF14; /* neon green */
    --muted:     #5a5a7a;
    --text:      #ffffff; /* primary UI text now white */
    --text-dim:  #bfc7c0;
    --mono:      'Courier Prime', monospace;
    --sans:      'DM Sans', sans-serif;
    --display:   'Bebas Neue', sans-serif;
    --glow-green: rgba(57, 255, 20, 0.20);
    --glow-orange: rgba(255, 95, 31, 0.16);
  }

  html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
  }

  [data-testid="stHeader"] { background: transparent !important; }
  [data-testid="stSidebar"] { background: var(--surface) !important; }
  [data-testid="stToolbar"] { display: none; }

  /* ── Typography ── */
  h1, h2, h3 { font-family: var(--display) !important; letter-spacing: 0.08em; }

  /* ── Main container ── */
  .block-container {
    padding: 2rem 3rem !important;
    max-width: 1100px !important;
  }

  /* ── Header ── */
  .app-header {
    border-bottom: 1px solid var(--border);
    padding-bottom: 1.5rem;
    margin-bottom: 2rem;
  }
  .app-title {
    font-family: var(--display);
    font-size: 3.8rem;
    letter-spacing: 0.1em;
    color: var(--green);
    line-height: 1;
    margin: 0;
    text-shadow: 0 0 12px var(--glow-green);
  }
  .app-subtitle {
    font-family: var(--mono);
    font-size: 0.75rem;
    color: var(--muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.4rem;
  }

  /* ── Input area ── */
  .stTextInput > div > div > input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s;
  }
  .stTextInput > div > div > input:focus {
    border-color: var(--red) !important;
    box-shadow: 0 0 10px var(--glow-orange) !important;
  }
  .stTextInput > label {
    font-family: var(--mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
  }

  /* ── Buttons ── */
  .stButton > button {
    background: var(--amber) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: var(--display) !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.15em !important;
    padding: 0.6rem 2rem !important;
    transition: background 0.2s, transform 0.1s !important;
    width: 100% !important;
    box-shadow: 0 8px 24px var(--glow-orange);
  }
  .stButton > button:hover {
    background: #e04f1a !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 12px 32px var(--glow-orange);
  }
  .stButton > button:active { transform: translateY(0) !important; }

  /* ── Pipeline stage cards ── */
  .stage-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--muted);
    border-radius: 4px;
    padding: 0.75rem 1rem;
    margin: 0.35rem 0;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-family: var(--mono);
    font-size: 0.82rem;
    color: var(--text-dim);
    transition: all 0.3s;
  }
  .stage-card.running {
    border-left-color: var(--amber);
    color: var(--amber);
    background: rgba(255, 95, 31, 0.04);
    text-shadow: 0 0 8px var(--glow-orange);
  }
  .stage-card.done {
    border-left-color: var(--green);
    color: var(--text);
    background: rgba(57, 255, 20, 0.03);
    text-shadow: 0 0 8px var(--glow-green);
  }
  .stage-card.error {
    border-left-color: var(--red);
    color: var(--red);
    background: rgba(255, 95, 31, 0.06);
    text-shadow: 0 0 6px var(--glow-orange);
  }
  .stage-icon { font-size: 1rem; min-width: 1.2rem; text-align: center; }
  .stage-label { flex: 1; }
  .stage-time {
    font-size: 0.7rem;
    color: var(--muted);
    font-family: var(--mono);
  }

  /* ── Result panels ── */
  .result-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.5rem;
    margin-top: 0.75rem;
  }
  .panel-label {
    font-family: var(--mono);
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .panel-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
  }

  /* ── Meta row ── */
  .meta-row {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 1rem;
  }
  .meta-chip {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 0.3rem 0.75rem;
    font-family: var(--mono);
    font-size: 0.8rem;
    color: var(--text-dim);
  }
  .meta-chip span { color: var(--text); font-weight: 700; }

  /* ── Story output ── */
  .story-output {
    font-family: 'Courier Prime', monospace;
    font-size: 0.95rem;
    line-height: 1.85;
    color: var(--text);
    white-space: pre-wrap;
    word-break: break-word;
  }

  /* ── Analysis output ── */
  .analysis-output {
    font-family: var(--sans);
    font-size: 0.9rem;
    line-height: 1.7;
    color: var(--text-dim);
  }
  .analysis-output strong { color: var(--text); }

  /* ── JSON block ── */
  .json-block {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1rem;
    font-family: var(--mono);
    font-size: 0.8rem;
    color: #a8d8a8;
    white-space: pre-wrap;
    overflow-x: auto;
    line-height: 1.6;
  }

  /* ── Error box ── */
  .error-box {
    background: rgba(230, 57, 70, 0.08);
    border: 1px solid var(--red-dim);
    border-radius: 4px;
    padding: 1rem 1.25rem;
    font-family: var(--mono);
    font-size: 0.85rem;
    color: var(--red);
  }

  /* ── Copy button helper ── */
  .stDownloadButton > button {
    background: var(--surface2) !important;
    color: var(--text-dim) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    font-family: var(--mono) !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    padding: 0.4rem 1rem !important;
    width: auto !important;
  }
  .stDownloadButton > button:hover {
    border-color: var(--muted) !important;
    color: var(--text) !important;
    background: var(--surface) !important;
  }

  /* ── Divider ── */
  hr { border-color: var(--border) !important; margin: 2rem 0 !important; }

  /* ── Spinner override ── */
  .stSpinner > div { border-top-color: var(--red) !important; }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

  /* ── Hide Streamlit chrome ── */
  #MainMenu { display: none; }
  footer { display: none; }
</style>
""", unsafe_allow_html=True)


# ── Helper renderers ───────────────────────────────────────────────────────────

def render_header():
    st.markdown("""
    <div class="app-header">
      <p class="app-title">REDDIT STORY</p>
      <p class="app-subtitle">▸ LangGraph · Ollama · AI Story Pipeline</p>
    </div>
    """, unsafe_allow_html=True)


def stage_html(icon, label, status="pending", elapsed=None):
    time_str = f'<span class="stage-time">{elapsed:.1f}s</span>' if elapsed else ""
    return f"""
    <div class="stage-card {status}">
      <span class="stage-icon">{icon}</span>
      <span class="stage-label">{label}</span>
      {time_str}
    </div>"""


def render_pipeline_stages(stages: list):
    html = "".join(stage_html(*s) for s in stages)
    st.markdown(html, unsafe_allow_html=True)


def run_pipeline_with_progress(url: str):
    """Run the full pipeline, updating a progress display after each node."""
    from app.state import initial_state
    from app.agents.validator import validate_url
    from app.agents.metadata_agent import extract_metadata
    from app.agents.content_agent import extract_content
    from app.agents.json_agent import build_structured_json
    from app.agents.llm_agent import run_llm_analysis
    from app.agents.story_agent import run_story_writer

    STEPS = [
        ("🔗", "URL Validation"),
        ("📡", "Metadata Extraction"),
        ("📄", "Content Extraction"),
        ("🗂️",  "JSON Structuring"),
        ("🤖", "LLM Analysis"),
        ("✍️",  "Story Writer"),
    ]

    # Build mutable stage list: (icon, label, status, elapsed)
    stages = [(icon, label, "pending", None) for icon, label in STEPS]
    placeholder = st.empty()

    def refresh(idx, status, elapsed=None):
        stages[idx] = (STEPS[idx][0], STEPS[idx][1], status, elapsed)
        with placeholder.container():
            render_pipeline_stages(stages)

    def run_step(idx, fn, state):
        refresh(idx, "running")
        t0 = time.perf_counter()
        result = fn(state)
        elapsed = time.perf_counter() - t0
        if result.get("error"):
            refresh(idx, "error", elapsed)
        else:
            refresh(idx, "done", elapsed)
        return result

    state = initial_state(url)

    # Step 0 — Validate
    state = run_step(0, validate_url, state)
    if state.get("error") or not state.get("is_valid"):
        return state

    # Step 1 — Metadata
    state = run_step(1, extract_metadata, state)
    if state.get("error"):
        return state

    # Step 2 — Content
    state = run_step(2, extract_content, state)
    if state.get("error"):
        return state

    # Step 3 — JSON
    state = run_step(3, build_structured_json, state)
    if state.get("error"):
        return state

    # Step 4 — LLM Analysis
    state = run_step(4, run_llm_analysis, state)
    if state.get("error"):
        return state

    # Step 5 — Story
    state = run_step(5, run_story_writer, state)
    return state


def render_results(result: dict):
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Meta row ──────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="meta-row">
      <div class="meta-chip">TITLE &nbsp; <span>{result.get('title', '—')}</span></div>
      <div class="meta-chip">UPVOTES &nbsp; <span>{result.get('upvotes', 0):,}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_story, tab_analysis, tab_json = st.tabs(["✍️  Story", "🤖  Analysis", "🗂️  JSON Payload"])

    with tab_story:
        story = result.get("story", "")
        if story:
            st.markdown('<div class="panel-label">Generated Story</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-panel"><div class="story-output">{story}</div></div>',
                        unsafe_allow_html=True)
            st.download_button(
                label="⬇  Download Story (.txt)",
                data=story,
                file_name=f"{result.get('title', 'story')[:40].replace(' ', '_')}.txt",
                mime="text/plain",
            )
        else:
            st.markdown('<div class="error-box">No story was generated.</div>', unsafe_allow_html=True)

    with tab_analysis:
        analysis = result.get("llm_response", "")
        if analysis:
            st.markdown('<div class="panel-label">LLM Analysis</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-panel"><div class="analysis-output">{analysis}</div></div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-box">No analysis available.</div>', unsafe_allow_html=True)

    with tab_json:
        payload = result.get("structured_json", {})
        if payload:
            st.markdown('<div class="panel-label">Structured JSON Payload</div>', unsafe_allow_html=True)
            json_str = json.dumps(payload, indent=2, ensure_ascii=False)
            st.markdown(f'<div class="json-block">{json_str}</div>', unsafe_allow_html=True)
            st.download_button(
                label="⬇  Download JSON (.json)",
                data=json_str,
                file_name="payload.json",
                mime="application/json",
            )


# ── App layout ─────────────────────────────────────────────────────────────────

render_header()

col_input, col_gap, col_info = st.columns([3, 0.2, 1.5])

with col_input:
    url = st.text_input(
        "Reddit Post URL",
        placeholder="https://www.reddit.com/r/stories/comments/...",
        key="url_input",
    )
    run_clicked = st.button("▸  RUN PIPELINE", key="run_btn")

with col_info:
    model_name = os.getenv("OLLAMA_MODEL", "llama3.2")
    base_url   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    st.markdown(f"""
    <div class="result-panel" style="margin-top:0; padding: 1rem 1.2rem;">
      <div class="panel-label">Environment</div>
      <div style="font-family:var(--mono); font-size:0.78rem; line-height:2; color:var(--text-dim);">
        <div>MODEL &nbsp;<span style="color:var(--text)">{model_name}</span></div>
        <div>HOST &nbsp;&nbsp;<span style="color:var(--text)">{base_url}</span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# ── Pipeline execution ─────────────────────────────────────────────────────────
if run_clicked:
    if not url.strip():
        st.markdown('<div class="error-box">⚠ Please enter a Reddit post URL.</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="panel-label">Pipeline</div>', unsafe_allow_html=True)
        result = run_pipeline_with_progress(url.strip())

        if result.get("error"):
            st.markdown(
                f'<div class="error-box">❌ &nbsp;{result["error"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            render_results(result)

# ── Empty state hint ───────────────────────────────────────────────────────────
elif not run_clicked:
    st.markdown("""
    <div style="
      border: 1px dashed #2a2a38;
      border-radius: 6px;
      padding: 3rem;
      text-align: center;
      color: #5a5a7a;
      font-family: 'Courier Prime', monospace;
      font-size: 0.85rem;
      line-height: 2;
    ">
      paste a reddit post url above<br>
      and run the pipeline<br>
      <span style="font-size:1.8rem; display:block; margin-top:1rem; opacity:0.3;">📡</span>
    </div>
    """, unsafe_allow_html=True)
