from transformers import (
    DPRQuestionEncoder,
    DPRQuestionEncoderTokenizer,
)
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import pinecone
import os
import torch
import numpy as np

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

def get_relevant_context(queries, index, question_encoder, question_tokenizer, k=3):
    """Retrieve relevant context from Pinecone based on the queries using DPR"""
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
    
    # Average the embeddings from all queries
    query_embedding = np.mean(all_embeddings, axis=0)
    
    # Query Pinecone
    results = index.query(
        vector=query_embedding.tolist(),
        top_k=k,
        include_metadata=True
    )
    
    # Extract and return contexts
    contexts = [result.metadata['text'] for result in results.matches]
    return contexts

def setup_rag():
    """Initialize RAG components"""
    # Initialize Pinecone
    pinecone.init(
        api_key=os.getenv('PINECONE_API_KEY'),
        environment=os.getenv('PINECONE_ENV')
    )
    
    # Connect to index
    index_name = os.getenv('PINECONE_INDEX_NAME')
    index = pinecone.Index(index_name)
    
    # Initialize DPR components
    tokenizer = DPRQuestionEncoderTokenizer.from_pretrained("facebook/dpr-question_encoder-single-nq-base")
    model = DPRQuestionEncoder.from_pretrained("facebook/dpr-question_encoder-single-nq-base")
    
    # Initialize LLM
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0
    )
    
    return index, model, tokenizer, llm

def query_documents(question):
    """Main function to query documents using RAG with DPR and query expansion"""
    # Setup components
    index, question_encoder, question_tokenizer, llm = setup_rag()
    
    # Expand the query
    expanded_queries = expand_query(question, llm)
    
    # Get relevant contexts
    contexts = get_relevant_context(expanded_queries, index, question_encoder, question_tokenizer)
    
    # Create prompt for final answer
    context_text = "\n".join(contexts)
    prompt = f"""Based on the following contexts, answer the question. If you cannot find the answer in the contexts, say "I cannot find the answer in the provided context."

Contexts:
{context_text}

Question: {question}

Answer:"""
    
    # Generate final answer
    response = llm.invoke(prompt)
    return response.content

if __name__ == "__main__":
    while True:
        # Get user question
        question = input("\nEnter your question (or 'quit' to exit): ")
        
        if question.lower() == 'quit':
            break
            
        # Get answer
        answer = query_documents(question)
        print("\nAnswer:", answer)
