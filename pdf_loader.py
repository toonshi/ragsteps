from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import (
    DPRContextEncoder,
    DPRContextEncoderTokenizer,
)
import chromadb
import os
import torch

def load_pdfs_to_chroma(pdf_directory):
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(
        name="ds_knowledge_base",
        metadata={"description": "Knowledge base for data science content"}
    )
    
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
                
                # Add to ChromaDB
                collection.add(
                    documents=[chunk.page_content],
                    embeddings=[embedding.numpy().tolist()],
                    metadatas=[{
                        "source": filename,
                        "page": chunk.metadata.get('page', 0),
                        "chunk_id": f"{filename}_chunk_{i}"
                    }],
                    ids=[f"{filename}_chunk_{i}"]
                )
            
            print(f"Completed processing {filename}")
    
    print("All PDFs have been processed and stored in the database!")

if __name__ == "__main__":
    # Use the data directory where PDFs are stored
    pdf_dir = "./data"
    load_pdfs_to_chroma(pdf_dir)