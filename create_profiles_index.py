from pinecone import Pinecone
import os
from dotenv import load_dotenv

def create_profiles_index():
    # Load environment variables
    load_dotenv()
    
    # Initialize Pinecone
    pc = Pinecone()
    
    # Check if profiles index exists
    if "profiles" not in pc.list_indexes().names():
        # Create the profiles index
        pc.create_index(
            name="profiles",
            dimension=384,  # dimension for all-MiniLM-L6-v2
            metric="cosine",
            spec={
                "pod": {
                    "environment": "gcp-starter"  # Match your existing environment
                }
            }
        )
        print("Created new 'profiles' index")
    else:
        print("'profiles' index already exists")

if __name__ == "__main__":
    create_profiles_index()
