import streamlit as st
from rag_query import setup_rag, expand_query, get_relevant_context
from pdf_loader import load_pdfs_to_chroma
import os
import shutil
from dotenv import load_dotenv
import time
import chromadb

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="RAG Knowledge Base",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .document-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .search-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .answer-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin-top: 2rem;
        border-left: 5px solid #4CAF50;
    }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .upload-section {
        border: 2px dashed #1E88E5;
        border-radius: 10px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: center;
    }
    .document-list {
        margin-top: 2rem;
    }
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Title with custom styling
st.markdown("""
    <h1 style='text-align: center; color: #1E88E5; margin-bottom: 2rem;'>
        📚 RAG Knowledge Base
    </h1>
""", unsafe_allow_html=True)

# Initialize session state
if 'setup_stage' not in st.session_state:
    st.session_state.setup_stage = 0

if 'rag_components' not in st.session_state:
    try:
        # Progress tracking with better visual feedback
        progress_container = st.container()
        with progress_container:
            progress = st.progress(0)
            status = st.empty()
        
        # Stage 0: Starting
        if st.session_state.setup_stage == 0:
            status.info("⚡ Initializing system...")
            progress.progress(10)
            time.sleep(1)
            st.session_state.setup_stage = 1
        
        # Stage 1: Downloading
        if st.session_state.setup_stage == 1:
            status.info("🔄 Loading AI models...")
            progress.progress(30)
            st.session_state.rag_components = setup_rag()
            st.session_state.setup_stage = 2
        
        # Stage 2: Finalizing
        if st.session_state.setup_stage == 2:
            status.info("🎯 Finalizing setup...")
            progress.progress(100)
            time.sleep(1)
            status.success("🚀 System ready!")
            st.session_state.setup_stage = 3
        
    except Exception as e:
        st.error(f"Setup error: {str(e)}")
        st.stop()

def delete_from_chroma(filename):
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection("ds_knowledge_base")
    collection.delete(where={"source": filename})

# Sidebar with modern document management
with st.sidebar:
    st.markdown("""
        <h2 style='text-align: center; color: #1E88E5;'>
            📁 Document Management
        </h2>
    """, unsafe_allow_html=True)
    
    # Upload section with better styling
    st.markdown("""
        <div class="upload-section">
            <h3 style='color: #424242;'>
                📤 Upload Documents
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Drop PDF files here",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more PDF documents to analyze"
    )
    
    if uploaded_files:
        try:
            os.makedirs("./data", exist_ok=True)
            
            with st.spinner("📑 Processing documents..."):
                pdf_paths = []
                progress_text = st.empty()
                progress_bar = st.progress(0)
                
                for i, uploaded_file in enumerate(uploaded_files):
                    progress = (i + 1) / len(uploaded_files)
                    progress_text.text(f"Processing {uploaded_file.name}...")
                    progress_bar.progress(progress)
                    
                    file_path = os.path.join("./data", uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    pdf_paths.append(file_path)
                
                if pdf_paths:
                    load_pdfs_to_chroma(pdf_paths, is_directory=False)
                    
            st.success("✨ Documents processed successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    # Document list with card-based design
    st.markdown("""
        <div class="document-list">
            <h3 style='color: #424242;'>
                📚 Current Documents
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    docs_path = "./data"
    if os.path.exists(docs_path):
        docs = [f for f in os.listdir(docs_path) if f.endswith('.pdf')]
        if docs:
            for doc in docs:
                with st.container():
                    st.markdown(f"""
                        <div class='document-card'>
                            <h4>{doc}</h4>
                        </div>
                    """, unsafe_allow_html=True)
                    col1, col2 = st.columns([4, 1])
                    with col2:
                        if st.button("🗑️", key=f"delete_{doc}", help=f"Delete {doc}"):
                            try:
                                os.remove(os.path.join(docs_path, doc))
                                delete_from_chroma(doc)
                                st.success(f"🗑️ Removed {doc}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
        else:
            st.info("📭 No documents uploaded yet")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Clear all with confirmation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear All", type="secondary", help="Remove all documents"):
            st.session_state.show_confirm = True
    
    with col2:
        if st.session_state.get('show_confirm', False):
            if st.button("⚠️ Confirm", type="primary"):
                try:
                    if os.path.exists(docs_path):
                        shutil.rmtree(docs_path)
                        os.makedirs(docs_path)
                    client = chromadb.PersistentClient(path="./chroma_db")
                    collection = client.get_collection("ds_knowledge_base")
                    collection.delete()
                    st.success("🧹 All documents cleared!")
                    st.session_state.show_confirm = False
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Main query interface with modern design
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.markdown("""
        <div class='search-container'>
            <h2 style='text-align: center; color: #1E88E5; margin-bottom: 1rem;'>
                🔍 Ask Questions
            </h2>
    """, unsafe_allow_html=True)
    
    query = st.text_input(
        "",
        placeholder="Ask anything about your documents...",
        help="Enter your question here"
    )

    if query and st.session_state.setup_stage == 3:
        try:
            with st.spinner("🤔 Analyzing documents..."):
                collection, question_encoder, question_tokenizer, llm, chain = st.session_state.rag_components
                expanded_queries = expand_query(query, llm)
                context = get_relevant_context(expanded_queries, collection, question_encoder, question_tokenizer)
                response = chain.run(context=context, question=query)
                
                st.markdown("""
                    <div class='answer-container'>
                        <h3 style='color: #4CAF50;'>💡 Answer:</h3>
                """, unsafe_allow_html=True)
                st.write(response)
                st.markdown("</div>", unsafe_allow_html=True)
                
                with st.expander("🔍 Search Details", expanded=False):
                    st.markdown("#### 🔄 Query Variations:")
                    for q in expanded_queries:
                        st.info(q)
                    st.markdown("#### 📑 Retrieved Context:")
                    st.markdown(context)
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)

# Modern footer
st.markdown("---")
st.markdown("""
    <div class='footer'>
        <p>
            RAG Knowledge Base System<br>
            Built with ❤️ using Streamlit + DPR + GPT
        </p>
    </div>
""", unsafe_allow_html=True)
