import sys
import os
import streamlit as st
import json
import streamlit.components.v1 as components
import time
from datetime import datetime
import html as html_lib

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from crawler import DocumentLoader
from search import SearchEngine
from ai_agent import TangenAIAgent

# Page configuration
st.set_page_config(page_title="TangenAI", page_icon="🔍", layout="wide")

# Initialization
if "loader" not in st.session_state:
    st.session_state.loader = DocumentLoader()
if "engine" not in st.session_state:
    st.session_state.engine = SearchEngine()
if "ai_agent" not in st.session_state:
    st.session_state.ai_agent = TangenAIAgent()
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
if "recent_searches" not in st.session_state:
    st.session_state.recent_searches = []
if "ai_mode" not in st.session_state:
    st.session_state.ai_mode = False
if "vFinal_input" not in st.session_state:
    st.session_state.vFinal_input = ""

# Preload documents (only once per session)
if "docs_loaded" not in st.session_state:
    st.session_state.docs_loaded = False

if not st.session_state.docs_loaded:
    with st.spinner("Initializing Search Index..."):
        # Preload local sample docs
        sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_docs")
        if os.path.exists(sample_path):
            local_docs = st.session_state.loader.load_local_documents(sample_path)
            for doc_id, doc_data in local_docs.items():
                st.session_state.engine.add_document(doc_id, doc_data)

        # Preload social data
        social_path = os.path.join(os.path.dirname(__file__), "data", "social")
        if os.path.exists(social_path):
            for filename in os.listdir(social_path):
                if filename.endswith(".json"):
                    with open(os.path.join(social_path, filename), "r") as f:
                        social_data = json.load(f)
                        for item in social_data:
                            st.session_state.engine.add_document(item["id"], item)
        st.session_state.docs_loaded = True

# Inject Custom CSS for Premium Look
st.markdown("""
<style>
    /* Google-Specific Typography */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Product+Sans:wght@400;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Roboto', arial, sans-serif;
    }
    
    /* White Background */
    .stApp {
        background-color: #ffffff;
        color: #202124;
    }

    /* Reduce Streamlit default top padding (Google-like vertical balance) */
    section.main > div.block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1000px !important;
    }
    
    /* Google Logo/Header Styling */
    .hero-title {
        font-family: 'Product Sans', arial, sans-serif;
        font-size: 5.5rem;
        font-weight: 500;
        letter-spacing: -2px;
        text-align: center;
        padding-top: 5rem;
        margin-bottom: 2rem;
        display: flex;
        justify-content: center;
        gap: 2px;
    }
    
    .g-blue { color: #4285F4; }
    .g-red { color: #EA4335; }
    .g-yellow { color: #FBBC05; }
    .g-green { color: #34A853; }
    
    .hero-subtitle {
        text-align: center;
        color: #70757a;
        font-size: 0.9rem;
        margin-bottom: 3rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Hide sidebar entirely to hide the internal toggle */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], .stSidebar {
        display: none !important;
        width: 0 !important;
        visibility: hidden !important;
    }
    
    /* Google Search Bar Styling - Nuclear Fix for BaseWeb Ghost Arcs */
    div[data-testid="stTextInputRootElement"], 
    div[data-baseweb="input"],
    div[data-testid="stTextInput"] div, 
    div[data-testid="stTextInput"] div div, 
    div[data-testid="stTextInput"] div div div {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #202124 !important;
        border: 1px solid #dfe1e5 !important;
        border-radius: 24px !important;
        padding-left: 45px !important; 
        padding-right: 20px !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
        width: 100% !important;
        height: 48px !important;
    }
    .stTextInput > div > div > input:hover, .stTextInput > div > div > input:focus {
        box-shadow: 0 1px 6px rgba(32, 33, 36, 0.28) !important;
        border-color: rgba(223,225,229, 0) !important;
    }
    
    /* Search Icon Positioning Fix */
    .stTextInput::before {
        content: "🔍";
        position: absolute;
        left: 15px;
        top: 24px;
        transform: translateY(-50%);
        z-index: 10;
        font-size: 1.1rem;
        opacity: 0.4;
        pointer-events: none;
    }
    
    /* Google Results Styling (Flat, no borders) */
    .result-container {
        max-width: 652px;
        margin-bottom: 30px;
        padding-left: 20px;
    }
    
    .result-link-container {
        display: flex;
        flex-direction: column;
        margin-bottom: 4px;
    }
    
    .result-title {
        color: #1a0dab;
        font-size: 1.25rem;
        font-weight: 400;
        text-decoration: none;
        margin-bottom: 1px;
    }
    
    .result-title:hover {
        text-decoration: underline;
    }
    
    .result-url {
        color: #202124;
        font-size: 0.875rem;
        font-weight: 400;
        line-height: 1.3;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .result-snippet {
        color: #4d5156;
        font-size: 0.875rem;
        line-height: 1.58;
        margin-top: 4px;
        font-weight: 400;
    }
    
    .result-snippet b {
        color: #202124;
        font-weight: 700;
    }
    
    .result-score-subtle {
        color: #70757a;
        font-size: 0.75rem;
        margin-top: 6px;
    }
    
    /* Social Badges */
    .platform-badge {
        display: inline-flex;
        align-items: center;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-right: 8px;
        background: #f1f3f4 !important;
        color: #5f6368 !important;
        border: 1px solid #dfe1e5 !important;
    }
    .badge-semantic { 
        color: #1a73e8 !important; 
        border-color: #1a73e833 !important; 
        background: #1a73e808 !important;
        font-weight: 600 !important;
    }
    .badge-reddit { color: #FF4500 !important; border-color: #FF450022 !important; background: #FF450008 !important; }
    .badge-youtube { color: #FF0000 !important; border-color: #FF000022 !important; background: #FF000008 !important; }
    .badge-x { color: #000000 !important; border-color: #00000022 !important; background: #00000008 !important; }
    .badge-linkedin { color: #0077B5 !important; border-color: #0077B522 !important; background: #0077B508 !important; }
    .badge-facebook { color: #1877F2 !important; border-color: #1877F222 !important; background: #1877F208 !important; }
    .badge-instagram { color: #E4405F !important; border-color: #E4405F22 !important; background: #E4405F08 !important; }
    .badge-news { color: #70757a !important; border-color: #70757a44 !important; background: #f8f9fa !important; font-weight: 600 !important; }

    /* Sidebar overlay */
    section[data-testid="stSidebar"] {
        background: #f8f9fa !important;
        border-right: 1px solid #dfe1e5;
    }
    
    /* Force buttons to look like Google buttons */
    .stButton > button {
        background-color: #f8f9fa !important;
        color: #3c4043 !important;
        border: 1px solid #f8f9fa !important;
        border-radius: 4px !important;
        padding: 0 16px !important;
        font-size: 0.875rem !important;
        height: 36px !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
    }
    
    .stButton > button:hover {
        border-color: #dadce0 !important;
        color: #202124 !important;
        background-color: #f8f9fa !important;
        box-shadow: 0 1px 1px rgba(0,0,0,0.1) !important;
    }

    /* Remove card styling from previous iteration */
    .result-card {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin-bottom: 28px !important;
        box-shadow: none !important;
        transition: none !important;
        transform: none !important;
    }

    /* TangenAI Pagination Styling */
    .pagination-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 60px 0;
        width: 100%;
        font-family: 'Product Sans', Arial, sans-serif;
    }
    .tangenai-logo-p {
        font-size: 2.8rem;
        display: flex;
        gap: 0px;
        margin-bottom: -10px;
        letter-spacing: -1px;
    }
    .page-numbers-row {
        display: flex;
        gap: 0px;
        justify-content: center;
        width: 100%;
        padding-left: 32px; /* Offset for 'T' */
    }
    .page-num-btn {
        width: 28px;
        text-align: center;
        font-size: 0.95rem;
        color: #1a73e8;
        cursor: pointer;
    }
    .page-num-btn:hover { text-decoration: underline; }
    .page-num-active { color: #202124; cursor: default; }
    
    /* Next Button Styling */
    .next-wrap {
        margin-left: 25px;
        display: flex;
        flex-direction: column;
        align-items: center;
        color: #1a73e8;
        cursor: pointer;
        text-decoration: none;
    }
    .next-wrap:hover { text-decoration: underline; }
    .next-arrow { font-size: 1.4rem; font-weight: bold; margin-bottom: -5px; }
    .next-text { font-size: 0.9rem; }
    
    /* Clean buttons for numbers */
    div[data-testid="column"] button {
        background: transparent !important;
        border: none !important;
        color: #1a73e8 !important;
        padding: 0 !important;
        min-width: 20px !important;
        width: 100% !important;
        height: auto !important;
        font-size: 0.9rem !important;
    }
    div[data-testid="column"] button:hover {
        text-decoration: underline !important;
        background: transparent !important;
        box-shadow: none !important;
    }
    div[data-testid="column"] button p {
        margin: 0 !important;
    }
    /* Clean buttons for suggestions */
    .suggestion-box div[data-testid="stButton"] button {
        background: transparent !important;
        border: none !important;
        color: #202124 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 12px 20px !important;
        border-radius: 0 !important;
        font-family: inherit !important;
        font-size: 1.05rem !important;
        box-shadow: none !important;
    }
    .suggestion-box div[data-testid="stButton"] button:hover {
        background-color: #f8f9fa !important;
    }
    .suggestion-box div[data-testid="stButton"] button p {
        margin: 0 !important;
        font-weight: 400 !important;
    }
    .suggestion-box {
        background: white !important;
        border-radius: 0 0 24px 24px !important;
        box-shadow: 0 4px 6px rgba(32,33,36,0.2) !important;
        border: 1px solid #dfe1e5 !important;
        border-top: none !important;
        margin-top: -15px !important; /* Overlap with search bar */
        padding-top: 15px !important;
        position: absolute !important;
        width: 100% !important;
        z-index: 10000 !important;
        overflow: hidden !important;
    }
    .stTextInput { z-index: 10001 !important; position: relative !important; }

    /* --- Design System & Typography --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    /* --- Universal Layout --- */
    .stApp {
        background-color: #ffffff;
    }

    .main-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        min-height: 100vh;
        box-sizing: border-box;
        transition: all 0.5s ease-in-out;
    }

    .home-header {
        margin-top: 6vh;
        margin-bottom: 18px;
        text-align: center;
    }

    .results-header {
        margin-top: 20px;
        margin-bottom: 20px;
        align-self: flex-start;
        padding-left: 20px;
    }

    /* --- Super Search Bar (Google Style) --- */
    .search-box-unified {
        width: 100%;
        max-width: 650px;
        height: 52px;
        background: white;
        border: 1px solid #dfe1e5;
        border-radius: 26px;
        display: flex;
        align-items: center;
        padding: 0 15px;
        box-shadow: none;
        transition: box-shadow 0.2s, border-radius 0.2s;
        position: relative;
        z-index: 1001;
    }

    .search-box-unified:hover, .search-box-unified:focus-within {
        box-shadow: 0 1px 6px rgba(32,33,36,0.28);
        border-color: rgba(223,225,229,0);
    }
    
    /* When history is open, round top corners only */
    .search-box-active {
        border-radius: 26px 26px 0 0 !important;
        box-shadow: 0 1px 6px rgba(32,33,36,0.28) !important;
    }

    .icon-btn {
        color: #70757a;
        font-size: 20px;
        cursor: pointer;
        padding: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: color 0.2s;
        background: transparent;
        border: none;
    }
    .icon-btn:hover { color: #202124; }
    
    .search-input-wrap {
        flex-grow: 1;
        margin-top: -5px;
    }
    .search-input-wrap div[data-testid="stTextInput"] > div > div > input {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
        font-size: 1.1rem !important;
        padding-left: 10px !important;
    }

    /* --- Functional Dropdown --- */
    .history-dropdown {
        position: absolute;
        top: 51px;
        left: -1px;
        right: -1px;
        background: white;
        border: 1px solid #dfe1e5;
        border-top: none;
        border-radius: 0 0 26px 26px;
        box-shadow: 0 4px 6px rgba(32,33,36,0.28);
        z-index: 1000;
        padding: 10px 0;
        max-height: 400px;
        overflow-y: auto;
    }

    .history-item {
        display: flex;
        align-items: center;
        padding: 8px 20px;
        cursor: pointer;
        transition: background 0.1s;
    }
    .history-item:hover { background: #f1f3f4; }
    .history-item span { color: #202124; font-size: 0.95rem; }
    .history-clock { color: #9aa0a6; margin-right: 15px; font-size: 16px; }

    /* --- AI Toggle Pill --- */
    .ai-pill {
        background: #f8f9fa;
        border: 1px solid #dfe1e5;
        border-radius: 20px;
        padding: 5px 15px;
        font-size: 0.85rem;
        color: #3c4043;
        font-weight: 500;
        margin-left: 10px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .ai-pill-active {
        background: #e8f0fe;
        border-color: #1a73e8;
        color: #1a73e8;
    }

    /* --- Result Cards --- */
    .result-card {
        margin-bottom: 28px;
        max-width: 650px;
    }
    .result-url { color: #202124; font-size: 0.875rem; margin-bottom: 4px; display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .result-title { color: #1a0dab; font-size: 1.25rem; font-weight: 400; text-decoration: none; display: block; margin-bottom: 4px; }
    .result-title:hover { text-decoration: underline; }
    .result-snippet { color: #4d5156; font-size: 0.875rem; line-height: 1.58; }

    /* --- Modal Styling --- */
    .modal-overlay {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.4);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    .modal-content {
        background: white;
        padding: 30px;
        border-radius: 12px;
        width: 90%;
        max-width: 500px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- Initialization ---
if "show_modal" not in st.session_state: st.session_state.show_modal = False
if "voice_active" not in st.session_state: st.session_state.voice_active = False
if "dark_mode" not in st.session_state: st.session_state.dark_mode = False

# --- Dark Mode Injection ---
dark_css = """
<style>
    .stApp { background-color: #202124 !important; color: #e8eaed !important; }
    .search-box-unified { background: #3c4043 !important; border-color: #5f6368 !important; }
    .search-box-unified:hover { box-shadow: 0 1px 6px rgba(0,0,0,0.5) !important; }
    .search-input-wrap input { color: #e8eaed !important; }
    .history-dropdown { background: #3c4043 !important; border-color: #5f6368 !important; }
    .history-item:hover { background: #4a4d51 !important; }
    .history-item span { color: #e8eaed !important; }
    .result-title { color: #8ab4f8 !important; }
    .result-snippet { color: #bdc1c6 !important; }
    .modal-content { background: #202124 !important; color: #e8eaed !important; }
    .icon-btn { color: #9aa0a6 !important; }
    
    .premium-toggle-box {
        position: fixed;
        top: 25px;
        right: 40px;
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 12px;
        background: {"rgba(40, 40, 40, 0.85)" if st.session_state.dark_mode else "rgba(255, 255, 255, 0.85)"};
        backdrop-filter: blur(12px);
        padding: 10px 20px;
        border-radius: 40px;
        border: 1px solid {"rgba(255,255,255,0.1)" if st.session_state.dark_mode else "rgba(0,0,0,0.1)"};
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .premium-toggle-box:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 12px 40px rgba(0,0,0,0.2);
    }
    
    /* Logo / Home Navigation styling */
    .logo-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin-bottom: 2rem;
    }
    .logo-btn button {
        background: transparent !important;
        border: none !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -2px !important;
        color: inherit !important;
        box-shadow: none !important;
        transition: transform 0.2s !important;
    }
    .logo-btn button:hover {
        transform: scale(1.02);
    }
</style>
"""

# --- Theme CSS ---
if st.session_state.dark_mode:
    st.markdown(dark_css, unsafe_allow_html=True)

st.markdown(
    """
    <style>
      .premium-toggle-box {
        position: fixed;
        top: 18px;
        right: 22px;
        z-index: 9999;
        backdrop-filter: blur(12px);
        padding: 10px 18px;
        border-radius: 999px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        cursor: pointer;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
      }
      .premium-toggle-box:hover {
        transform: translateY(-1px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.16);
      }
      .premium-toggle-inner {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 600;
        font-size: 0.92rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Real Streamlit controls (no hidden buttons) ---
top_spacer = st.container()
with top_spacer:
    c1, c2, c3 = st.columns([6, 1.5, 1.5])
    with c3:
        # Theme toggle moved to floating overlay
        pass

def go_home():
    st.session_state.search_query = ""
    st.session_state.last_query = ""
    st.session_state.vFinal_input = ""

# --- UI Layout State ---
is_results_page = bool(st.session_state.search_query)
header_class = "results-header" if is_results_page else "home-header"

# 1. Branding (functional home)
brand_size = "3.6rem" if is_results_page else "6rem"
st.markdown(
    f"""
    <div style="display:flex; justify-content:center; width:100%; margin-top:{'0.5rem' if is_results_page else '6vh'};">
      <button
        onclick="window.location.reload()"
        style="all:unset; cursor:pointer; text-align:center; font-family:'Product Sans','Inter',sans-serif;">
        <div style="font-size:{brand_size}; font-weight:700; letter-spacing:-2px; line-height:1.05;">
          <span style="color:#4285F4;">T</span><span style="color:#EA4335;">a</span><span style="color:#FBBC05;">n</span><span style="color:#4285F4;">g</span><span style="color:#34A853;">e</span><span style="color:#EA4335;">n</span><span style="color:#4285F4;">A</span><span style="color:#34A853;">I</span>
        </div>
      </button>
    </div>
    """,
    unsafe_allow_html=True,
)

if not is_results_page:
    st.markdown('<div style="color: #70757a; font-size: 1.15rem; margin-bottom: 28px; text-align: center;">High-Performance Entity Intelligence</div>', unsafe_allow_html=True)

# 2. Functional "+" Source Modal
if st.session_state.show_modal:
    st.markdown('<div class="modal-overlay">', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="modal-content">', unsafe_allow_html=True)
        st.subheader("➕ Add Data Source")
        source_url = st.text_input("Ingest URL", placeholder="https://en.wikipedia.org/wiki/...")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            if st.button("Index Now", use_container_width=True):
                if source_url:
                    with st.spinner("Indexing..."):
                        docs = st.session_state.loader.crawl_webpage(source_url)
                        if docs:
                            for url_id, d in docs.items(): st.session_state.engine.add_document(url_id, d)
                            st.success("Indexed!")
                            st.session_state.show_modal = False
                            st.rerun()
        with m_col2:
            if st.button("Close", key="close_modal", use_container_width=True):
                st.session_state.show_modal = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Final Advanced UI Construction ---
st.markdown(f"""
<style>
    /* Dark Mode Core Overrides */
    {'.stApp, div[data-testid="stAppViewContainer"] { background-color: #202124 !important; color: #e8eaed !important; }' if st.session_state.dark_mode else ''}

    /* --- Google-like single search bar (styles applied to the real Streamlit input) --- */
    input.tangen-search-input {{
        background: {"#3c4043" if st.session_state.dark_mode else "#ffffff"} !important;
        color: {"#e8eaed" if st.session_state.dark_mode else "#202124"} !important;
        border: 1px solid {"#5f6368" if st.session_state.dark_mode else "#dfe1e5"} !important;
        border-radius: 26px !important;
        height: 52px !important;
        line-height: 52px !important;
        font-size: 1.05rem !important;
        padding-left: 48px !important;  /* plus icon */
        padding-right: 170px !important; /* mic + ai pill */
        transition: box-shadow 0.18s ease, border-color 0.18s ease !important;
    }}
    input.tangen-search-input:hover {{
        box-shadow: 0 1px 6px rgba(32,33,36,0.28) !important;
        border-color: rgba(223,225,229,0) !important;
    }}
    input.tangen-search-input:focus {{
        box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.16), 0 1px 6px rgba(32,33,36,0.28) !important;
        border-color: rgba(26, 115, 232, 0.55) !important;
        outline: none !important;
    }}

    /* Container we attach to the Streamlit text input widget via JS */
    .tangen-search-container {{
        position: relative !important;
        max-width: 650px !important;
        margin: 0 auto !important;
    }}

    .tangen-search-icons {{
        position: absolute;
        inset: 0;
        pointer-events: none;
    }}
    .tangen-search-icon-left {{
        position: absolute;
        left: 12px;
        top: 50%;
        transform: translateY(-50%);
        color: #70757a;
        font-size: 22px;
        opacity: 0.8;
        pointer-events: auto;
    }}
    .tangen-search-icon-right {{
        position: absolute;
        right: 8px;
        top: 50%;
        transform: translateY(-50%);
        display: flex;
        align-items: center;
        gap: 8px;
        pointer-events: auto;
    }}
    .tangen-icon-btn {{
        width: 34px;
        height: 34px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 999px;
        cursor: pointer;
        user-select: none;
        font-size: 18px;
        color: #4285f4;
        background: transparent;
        transition: transform 0.12s ease, background 0.12s ease, color 0.12s ease;
    }}
    .tangen-icon-btn:hover {{
        transform: translateY(-1px);
        background: rgba(26, 115, 232, 0.08);
        color: #1a73e8;
    }}
    .tangen-icon-btn:active {{
        transform: translateY(0);
        background: rgba(26, 115, 232, 0.14);
    }}
    .tangen-icon-btn:focus {{
        outline: 2px solid rgba(26,115,232,0.35);
        outline-offset: 2px;
    }}
    
    /* Autocomplete & History unified */
    .dropdown-box {{
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: {"#3c4043" if st.session_state.dark_mode else "white"};
        border: 1px solid {"#5f6368" if st.session_state.dark_mode else "#dfe1e5"};
        border-top: none;
        border-radius: 0 0 24px 24px;
        box-shadow: 0 4px 6px rgba(32,33,36,0.28);
        z-index: 1000;
        padding-bottom: 10px;
        opacity: 0;
        transform: translateY(-4px);
        transition: opacity 120ms ease-out, transform 120ms ease-out;
        pointer-events: none;
    }}
    .dropdown-box.open {{
        opacity: 1;
        transform: translateY(0);
        pointer-events: auto;
    }}

    .suggestion-item {{
        padding: 10px 20px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 12px;
        color: {"#e8eaed" if st.session_state.dark_mode else "#202124"};
        font-size: 0.98rem;
        line-height: 1.2;
        user-select: none;
    }}
    .suggestion-item:hover {{
        background: {"#4a4d51" if st.session_state.dark_mode else "#f1f3f4"};
    }}
    .suggestion-item.active {{
        background: {"#3b6bdc33" if st.session_state.dark_mode else "#e8f0fe"};
    }}
    
    .dropdown-box .stButton button {{
        background: none !important;
        border: none !important;
        text-align: left !important;
        padding: 8px 45px !important;
        color: {"#e8eaed" if st.session_state.dark_mode else "#202124"} !important;
        width: 100%;
    }}
    .dropdown-box .stButton button:hover {{
        background: {"#4a4d51" if st.session_state.dark_mode else "#f1f3f4"} !important;
    }}
    
    /* AI Mode Pill (Internal to Search Bar) */
    .tangen-ai-pill-internal {{
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 18px;
        background: {"#3c4043" if st.session_state.dark_mode else "#f1f3f4"} !important;
        border: 1px solid {"#5f6368" if st.session_state.dark_mode else "#dfe1e5"} !important;
        color: {"#e8eaed" if st.session_state.dark_mode else "#202124"} !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        cursor: pointer;
        transition: all 0.2s ease;
        user-select: none;
        white-space: nowrap;
    }}
    .tangen-ai-pill-internal:hover {{
        background: {"#4a4d51" if st.session_state.dark_mode else "#e8eaed"} !important;
    }}
    .tangen-ai-pill-internal.active {{
        background: #e8f0fe !important;
        color: #1a73e8 !important;
        border-color: #1a73e8 !important;
    }}
    .tangen-ai-pill-internal i {{
        font-size: 14px;
    }}
</style>
""", unsafe_allow_html=True)

search_col = st.columns([1, 6, 1])[1] if not is_results_page else st.container()

with search_col:
    # Use on_change to trigger search immediately on Enter
    def on_search():
        query_text = st.session_state.vFinal_input.strip()
        if query_text:
            if query_text in st.session_state.recent_searches:
                st.session_state.recent_searches.remove(query_text)
            st.session_state.recent_searches.insert(0, query_text)
            st.session_state.recent_searches = st.session_state.recent_searches[:10]
            st.session_state.search_query = query_text
            st.session_state.last_query = query_text

    query = st.text_input(
        "Search",
        placeholder="Search anything...",
        label_visibility="collapsed",
        key="vFinal_input",
        on_change=on_search
    )

    # Simplified JS for icons and AI toggle
    components.html(
        f"""
        <script>
        (function () {{
          const doc = (window.parent && window.parent.document) ? window.parent.document : document;
          
          function init() {{
            const input = doc.querySelector('input[placeholder="Search anything..."]');
            if (!input) return setTimeout(init, 50);

            input.classList.add('tangen-search-input');
            const container = input.closest('div[data-testid="stTextInput"]') || input.parentElement;
            if (!container) return;
            container.classList.add('tangen-search-container');

            if (!container.querySelector('.tangen-search-icons')) {{
                const icons = doc.createElement('div');
                icons.className = 'tangen-search-                icons.innerHTML = `
                  <div class="tangen-search-icon-left tangen-toggle-ai-trigger" style="cursor:pointer; font-size:1.4rem;">🔍</div>
                  <div class="tangen-search-icon-right">
                    <div class="tangen-icon-btn" role="button">
                      <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAE4AAABGCAYAAABi+aJwAAACmUlEQVR4AeyY602CQRBFN5ZABfwmFEAplEEBhBoog1IogwpoQT2aJZuR+Lk37sN4Sa77mrvMHEYRXl79kAi8JD8kAgYnYUvJ4AxOJCDa3HEGJxIQbe44gxMJiDZ3nMGJBESbO87gRAKi7ZuOE2/8JzaDE19ogzM4kYBoc8cZnEhAtLnj/jq46/Wa0Pl8/hjFerrZhnccsPb7fcoCHHPGbhSEJxoODkjAi7kDbr1ex+1p1kPBAWeJBGCXYkacTw/uWTeOABWfcxi4GiA1sbHAVmsNXKts/tC9Bie+WAZncCIB0eaOMziRgGhzxxmcSEC0ueMMTiQg2txxBicSEG1NO44P53ynlsVayXO32z1sfBWV72NU73xcKE5+HVyZR1kw+xTNiOIZe4p+657a524KbimZw+GwFJJizKgOi4k2B1d2RCwaKOV5TI4zYsr98o54Vsa1njcHF4uLX4VfLpcvXUXR+DhjnlX+que9UWNzcHQNygXSMSivGYF0u93S7V3AYmSPsyygobxmjDHs9VJzcBQSC6TrIgTiUAmZNQJ0jI93EtdTXcABIxYKCLRULJBRGcddqNzrPe8CjqIoFIDMswDH/2KAYY7oLtaIM9Y5npE7uIv5SHUDR5H8/XpWNHCAhgDGGuEphZc7yr1R867gKJLiEfOfii4DWK3vp/crcd3BkSQA8jsnc/aeKQMDGvNnMaP2hoDLxQINAREwq9UqIebszQgs5z4UXE4ij/f7PaG8nnnsCW5mDtW5GVw1sk+DwX1yqP45DbjtdvvxYZ83i81mU11Ib8M04I7H4wPc6XTqzaH6+aYBV535YIPBiS+AwRmcSEC0ueMMTiQg2txxBicSEG2TdJyY/UCbwYnwDc7gRAKizR0ngnsDAAD//3mgaJoAAAAGSURBVAMA0o4AcxiYDHAAAAAASUVORK5CYII=" style="width:38px; height:38px; vertical-align:middle; filter: grayscale(1) invert({'1' if st.session_state.dark_mode else '0'}); opacity:0.8;">
                    </div>
                  </div>
                `;
                container.appendChild(icons);
 
                icons.querySelector('.tangen-toggle-ai-trigger').addEventListener('click', (e) => {{
                  e.stopPropagation();
                  const sidebar = doc.querySelector('section[data-testid="stSidebar"]');
                  if (sidebar) {{
                    const checkbox = sidebar.querySelector('input[type="checkbox"]');
                    if (checkbox) checkbox.click();
                  }}
                }});
     }});
            }}
          }}
          init();
        }})();
        </script>
        """,
        height=0,
    )

    # Hidden sidebar toggle for AI Mode (Completely removed from main view)
    with st.sidebar:
        st.checkbox("Toggle AI", key="ai_toggle_sidebar", value=st.session_state.ai_mode, on_change=lambda: st.session_state.update(ai_mode=not st.session_state.ai_mode))

    # 2. Search Suggestions Dropdown (Simplified)
    suggest_items = []
    icon = "🕒"
    if not st.session_state.search_query:
        search_text = (query or "").strip()
        if search_text:
            all_terms = list(st.session_state.engine.indexer.index['content'].keys())
            suggest_items = [t for t in all_terms if t.startswith(search_text.lower())][:6]
            icon = "🔍"
        else:
            suggest_items = st.session_state.recent_searches[:10]

    if suggest_items:
        items_js = json.dumps(suggest_items)
        st.markdown(f"""
            <script>
            (function() {{
                const doc = (window.parent && window.parent.document) ? window.parent.document : document;
                const input = doc.querySelector('input[placeholder="Search anything..."]');
                const container = doc.querySelector('.tangen-search-container');
                if (!input || !container) return;

                // Remove old dropdown
                const oldList = doc.querySelector('#suggestions-list');
                if (oldList) oldList.remove();

                const items = {items_js};
                const list = doc.createElement('div');
                list.id = 'suggestions-list';
                list.className = 'dropdown-box';
                list.role = 'listbox';
                list.style.display = 'block'; 
                
                items.forEach((item) => {{
                    const el = doc.createElement('div');
                    el.className = 'suggestion-item';
                    el.innerHTML = `{icon} ${{item}}`;
                    el.addEventListener('mousedown', (e) => {{
                        e.preventDefault();
                        input.value = item;
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        const submitBtn = doc.querySelector('#tangen-hidden-submit-btn button');
                        if (submitBtn) submitBtn.click();
                    }});
                    list.appendChild(el);
                }});
                container.appendChild(list);

                input.onfocus = () => {{ 
                    if (doc.querySelector('#suggestions-list'))
                        doc.querySelector('#suggestions-list').style.display = 'block'; 
                }};
                input.onblur = () => {{ 
                    setTimeout(() => {{ 
                        const l = doc.querySelector('#suggestions-list');
                        if (l) l.style.display = 'none'; 
                    }}, 200); 
                }};
            }})();
            </script>
        """, unsafe_allow_html=True)

# 5. Search Execution & Results (submitted query only)
if st.session_state.search_query:
    current_query = st.session_state.search_query
    print(f"DEBUG: Executing search for: '{current_query}'")
    st.markdown('<div style="margin-top: 30px;">', unsafe_allow_html=True)
    all_results = st.session_state.engine.search(current_query, top_k=50)
    print(f"DEBUG: Search returned {len(all_results)} results.")
    
    if not all_results:
        st.info("No documents match your query.")
    else:
        # AI Synthesis
        if st.session_state.ai_mode:
            with st.spinner("AI Synthesis in progress..."):
                synthesis = st.session_state.ai_agent.synthesize(current_query, all_results)
                st.markdown(f'<div style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 5px solid #1a73e8; margin-bottom: 30px;">{synthesis}</div>', unsafe_allow_html=True)
        
        # Result List
        st.markdown(f'<div style="color: #70757a; font-size: 0.875rem; margin-bottom: 20px;">About {len(all_results)} results</div>', unsafe_allow_html=True)
        
        # Simple pagination for demonstration
        for res in all_results[:10]:
            st.markdown(f"""
            <div class="result-card">
                <span class="result-url">{res['url']}</span>
                <a href="{res['url']}" target="_blank" class="result-title">{res['title']}</a>
                <div class="result-snippet">{res['snippet']}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
