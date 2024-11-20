import streamlit as st
from rag_query_streamlit import query_knowledge_base
from pdf_loader import load_pdfs_to_chroma
import os
from dotenv import load_dotenv
import time
import shutil
from pinecone import Pinecone

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Study Rug",
    page_icon=None,
    layout="wide"
)

# Title
st.title("Study Rug")

# Initialize session states
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False

if 'use_gpt_knowledge' not in st.session_state:
    st.session_state.use_gpt_knowledge = True

# Create two columns: chat and sidebar
chat_col, sidebar_col = st.columns([2, 1])

with chat_col:
    # Chat interface
    st.write("### Chat with your documents")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = query_knowledge_base(prompt, use_gpt_knowledge=st.session_state.use_gpt_knowledge)
                if response['error']:
                    error_message = f"⚠️ Error: {response['error']}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
                else:
                    st.markdown(response['answer'])
                    st.session_state.messages.append({"role": "assistant", "content": response['answer']})

with sidebar_col:
    st.sidebar.title("Document Management")
    
    # Knowledge Mode Toggle
    st.sidebar.markdown("### Knowledge Mode")
    st.session_state.use_gpt_knowledge = st.sidebar.toggle(
        "Use GPT Knowledge",
        value=st.session_state.use_gpt_knowledge,
        help="Toggle between using only document knowledge or allowing GPT to use its general knowledge"
    )
    
    # Upload documents
    uploaded_files = st.sidebar.file_uploader(
        "Upload PDF documents",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more PDF files to add to your knowledge base"
    )
    
    if uploaded_files:
        try:
            # Create data directory if it doesn't exist
            os.makedirs("./data", exist_ok=True)
            
            # Save and process uploaded files
            with st.sidebar.spinner("Processing documents..."):
                for uploaded_file in uploaded_files:
                    file_path = os.path.join("./data", uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                
                # Process all files in the directory
                load_pdfs_to_chroma("./data")
                
            st.sidebar.success("Documents processed successfully!")
            st.experimental_rerun()
            
        except Exception as e:
            st.sidebar.error(f"Error processing documents: {str(e)}")
    
    # List and manage existing documents
    st.sidebar.markdown("### Current Documents")
    docs_path = "./data"
    if os.path.exists(docs_path):
        docs = [f for f in os.listdir(docs_path) if f.endswith('.pdf')]
        if docs:
            for doc in docs:
                col1, col2 = st.sidebar.columns([3, 1])
                with col1:
                    st.write(f"📄 {doc}")
                with col2:
                    if st.button("🗑️", key=f"delete_{doc}"):
                        try:
                            # Remove file
                            os.remove(os.path.join(docs_path, doc))
                            # Remove from Pinecone
                            pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
                            index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))
                            # Delete vectors with matching metadata
                            index.delete(filter={"source": doc})
                            st.sidebar.success(f"Deleted {doc}")
                            st.experimental_rerun()
                        except Exception as e:
                            st.sidebar.error(f"Error deleting {doc}: {str(e)}")
        else:
            st.sidebar.info("No documents uploaded yet.")
    
    # Controls section
    st.sidebar.markdown("### Controls")
    
    # Clear chat button
    if st.sidebar.button("Clear Chat History", help="Clear all chat messages"):
        st.session_state.messages = []
        st.experimental_rerun()
    
    # Clear all documents button
    if st.sidebar.button("Clear All Documents", help="Remove all documents from the knowledge base"):
        try:
            # Clear data directory
            if os.path.exists(docs_path):
                shutil.rmtree(docs_path)
                os.makedirs(docs_path)
            
            # Clear Pinecone index
            pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
            index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))
            index.delete(delete_all=True)
            
            st.sidebar.success("All documents cleared!")
            st.experimental_rerun()
        except Exception as e:
            st.sidebar.error(f"Error clearing documents: {str(e)}")
    
    # Show contexts from last query
    if st.session_state.messages and 'response' in locals() and response.get('contexts'):
        st.sidebar.markdown("### Source Contexts")
        for i, context in enumerate(response['contexts'], 1):
            with st.sidebar.expander(f"Context {i}"):
                st.markdown(context)

# # Footer
# st.markdown("---")
# st.markdown("Thanks for checking it out!")