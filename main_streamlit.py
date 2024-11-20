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
st.set_page_config(page_title="RAG Knowledge Base", page_icon=None)

# Title
st.title("RAG Knowledge Base")

# Initialize session state
if 'setup_stage' not in st.session_state:
    st.session_state.setup_stage = 0

if 'rag_components' not in st.session_state:
    try:
        # Progress tracking
        progress = st.progress(0)
        status = st.empty()
        
        # Stage 0: Starting
        if st.session_state.setup_stage == 0:
            status.info("Starting model download...")
            progress.progress(10)
            time.sleep(1)
            st.session_state.setup_stage = 1
        
        # Stage 1: Downloading
        if st.session_state.setup_stage == 1:
            status.info("Downloading DPR model (this may take a few minutes)...")
            progress.progress(30)
            st.session_state.rag_components = setup_rag()
            st.session_state.setup_stage = 2
        
        # Stage 2: Finalizing
        if st.session_state.setup_stage == 2:
            status.info("Finalizing setup...")
            progress.progress(100)
            time.sleep(1)
            status.success("System ready!")
            st.session_state.setup_stage = 3
        
    except Exception as e:
        st.error(f"Setup error: {str(e)}")
        st.stop()

def delete_from_chroma(filename):
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection("ds_knowledge_base")
    # Delete all chunks associated with this file
    collection.delete(
        where={"source": filename}
    )

# Sidebar with document management
with st.sidebar:
    st.header("Document Management")
    
    # Document upload section
    st.subheader("Upload Documents")
    uploaded_files = st.file_uploader("Choose PDF files", type=['pdf'], accept_multiple_files=True)
    
    if uploaded_files:
        try:
            # Create data directory if it doesn't exist
            os.makedirs("./data", exist_ok=True)
            
            # Save and process uploaded files
            with st.spinner("Processing documents..."):
                pdf_paths = []
                for uploaded_file in uploaded_files:
                    # Save file
                    file_path = os.path.join("./data", uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    pdf_paths.append(file_path)
                
                # Update knowledge base with all new files
                if pdf_paths:
                    load_pdfs_to_chroma(pdf_paths, is_directory=False)
                    
            st.success("Documents added and vectorized successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Error processing documents: {str(e)}")
    
    # Document list and management
    st.subheader("Current Documents")
    docs_path = "./data"
    if os.path.exists(docs_path):
        docs = [f for f in os.listdir(docs_path) if f.endswith('.pdf')]
        if docs:
            for doc in docs:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"- {doc}")
                with col2:
                    if st.button("Delete", key=f"delete_{doc}"):
                        try:
                            # Remove file from filesystem
                            os.remove(os.path.join(docs_path, doc))
                            # Remove from ChromaDB
                            delete_from_chroma(doc)
                            st.success(f"Deleted {doc}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting {doc}: {str(e)}")
        else:
            st.info("No documents uploaded yet.")
    
    st.markdown("---")
    # Clear all documents
    if st.button("Clear All Documents", type="secondary"):
        try:
            # Remove all files
            if os.path.exists(docs_path):
                shutil.rmtree(docs_path)
                os.makedirs(docs_path)
            # Clear ChromaDB collection
            client = chromadb.PersistentClient(path="./chroma_db")
            collection = client.get_collection("ds_knowledge_base")
            collection.delete()
            st.success("All documents cleared!")
            st.rerun()
        except Exception as e:
            st.error(f"Error clearing documents: {str(e)}")

# Main query interface
st.markdown("### Ask Questions")
query = st.text_input("Enter your question:", placeholder="e.g., What are the key points about early intervention?")

if query and st.session_state.setup_stage == 3:
    try:
        with st.spinner("Finding answer..."):
            # Get components
            collection, question_encoder, question_tokenizer, llm, chain = st.session_state.rag_components
            
            # Process query
            expanded_queries = expand_query(query, llm)
            context = get_relevant_context(expanded_queries, collection, question_encoder, question_tokenizer)
            response = chain.run(context=context, question=query)
            
            # Show answer
            st.markdown("### Answer:")
            st.write(response)
            
            # Show details
            with st.expander("Search Details"):
                st.markdown("#### Query Variations:")
                for q in expanded_queries:
                    st.markdown(f"- {q}")
                st.markdown("#### Retrieved Context:")
                st.markdown(context)
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.caption("RAG Knowledge Base System | Built with Streamlit + DPR + GPT")
