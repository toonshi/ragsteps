import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_pinecone_index():
    # Initialize Pinecone
    pc = Pinecone(
        api_key=os.getenv('PINECONE_API_KEY')
    )
    
    # Check if index already exists
    index_name = os.getenv('PINECONE_INDEX_NAME')
    if index_name not in pc.list_indexes().names():
        # Create index
        pc.create_index(
            name=index_name,
            dimension=768,  # DPR dimension
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'  # Free tier supported region
            )
        )
        print(f"Created new index: {index_name}")
    else:
        print(f"Index {index_name} already exists")

if __name__ == "__main__":
    create_pinecone_index()