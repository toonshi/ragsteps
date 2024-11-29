import pinecone
from chromadb.config import PersistentClient
from dotenv import load_dotenv
import os
from tqdm import tqdm
import numpy as np

# Load environment variables
load_dotenv()

def migrate_to_pinecone():
    # Initialize Pinecone
    pinecone.init(
        api_key=os.getenv('PINECONE_API_KEY'),  # Pinecone API Key
        environment=os.getenv('PINECONE_ENVIRONMENT')  # Environment (e.g., 'us-west1-gcp')
    )
    
    # Connect to Pinecone index
    index_name = os.getenv('PINECONE_INDEX_NAME')
    if index_name not in pinecone.list_indexes():
        raise ValueError(f"Index '{index_name}' not found in Pinecone. Please create it first.")
    index = pinecone.Index(index_name)
    
    # Initialize ChromaDB
    chroma_client = PersistentClient(path="./chroma_db")
    collection = chroma_client.get_collection("ds_knowledge_base")
    
    # Retrieve all data from ChromaDB
    results = collection.get(
        include=['embeddings', 'documents', 'metadatas']
    )
    
    # Validate data
    embeddings = results['embeddings']
    documents = results['documents']
    metadatas = results['metadatas']
    ids = results['ids']
    
    if len(ids) != len(embeddings) or len(ids) != len(documents):
        raise ValueError("Mismatch between embeddings, documents, and IDs in ChromaDB data.")
    
    # Prepare and migrate in batches
    batch_size = 100
    for i in tqdm(range(0, len(ids), batch_size), desc="Migrating batches to Pinecone"):
        batch_ids = ids[i:i + batch_size]
        batch_embeddings = embeddings[i:i + batch_size]
        batch_documents = documents[i:i + batch_size]
        batch_metadatas = metadatas[i:i + batch_size]
        
        # Prepare vectors for Pinecone
        vectors = []
        for id_, embedding, document, metadata in zip(batch_ids, batch_embeddings, batch_documents, batch_metadatas):
            metadata = metadata or {}
            metadata['text'] = document  # Add document text to metadata
            vectors.append((id_, embedding, metadata))
        
        # Upsert vectors to Pinecone
        index.upsert(vectors=vectors)
    
    print(f"Migration complete! Migrated {len(ids)} documents to Pinecone.")

if __name__ == "__main__":
    try:
        migrate_to_pinecone()
    except Exception as e:
        print(f"An error occurred: {e}")
