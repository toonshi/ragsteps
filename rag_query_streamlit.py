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

def query_knowledge_base(question, top_k=3):
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
        
        # Create prompt for GPT
        prompt = f"""Based on the following contexts, answer the question. If the answer cannot be found in the contexts, say "I cannot answer this based on the available information."

Question: {question}

Relevant contexts:
{chr(10).join(f'Context {i+1}: {context}' for i, context in enumerate(contexts))}

Answer the question in a clear and concise manner. If you find multiple relevant pieces of information in the contexts, synthesize them into a coherent response."""
        
        # Get response from GPT
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context. Be accurate and concise."},
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

if __name__ == "__main__":
    while True:
        # Get user question
        question = input("\nEnter your question (or 'quit' to exit): ")
        
        if question.lower() == 'quit':
            print("Goodbye!")
            break
        
        try:
            # Get response
            answer = query_knowledge_base(question)
            print("\nAnswer:", answer['answer'])
            print("\nContexts:", answer['contexts'])
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Make sure you have set your PINECONE_API_KEY and OPENAI_API_KEY in the .env file")
