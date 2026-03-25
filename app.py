import sys
import os
import streamlit as st

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from crawler import DocumentLoader
from search import SearchEngine

# Page configuration
st.set_page_config(page_title="TangenAI", page_icon="🔍", layout="wide")

# Initialize Engine in session state so index stays persistent across interaction
if "engine" not in st.session_state:
    st.session_state.engine = SearchEngine()
    st.session_state.loader = DocumentLoader()
    
    # Preload local sample docs silently
    sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_docs")
    local_docs = st.session_state.loader.load_local_documents(sample_path)
    if local_docs:
        for doc_id, doc_data in local_docs.items():
            st.session_state.engine.add_document(doc_id, doc_data)

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
</style>
""", unsafe_allow_html=True)

# Main Header Design (Google Colors)
st.markdown('<div class="hero-title"><span class="g-blue">T</span><span class="g-red">a</span><span class="g-yellow">n</span><span class="g-blue">g</span><span class="g-green">e</span><span class="g-red">n</span><span class="g-blue">A</span><span class="g-green">I</span></div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">High-Performance TF-IDF Intelligence</div>', unsafe_allow_html=True)

# Sidebar for Operations/Crawling (Styled as a tool drawer)
with st.sidebar:
    st.header("⚙️ Search Tools")
    st.write(f"**Index size:** {st.session_state.engine.indexer.get_total_documents()} documents")
    
    st.divider()
    
    st.subheader("🌐 Add Source")
    url_to_crawl = st.text_input("Enter URL", placeholder="https://en.wikipedia.org...")
    if st.button("Index Webpage", use_container_width=True):
        if url_to_crawl:
            with st.spinner("Indexing..."):
                docs = st.session_state.loader.crawl_webpage(url_to_crawl)
                if docs:
                    for url_id, doc_data in docs.items():
                        st.session_state.engine.add_document(url_id, doc_data)
                    st.success(f"Indexed {url_to_crawl}")
                    st.rerun()
        else:
            st.warning("Provide a URL.")
            
    st.divider()
    
    st.subheader("📁 Local Assets")
    folder_path = st.text_input("Relative path", value="data/sample_docs")
    if st.button("Scan Directory", use_container_width=True):
        if folder_path:
            full_path = os.path.join(os.path.dirname(__file__), folder_path)
            with st.spinner("Scanning..."):
                local_docs = st.session_state.loader.load_local_documents(full_path)
                if local_docs:
                    for doc_id, doc_data in local_docs.items():
                        st.session_state.engine.add_document(doc_id, doc_data)
                    st.success(f"Indexed {len(local_docs)} files.")
                    st.rerun()

# Main Search Interaction Area
search_col1, search_col2, search_col3 = st.columns([1, 4, 1])

# Set a version for the search cache for Semantic Intelligence update
SEARCH_CACHE_VERSION = "v6_semantic_intelligence"

@st.cache_data(show_spinner=False)
def perform_search(query_str: str, doc_count: int, version: str):
    return st.session_state.engine.search(query_str, top_k=50)

def get_suggestion(query_str: str):
    import difflib
    words = st.session_state.engine.indexer.index.keys()
    query_words = query_str.lower().split()
    suggestions = []
    for word in query_words:
        matches = difflib.get_close_matches(word, words, n=1, cutoff=0.8)
        suggestions.append(matches[0] if matches else word)
    
    suggested_query = " ".join(suggestions)
    return suggested_query if suggested_query != query_str.lower() else None

if "page_number" not in st.session_state:
    st.session_state.page_number = 1

with search_col2:
    query = st.text_input("Initiate Query", placeholder="Search anything...", label_visibility="collapsed")
    
    if query:
        # Spell check / Did you mean
        suggestion = get_suggestion(query)
        if suggestion:
            st.markdown(f'<div style="color: #d93025; font-size: 0.95rem; margin-bottom: 25px; margin-left: 20px;">Did you mean: <span style="color: #1a0dab; font-style: italic; font-weight: 400; cursor: pointer; text-decoration: underline;">{suggestion}</span></div>', unsafe_allow_html=True)

        # Retrieve results
        all_results = perform_search(query, st.session_state.engine.indexer.get_total_documents(), SEARCH_CACHE_VERSION)
        
        if not all_results:
            st.info("No results found.")
        else:
            # 1. Knowledge Panel (Hero Support)
            top_res = all_results[0]
            if top_res.get("is_hero") or top_res["score"] > 10:
                st.markdown(f'<h1 style="font-family: Product Sans; font-size: 2.5rem; margin-top: 1rem; margin-left: 20px;">{top_res["title"]}</h1>', unsafe_allow_html=True)
                st.markdown(f'<div style="color: #70757a; font-size: 0.9rem; margin-bottom: 20px; margin-left: 20px;">{top_res.get("facts", {}).get("Role", "Result")} • Overview</div>', unsafe_allow_html=True)
                
                # Knowledge Mesh (Hero View)
                hero_col1, hero_col2 = st.columns([2, 1])
                with hero_col1:
                    if top_res.get("image_url"):
                         st.image(top_res["image_url"], use_column_width=True)
                    st.markdown(f'<div style="font-size: 1.1rem; line-height: 1.6; margin-top: 15px; padding: 20px; background: #f8f9fa; border-radius: 12px; border: 1px solid #dfe1e5;">{top_res["snippet"]} <a href="{top_res["url"]}" target="_blank">Wikipedia</a></div>', unsafe_allow_html=True)
                
                with hero_col2:
                    # Fact Box
                    if top_res.get("facts"):
                        st.markdown('<div style="background: #f8f9fa; padding: 15px; border-radius: 12px; border: 1px solid #dfe1e5;">', unsafe_allow_html=True)
                        st.write("**About**")
                        for label, val in top_res["facts"].items():
                            st.markdown(f'<div style="font-size: 0.85rem; margin-bottom: 8px;"><b>{label}</b>: {val}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                st.divider()

            # 2. Standard Results List
            st.markdown(f'<div style="color: #70757a; font-size: 0.875rem; margin-bottom: 20px; margin-left: 20px;">About {len(all_results)} results</div>', unsafe_allow_html=True)
            
            # Pagination Logic
            results_per_page = 8
            total_pages = (len(all_results) + results_per_page - 1) // results_per_page
            start_idx = (st.session_state.page_number - 1) * results_per_page
            end_idx = start_idx + results_per_page
            results = all_results[start_idx:end_idx]

            for res in results:
                platform = res.get("platform", "Web")
                platform_class = f"badge-{platform.lower()}" if platform != "Web" else ""
                
                # Semantic Badge if hero/entity match
                is_hero = res.get("is_hero", False)
                semantic_badge = '<span class="platform-badge badge-semantic">✨ Semantic Match</span>' if is_hero else ''
                
                # Metadata string for social results
                meta_info = ""
                if platform == "Reddit":
                    meta_info = f" • r/{res.get('metadata', {}).get('subreddit')} • {res.get('metadata', {}).get('upvotes')} ↑"
                elif platform == "YouTube":
                    meta_info = f" • Video"
                
                badge_html = f'<div style="display: flex; align-items: center; gap: 4px;">{semantic_badge}<span class="platform-badge {platform_class}">{platform}</span></div>' if (platform != "Web" or is_hero) else ''
                
                img_tag = f'<img src="{res["image_url"]}" style="width: 92px; height: 92px; object-fit: cover; border-radius: 8px; margin-left: 20px; flex-shrink: 0;" />' if res.get("image_url") else ''
                
                card_html = f'<div class="result-container">' \
                            f'<div style="display: flex; justify-content: space-between; align-items: flex-start;">' \
                            f'<div style="flex-grow: 1;">' \
                            f'<div class="result-link-container">' \
                            f'<div style="display: flex; align-items: center; margin-bottom: 2px;">{badge_html}<span class="result-url">{res["url"]}</span></div>' \
                            f'<a href="{res["url"]}" target="_blank" style="text-decoration: none;">' \
                            f'<div class="result-title">{res["title"]}</div>' \
                            f'</a>' \
                            f'</div>' \
                            f'<div class="result-snippet">{res["snippet"]}<span style="color: #70757a; font-size: 0.85rem;">{meta_info}</span></div>' \
                            f'</div>' \
                            f'{img_tag}' \
                            f'</div>' \
                            f'</div>'
                st.markdown(card_html, unsafe_allow_html=True)
            
            # Pagination Controls
            if total_pages > 1:
                st.markdown('<div class="pagination-container" style="justify-content: flex-start; padding-left: 20px;">', unsafe_allow_html=True)
                cols = st.columns(total_pages + 2)
                for i in range(total_pages):
                    page = i + 1
                    if cols[i].button(f"{page}", key=f"page_{page}", type="secondary" if page != st.session_state.page_number else "primary"):
                        st.session_state.page_number = page
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
