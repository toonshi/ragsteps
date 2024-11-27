from transformers import DPRQuestionEncoder, DPRQuestionEncoderTokenizer
import torch
from pinecone import Pinecone
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables
load_dotenv()

def get_question_embedding(question):
    # Initialize DPR question encoder
    question_encoder = DPRQuestionEncoder.from_pretrained(
        "facebook/dpr-question_encoder-single-nq-base"
    )
    question_tokenizer = DPRQuestionEncoderTokenizer.from_pretrained(
        "facebook/dpr-question_encoder-single-nq-base"
    )
    
    # Create question embedding
    question_inputs = question_tokenizer(question, return_tensors="pt")
    question_embedding = question_encoder(**question_inputs).pooler_output
    return question_embedding[0].detach().numpy()

def query_knowledge_base(question, top_k=3, use_gpt_knowledge=True):
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        
        # Connect to index
        index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))
        
        # Get question embedding
        question_embedding = get_question_embedding(question)
        
        # Query Pinecone
        results = index.query(
            vector=question_embedding.tolist(),
            top_k=top_k,
            include_metadata=True
        )
        
        # Extract contexts
        contexts = [match.metadata['text'] for match in results.matches]
        
        # Create prompt for GPT based on mode
        if use_gpt_knowledge:
            prompt = f"""Answer the question based on the provided contexts. If the contexts don't contain enough information, you can also use your general knowledge to provide a complete answer. Always prioritize information from the contexts when available, but feel free to supplement with additional relevant information.

Question: {question}

Relevant contexts from documents:
{chr(10).join(f'Context {i+1}: {context}' for i, context in enumerate(contexts))}

Instructions:
1. First, use information from the provided contexts when available
2. If the contexts don't fully answer the question, supplement with your general knowledge
3. If using general knowledge, clearly indicate which parts of your answer come from the documents and which are from your general knowledge
4. Be helpful and informative while maintaining accuracy

Answer:"""
        else:
            prompt = f"""Answer the question based ONLY on the provided contexts. If the contexts don't contain enough information to answer the question, simply state that you cannot answer based on the available information.

Question: {question}

Relevant contexts from documents:
{chr(10).join(f'Context {i+1}: {context}' for i, context in enumerate(contexts))}

Instructions:
1. Only use information from the provided contexts
2. If the contexts don't contain enough information, say so
3. Do not use any external knowledge
4. Be accurate and precise

Answer:"""
        
        # Get response from GPT
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers questions based on provided document contexts." + (" You can also use your general knowledge when appropriate." if use_gpt_knowledge else " You must ONLY use information from the provided contexts.")},
            {"role": "user", "content": prompt}
        ]
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return {
            'answer': response.choices[0].message.content,
            'contexts': contexts,
            'error': None
        }
    except Exception as e:
        return {
            'answer': None,
            'contexts': None,
            'error': str(e)
        }