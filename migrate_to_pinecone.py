import chromadb
from pinecone import Pinecone
from dotenv import load_dotenv
import os
from tqdm import tqdm
import numpy as np

# Load environment variables
load_dotenv()

def migrate_to_pinecone():
    # Initialize Pinecone
    pc = Pinecone(
        api_key=os.getenv('PINECONE_API_KEY')
    )
    
    # Connect to Pinecone index
    index_name = os.getenv('PINECONE_INDEX_NAME')
    index = pc.Index(index_name)
    
    # Initialize ChromaDB
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_collection("ds_knowledge_base")
    
    # Get all documents from ChromaDB
    results = collection.get(
        include=['embeddings', 'documents', 'metadatas']
    )
    
    # Prepare batches for Pinecone
    batch_size = 100
    for i in tqdm(range(0, len(results['ids']), batch_size)):
        batch_ids = results['ids'][i:i + batch_size]
        batch_embeddings = results['embeddings'][i:i + batch_size]
        batch_documents = results['documents'][i:i + batch_size]
        
        # Prepare vectors for Pinecone
        vectors = []
        for id_, embedding, text in zip(batch_ids, batch_embeddings, batch_documents):
            vectors.append({
                'id': id_,
                'values': embedding,
                'metadata': {'text': text}
            })
        
        # Upsert to Pinecone
        index.upsert(vectors=vectors)
    
    print(f"Migration complete! Migrated {len(results['ids'])} documents to Pinecone")

if __name__ == "__main__":
    migrate_to_pinecone()