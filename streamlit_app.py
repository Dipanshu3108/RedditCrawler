import streamlit as st
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RedditStory — AI Story Pipeline",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state defaults ─────────────────────────────────────────────────────
if "pipeline_running" not in st.session_state:
    st.session_state.pipeline_running = False
if "pipeline_done" not in st.session_state:
    st.session_state.pipeline_done = False
if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None
if "submitted_url" not in st.session_state:
    st.session_state.submitted_url = ""

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:ital,wght@0,400;0,700;1,400&family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');

  /* ── CSS Variables ── */
  :root {
    --bg:        #0a0a0c;
    --surface:   #111116;
    --surface2:  #1a1a22;
    --border:    #2a2a38;
    --red:       #e63946;
    --red-dim:   #7a1e26;
    --amber:     #f4a261;
    --green:     #52b788;
    --muted:     #5a5a7a;
    --text:      #d8d8e8;
    --text-dim:  #8888aa;
    --mono:      'Courier Prime', monospace;
    --sans:      'DM Sans', sans-serif;
    --display:   'Bebas Neue', sans-serif;
  }

  /* ── Keyframe Animations ── */
  @keyframes pulse-border {
    0%, 100% { border-left-color: var(--amber); box-shadow: -3px 0 12px rgba(244,162,97,0.3); }
    50%       { border-left-color: #ffd199;      box-shadow: -3px 0 24px rgba(244,162,97,0.6); }
  }
  @keyframes slide-in {
    from { opacity: 0; transform: translateX(-12px); }
    to   { opacity: 1; transform: translateX(0); }
  }
  @keyframes fade-in {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes done-flash {
    0%   { background: rgba(82,183,136,0.25); }
    100% { background: rgba(82,183,136,0.05); }
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  @keyframes blink-dot {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.2; }
  }
  @keyframes scanline {
    0%   { background-position: 0 0; }
    100% { background-position: 0 100px; }
  }
  @keyframes url-collapse {
    from { opacity: 1; max-height: 120px; }
    to   { opacity: 0; max-height: 0; }
  }
  @keyframes status-slide {
    from { opacity: 0; transform: translateY(-8px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes progress-bar {
    from { width: 0%; }
    to   { width: 100%; }
  }
  @keyframes glow-red {
    0%, 100% { text-shadow: 0 0 10px rgba(230,57,70,0.4); }
    50%       { text-shadow: 0 0 25px rgba(230,57,70,0.8), 0 0 50px rgba(230,57,70,0.3); }
  }

  /* ── Base reset ── */
  html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
  }
  [data-testid="stHeader"] { background: transparent !important; }
  [data-testid="stSidebar"] { background: var(--surface) !important; }
  [data-testid="stToolbar"] { display: none; }
  #MainMenu { display: none; }
  footer { display: none; }

  h1, h2, h3 { font-family: var(--display) !important; letter-spacing: 0.08em; }

  .block-container {
    padding: 2rem 3rem !important;
    max-width: 1100px !important;
  }

  /* ── Header ── */
  .app-header {
    border-bottom: 1px solid var(--border);
    padding-bottom: 1.5rem;
    margin-bottom: 2rem;
    position: relative;
  }
  .app-title {
    font-family: var(--display);
    font-size: 3.8rem;
    letter-spacing: 0.1em;
    color: var(--red);
    line-height: 1;
    margin: 0;
    animation: glow-red 4s ease-in-out infinite;
  }
  .app-subtitle {
    font-family: var(--mono);
    font-size: 0.75rem;
    color: var(--muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.4rem;
  }

  /* ── Status bar (shown when running/done) ── */
  .status-bar {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--red);
    border-radius: 4px;
    padding: 0.75rem 1.25rem;
    margin-bottom: 1.5rem;
    font-family: var(--mono);
    font-size: 0.82rem;
    animation: status-slide 0.4s ease-out;
    position: relative;
    overflow: hidden;
  }
  .status-bar::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--red), var(--amber));
    animation: progress-bar 12s linear forwards;
  }
  .status-bar.done::after {
    width: 100%;
    background: var(--green);
    animation: none;
  }
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--red);
    animation: blink-dot 0.9s ease-in-out infinite;
    flex-shrink: 0;
  }
  .status-dot.done {
    background: var(--green);
    animation: none;
  }
  .status-url {
    color: var(--text-dim);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 600px;
  }
  .status-url span { color: var(--amber); }

  /* ── Input area ── */
  .stTextInput > div > div > input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  .stTextInput > div > div > input:focus {
    border-color: var(--red) !important;
    box-shadow: 0 0 0 2px rgba(230, 57, 70, 0.15) !important;
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
    background: var(--red) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: var(--display) !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.15em !important;
    padding: 0.6rem 2rem !important;
    transition: background 0.2s, transform 0.1s, box-shadow 0.2s !important;
    width: 100% !important;
  }
  .stButton > button:hover {
    background: #c1121f !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(230,57,70,0.35) !important;
  }
  .stButton > button:active { transform: translateY(0) !important; }

  /* ── Reset button ── */
  .reset-btn > button {
    background: var(--surface2) !important;
    color: var(--text-dim) !important;
    border: 1px solid var(--border) !important;
    font-family: var(--mono) !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.1em !important;
    padding: 0.5rem 1.25rem !important;
    width: auto !important;
  }
  .reset-btn > button:hover {
    border-color: var(--muted) !important;
    color: var(--text) !important;
    transform: none !important;
    box-shadow: none !important;
  }

  /* ── Pipeline stage cards ── */
  .pipeline-log {
    display: flex;
    flex-direction: column;
    gap: 0;
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
    background: var(--surface);
  }
  .pipeline-log-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.6rem 1rem;
    background: var(--surface2);
    border-bottom: 1px solid var(--border);
    font-family: var(--mono);
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
  }
  .log-dot-group { display: flex; gap: 5px; }
  .log-dot {
    width: 8px; height: 8px; border-radius: 50%;
    display: inline-block;
  }

  .stage-card {
    display: flex;
    align-items: center;
    gap: 0.9rem;
    padding: 0.7rem 1rem;
    border-left: 3px solid transparent;
    border-bottom: 1px solid var(--border);
    font-family: var(--mono);
    font-size: 0.82rem;
    color: var(--text-dim);
    transition: all 0.35s ease;
    position: relative;
    background: var(--surface);
  }
  .stage-card:last-child { border-bottom: none; }

  /* Pending */
  .stage-card.pending {
    border-left-color: #2a2a38;
    color: var(--muted);
    opacity: 0.6;
  }

  /* Running */
  .stage-card.running {
    border-left-color: var(--amber);
    color: var(--amber);
    background: rgba(244,162,97,0.05);
    animation: pulse-border 1.4s ease-in-out infinite, slide-in 0.3s ease-out;
  }
  .stage-card.running .stage-icon-wrap {
    animation: spin 1.2s linear infinite;
    display: inline-block;
  }

  /* Done */
  .stage-card.done {
    border-left-color: var(--green);
    color: var(--text);
    animation: done-flash 0.6s ease-out forwards, fade-in 0.3s ease-out;
  }

  /* Error */
  .stage-card.error {
    border-left-color: var(--red);
    color: var(--red);
    background: rgba(230,57,70,0.07);
    animation: slide-in 0.3s ease-out;
  }

  .stage-icon { font-size: 1rem; min-width: 1.4rem; text-align: center; }
  .stage-label { flex: 1; }
  .stage-meta {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.72rem;
    color: var(--muted);
  }
  .stage-badge {
    padding: 0.12rem 0.5rem;
    border-radius: 2px;
    font-size: 0.65rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }
  .badge-running {
    background: rgba(244,162,97,0.15);
    color: var(--amber);
    border: 1px solid rgba(244,162,97,0.3);
  }
  .badge-done {
    background: rgba(82,183,136,0.12);
    color: var(--green);
    border: 1px solid rgba(82,183,136,0.25);
  }
  .badge-error {
    background: rgba(230,57,70,0.12);
    color: var(--red);
    border: 1px solid rgba(230,57,70,0.25);
  }
  .stage-time { font-family: var(--mono); font-size: 0.7rem; color: var(--muted); }

  /* ── Result panels ── */
  .result-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.5rem;
    margin-top: 0.75rem;
    animation: fade-in 0.5s ease-out;
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
    flex-wrap: wrap;
    animation: fade-in 0.4s ease-out;
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
    animation: fade-in 0.3s ease-out;
  }

  /* ── Copy/download buttons ── */
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
    transition: all 0.2s !important;
  }
  .stDownloadButton > button:hover {
    border-color: var(--muted) !important;
    color: var(--text) !important;
    background: var(--surface) !important;
    transform: none !important;
    box-shadow: none !important;
  }

  hr { border-color: var(--border) !important; margin: 2rem 0 !important; }
  .stSpinner > div { border-top-color: var(--red) !important; }
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
  }
  .stTabs [data-baseweb="tab"] {
    font-family: var(--mono) !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.1em !important;
    color: var(--muted) !important;
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 1.25rem !important;
    text-transform: uppercase !important;
  }
  .stTabs [aria-selected="true"] {
    color: var(--text) !important;
    border-bottom: 2px solid var(--red) !important;
  }
</style>
""", unsafe_allow_html=True)


# ── Helper renderers ───────────────────────────────────────────────────────────

def render_header():
    st.markdown("""
    <div class="app-header">
      <p class="app-title">REDDIT STORY</p>
      <p class="app-subtitle">▸ AI Story Writer</p>
    </div>
    """, unsafe_allow_html=True)


def stage_html(icon, label, status="pending", elapsed=None, step_num=0):
    """Build a single animated stage row."""
    badge = ""
    time_str = ""
    spin_open = spin_close = ""

    if status == "running":
        badge = '<span class="stage-badge badge-running">● running</span>'
        spin_open  = '<span class="stage-icon-wrap">'
        spin_close = '</span>'
    elif status == "done":
        badge = '<span class="stage-badge badge-done">✓ done</span>'
        if elapsed is not None:
            time_str = f'<span class="stage-time">{elapsed:.1f}s</span>'
    elif status == "error":
        badge = '<span class="stage-badge badge-error">✕ error</span>'
        if elapsed is not None:
            time_str = f'<span class="stage-time">{elapsed:.1f}s</span>'

    return f"""
    <div class="stage-card {status}">
      <span class="stage-icon">{spin_open}{icon}{spin_close}</span>
      <span class="stage-label">{label}</span>
      <span class="stage-meta">
        {badge}
        {time_str}
      </span>
    </div>"""


def render_pipeline_log(stages: list):
    """Render a styled terminal-log-style pipeline block."""
    rows = "".join(stage_html(icon, label, status, elapsed, i)
                   for i, (icon, label, status, elapsed) in enumerate(stages))
    done_count  = sum(1 for s in stages if s[2] == "done")
    total_count = len(stages)

    st.markdown(f"""
    <div class="pipeline-log">
      <div class="pipeline-log-header">
        <span>Pipeline Log</span>
        <span>{done_count} / {total_count} stages</span>
        <div class="log-dot-group">
          <span class="log-dot" style="background:#e63946"></span>
          <span class="log-dot" style="background:#f4a261"></span>
          <span class="log-dot" style="background:#52b788"></span>
        </div>
      </div>
      {rows}
    </div>
    """, unsafe_allow_html=True)


def render_status_bar(url: str, done: bool = False):
    """Compact status pill shown while running or after completion."""
    cls  = "done" if done else ""
    dot  = "done" if done else ""
    verb = "Processed" if done else "Processing"
    # truncate url for display
    display_url = url if len(url) < 70 else url[:67] + "..."
    st.markdown(f"""
    <div class="status-bar {cls}">
      <span class="status-dot {dot}"></span>
      <span class="status-url">{verb}: <span>{display_url}</span></span>
    </div>
    """, unsafe_allow_html=True)


def run_pipeline_with_progress(url: str):
    """Run the full pipeline, updating the animated log after each node."""
    from app.state import initial_state
    from app.agents.validator import validate_url
    from app.agents.metadata_agent import extract_metadata
    from app.agents.content_agent import extract_content
    from app.agents.json_agent import build_structured_json
    from app.agents.llm_agent import run_llm_analysis
    from app.agents.story_agent import run_story_writer

    STEPS = [
        ("🔗", "URL Validation",       "Verifying Reddit URL format & accessibility"),
        ("📡", "Metadata Extraction",  "Pulling post title, upvotes, author, subreddit"),
        ("📄", "Content Extraction",   "Scraping body text and top comments"),
        ("🗂️", "JSON Structuring",     "Normalising data into structured payload"),
        ("🤖", "LLM Analysis",         "Running local model — summarising & analysing"),
        ("✍️", "Story Writer",          "Generating narrative from analysis"),
    ]

    stages = [(icon, label, "pending", None) for icon, label, _ in STEPS]
    placeholder = st.empty()

    def refresh(idx, status, elapsed=None):
        stages[idx] = (STEPS[idx][0], STEPS[idx][1], status, elapsed)
        with placeholder.container():
            render_pipeline_log(stages)

    def run_step(idx, fn, state):
        refresh(idx, "running")
        t0 = time.perf_counter()
        result = fn(state)
        elapsed = time.perf_counter() - t0
        refresh(idx, "error" if result.get("error") else "done", elapsed)
        return result

    state = initial_state(url)

    state = run_step(0, validate_url, state)
    if state.get("error") or not state.get("is_valid"):
        return state

    state = run_step(1, extract_metadata, state)
    if state.get("error"): return state

    state = run_step(2, extract_content, state)
    if state.get("error"): return state

    state = run_step(3, build_structured_json, state)
    if state.get("error"): return state

    state = run_step(4, run_llm_analysis, state)
    if state.get("error"): return state

    state = run_step(5, run_story_writer, state)
    return state


def render_results(result: dict):
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="meta-row">
      <div class="meta-chip">TITLE &nbsp; <span>{result.get('title', '—')}</span></div>
      <div class="meta-chip">UPVOTES &nbsp; <span>{result.get('upvotes', 0):,}</span></div>
    </div>
    """, unsafe_allow_html=True)

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

model_name = os.getenv("OLLAMA_MODEL_CLOUD", "")
base_url_env = os.getenv("OLLAMA_CLOUD_BASE_URL", "")

# ── State-driven layout ────────────────────────────────────────────────────────
is_running = st.session_state.pipeline_running
is_done    = st.session_state.pipeline_done

# ── Show URL input only when idle ──────────────────────────────────────────────
if not is_running and not is_done:
    col_input, col_gap, col_info = st.columns([3, 0.2, 1.5])

    with col_input:
        url = st.text_input(
            "Reddit Post URL",
            placeholder="https://www.reddit.com/r/stories/comments/...",
            key="url_input",
        )
        run_clicked = st.button("▸  RUN PIPELINE", key="run_btn")

    with col_info:
        st.markdown(f"""
        <div class="result-panel" style="margin-top:0; padding: 1rem 1.2rem;">
          <div class="panel-label">Environment</div>
          <div style="font-family:var(--mono); font-size:0.78rem; line-height:2; color:var(--text-dim);">
            <div>MODEL &nbsp;<span style="color:var(--text)">{model_name}</span></div>
            <div>HOST &nbsp;&nbsp;<span style="color:var(--text)">{base_url_env}</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    if run_clicked:
        if not url.strip():
            st.markdown('<div class="error-box">⚠ Please enter a Reddit post URL.</div>',
                        unsafe_allow_html=True)
        else:
            st.session_state.submitted_url    = url.strip()
            st.session_state.pipeline_running = True
            st.session_state.pipeline_done    = False
            st.session_state.pipeline_result  = None
            st.rerun()

    else:
        # ── Empty state ──────────────────────────────────────────────────────
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


# ── Running state ──────────────────────────────────────────────────────────────
elif is_running:
    submitted = st.session_state.submitted_url
    render_status_bar(submitted, done=False)

    st.markdown('<div class="panel-label">Pipeline</div>', unsafe_allow_html=True)
    result = run_pipeline_with_progress(submitted)

    st.session_state.pipeline_result  = result
    st.session_state.pipeline_running = False
    st.session_state.pipeline_done    = True
    st.rerun()


# ── Done state ─────────────────────────────────────────────────────────────────
elif is_done:
    submitted = st.session_state.submitted_url
    result    = st.session_state.pipeline_result

    # Compact status + reset button side by side
    col_status, col_reset = st.columns([5, 1])
    with col_status:
        render_status_bar(submitted, done=True)
    with col_reset:
        st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
        if st.button("↺  New URL", key="reset_btn"):
            st.session_state.pipeline_running = False
            st.session_state.pipeline_done    = False
            st.session_state.pipeline_result  = None
            st.session_state.submitted_url    = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if result and result.get("error"):
        st.markdown(
            f'<div class="error-box">❌ &nbsp;{result["error"]}</div>',
            unsafe_allow_html=True,
        )
    elif result:
        render_results(result)