import streamlit as st
from rag_query_streamlit import query_knowledge_base
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="RAG Knowledge Base",
    page_icon=None,
    layout="wide"
)

# Title
st.title("RAG Knowledge Base")

# Initialize session state for conversation history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Initialize setup state
if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False

if not st.session_state.setup_complete:
    progress = st.progress(0)
    status = st.empty()
    
    try:
        status.info("Initializing system...")
        progress.progress(30)
        time.sleep(1)
        
        status.info("Checking Pinecone connection...")
        progress.progress(60)
        time.sleep(1)
        
        status.info("Finalizing setup...")
        progress.progress(100)
        time.sleep(1)
        
        status.success("System ready!")
        st.session_state.setup_complete = True
        
    except Exception as e:
        status.error(f"Setup failed: {str(e)}")
        st.stop()

# Create two columns
col1, col2 = st.columns([3, 1])

with col1:
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
                response = query_knowledge_base(prompt)
                if response['error']:
                    error_message = f"⚠️ Error: {response['error']}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
                else:
                    st.markdown(response['answer'])
                    st.session_state.messages.append({"role": "assistant", "content": response['answer']})

with col2:
    st.sidebar.title("Controls")
    
    # Clear chat button
    if st.sidebar.button("Clear Chat History"):
        st.session_state.messages = []
        st.experimental_rerun()
    
    # Show contexts from last query
    if st.session_state.messages and 'response' in locals() and response.get('contexts'):
        st.sidebar.title("Source Contexts")
        for i, context in enumerate(response['contexts'], 1):
            with st.sidebar.expander(f"Context {i}"):
                st.markdown(context)

# Footer
st.markdown("---")
st.markdown("Powered by DPR, Pinecone, and GPT-3.5")