from transformers import DPRQuestionEncoder, DPRQuestionEncoderTokenizer
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import chromadb
from dotenv import load_dotenv
import os
import torch
import numpy as np
import streamlit as st

# Load environment variables
load_dotenv()

def expand_query(query, llm):
    """Generate multiple variations of the query for better retrieval"""
    template = """Generate 3 different versions of the following question that mean the same thing. 
    Format them as a comma-separated list.
    
    Question: {question}
    
    Different versions:"""
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"]
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    expanded = chain.run(question=query)
    # Split the result and add the original query
    queries = [query] + [q.strip() for q in expanded.split(',')]
    return queries

def get_relevant_context(queries, collection, question_encoder, question_tokenizer, k=3):
    """Retrieve relevant context from ChromaDB based on the queries using DPR"""
    # Create embeddings for all queries
    all_embeddings = []
    for query in queries:
        inputs = question_tokenizer(
            query,
            max_length=512,
            padding=True,
            truncation=True,
            return_tensors="pt"
        )
        with torch.no_grad():
            embedding = question_encoder(**inputs).pooler_output[0]
            all_embeddings.append(embedding.numpy().tolist())
    
    # Query ChromaDB with all embeddings
    all_results = []
    for embedding in all_embeddings:
        results = collection.query(
            query_embeddings=[embedding],
            n_results=k
        )
        all_results.extend(zip(results['documents'][0], results['metadatas'][0]))
    
    # Remove duplicates while preserving order
    seen = set()
    unique_results = []
    for doc, meta in all_results:
        if doc not in seen:
            seen.add(doc)
            unique_results.append((doc, meta))
    
    # Format context with sources
    context_parts = []
    for doc, meta in unique_results[:k]:  # Take top k unique results
        source = meta['source']
        page = meta['page']
        context_parts.append(f"From {source} (Page {page}):\n{doc}")
    
    return "\n\n".join(context_parts)

def setup_rag():
    """Initialize RAG components"""
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection("ds_knowledge_base")
    
    # Initialize DPR question encoder
    question_encoder = DPRQuestionEncoder.from_pretrained(
        "facebook/dpr-question_encoder-single-nq-base"
    )
    question_tokenizer = DPRQuestionEncoderTokenizer.from_pretrained(
        "facebook/dpr-question_encoder-single-nq-base"
    )
    
    # Initialize LLM
    openai_api_key = st.secrets["OPENAI_API_KEY"]  # Make sure to set this in your Streamlit secrets

    # Initialize OpenAI model
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        openai_api_key=openai_api_key  # Use the API key from Streamlit secrets
    )
    
    # Create prompt template
    template = """You are a helpful assistant that provides accurate information based on the given context.
    Use the following context to answer the question. If you can't find the answer in the context, say so.
    Don't make up information.

    Context:
    {context}

    Question: {question}

    Answer: """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )
    
    # Create chain
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Return all components
    return collection, question_encoder, question_tokenizer, llm, chain

def query_documents(question):
    """Main function to query documents using RAG with DPR and query expansion"""
    # Set up RAG components
    collection, question_encoder, question_tokenizer, llm, chain = setup_rag()
    
    # Expand the query
    expanded_queries = expand_query(question, llm)
    print("\nExpanded queries:", expanded_queries)
    
    # Get relevant context using all queries
    context = get_relevant_context(expanded_queries, collection, question_encoder, question_tokenizer)
    
    # Generate answer
    response = chain.run(context=context, question=question)
    
    return response

if __name__ == "__main__":
    while True:
        # Get user question
        question = input("\nEnter your question (or 'quit' to exit): ")
        
        if question.lower() == 'quit':
            print("Goodbye!")
            break
        
        try:
            # Get response
            answer = query_documents(question)
            print("\nAnswer:", answer)
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Make sure you have set your OPENAI_API_KEY in the .env file")
