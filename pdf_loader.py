from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import (
    DPRContextEncoder,
    DPRContextEncoderTokenizer,
)
import os
import torch
from pinecone import Pinecone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_pdfs_to_chroma(pdf_directory):
    # Initialize Pinecone
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))
    
    # Initialize DPR context encoder
    context_encoder = DPRContextEncoder.from_pretrained(
        "facebook/dpr-ctx_encoder-single-nq-base"
    )
    context_tokenizer = DPRContextEncoderTokenizer.from_pretrained(
        "facebook/dpr-ctx_encoder-single-nq-base"
    )
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    # Process each PDF in the directory
    for filename in os.listdir(pdf_directory):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_directory, filename)
            print(f"Processing {filename}...")
            
            # Load PDF
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            
            # Split text into chunks
            chunks = text_splitter.split_documents(pages)
            
            # Process chunks in batches
            batch_size = 100
            vectors = []
            
            # Process each chunk
            for i, chunk in enumerate(chunks):
                # Create DPR embeddings
                context_inputs = context_tokenizer(
                    chunk.page_content,
                    max_length=512,
                    padding=True,
                    truncation=True,
                    return_tensors="pt"
                )
                with torch.no_grad():
                    embedding = context_encoder(**context_inputs).pooler_output[0]
                
                # Prepare vector for Pinecone
                vector = {
                    "id": f"{filename}_chunk_{i}",
                    "values": embedding.numpy().tolist(),
                    "metadata": {
                        "text": chunk.page_content,
                        "source": filename,
                        "page": chunk.metadata.get('page', 0)
                    }
                }
                vectors.append(vector)
                
                # Upload batch if it's full or this is the last chunk
                if len(vectors) >= batch_size or i == len(chunks) - 1:
                    index.upsert(vectors=vectors)
                    vectors = []  # Clear the batch
            
            print(f"Completed processing {filename}")
    
    print("All PDFs have been processed and stored in Pinecone!")

if __name__ == "__main__":
    # Use the data directory where PDFs are stored
    pdf_dir = "./data"
    load_pdfs_to_chroma(pdf_dir)