import sys
import os
import streamlit as st

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from crawler import DocumentLoader
from search import SearchEngine

# Page configuration
st.set_page_config(page_title="OmniSearch", page_icon="🔍", layout="wide")

# Initialize Engine in session state so index stays persistent across interaction
if "engine" not in st.session_state:
    st.session_state.engine = SearchEngine()
    st.session_state.loader = DocumentLoader()
    
    # Preload local sample docs silently
    sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_docs")
    local_docs = st.session_state.loader.load_local_documents(sample_path)
    if local_docs:
        for doc_id, text in local_docs.items():
            st.session_state.engine.add_document(doc_id, text)

# Inject Custom CSS for Premium Look
st.markdown("""
<style>
    /* Dark Theme & Premium Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
    }
    
    /* Hero Section Styling */
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #3b82f6, #9333ea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding-top: 2rem;
        margin-bottom: -1rem;
        letter-spacing: -1.5px;
    }
    
    .hero-subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.2rem;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    /* Glassmorphic Search Result Cards */
    .result-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    
    .result-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border: 1px solid rgba(59, 130, 246, 0.4);
    }
    
    .result-title {
        color: #60a5fa;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .result-score {
        background: rgba(59, 130, 246, 0.15);
        color: #93c5fd;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    
    .result-snippet {
        color: #cbd5e1;
        font-size: 1rem;
        line-height: 1.6;
        margin-top: 10px;
    }
    
    /* Premium Sidebar overlay */
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.6) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
    }
</style>
""", unsafe_allow_html=True)

# Main Header Design
st.markdown('<div class="hero-title">OmniSearch</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">High-Performance TF-IDF Intelligence</div>', unsafe_allow_html=True)

# Sidebar for Operations/Crawling
with st.sidebar:
    st.header("⚙️ Indexing Engine")
    st.markdown(f"**Total Documents Available:** \n# `{st.session_state.engine.indexer.get_total_documents()}`", unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("🌐 Crawl Webpage")
    url_to_crawl = st.text_input("Deploy Web Crawler", placeholder="https://example.com")
    if st.button("Crawl & Index", type="primary", use_container_width=True):
        if url_to_crawl:
            with st.spinner("Executing crawler..."):
                docs = st.session_state.loader.crawl_webpage(url_to_crawl)
                if docs:
                    for url_id, text in docs.items():
                        st.session_state.engine.add_document(url_id, text)
                    st.success(f"Successfully processed {url_to_crawl}")
                    st.rerun() # Refresh page state to show new document count
                else:
                    st.error("Crawler failed or found empty webpage.")
        else:
            st.warning("Provide a valid target URL.")
            
    st.divider()
    
    st.subheader("📁 Ingest Local Data")
    folder_path = st.text_input("Relative Directory", value="data/sample_docs")
    if st.button("Load Local Content", use_container_width=True):
        if folder_path:
            full_path = os.path.join(os.path.dirname(__file__), folder_path)
            with st.spinner("Processing file structure..."):
                local_docs = st.session_state.loader.load_local_documents(full_path)
                if local_docs:
                    for doc_id, text in local_docs.items():
                        st.session_state.engine.add_document(doc_id, text)
                    st.success(f"Ingested {len(local_docs)} static documents.")
                    st.rerun()
                else:
                    st.error("No valid .txt assets found.")

# Main Search Interaction Area
search_col1, search_col2, search_col3 = st.columns([1, 2, 1])

with search_col2:
    query = st.text_input("Initiate Query", placeholder="What do you want to find?", label_visibility="collapsed")
    
    if query:
        # Retrieve results
        results = st.session_state.engine.search(query, top_k=10)
        
        st.write(f"Yielded {len(results)} exact or partial matches for **'{query}'**")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if not results:
            st.info("No matching content indexed. Try modifying your search criteria.")
        else:
            for doc_id, score, snippet in results:
                clean_snippet = snippet.replace('\n', ' ')
                
                # Dynamic HTML for Premium Result Card
                card_html = f"""
                <div class="result-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="result-title">{doc_id}</span>
                        <span class="result-score">Relevance Score: {score:.4f}</span>
                    </div>
                    <div class="result-snippet">{clean_snippet}</div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
