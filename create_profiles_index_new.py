from pinecone import Pinecone
import os
from dotenv import load_dotenv
import time

def delete_profiles_index():
    # Load environment variables
    load_dotenv()
    
    # Initialize Pinecone
    pc = Pinecone()
    
    # Check if profiles index exists
    if "profiles" in pc.list_indexes().names():
        print("Deleting existing 'profiles' index...")
        pc.delete_index("profiles")
        # Wait a bit to ensure the index is fully deleted
        time.sleep(10)
        print("Existing index deleted")

def create_profiles_index():
    # Load environment variables
    load_dotenv()
    
    # Initialize Pinecone
    pc = Pinecone()
    
    # Check if profiles index exists
    if "profiles" not in pc.list_indexes().names():
        # Create the profiles index
        print("Creating new 'profiles' index...")
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
    delete_profiles_index()  # First delete the existing index
    create_profiles_index()  # Then create a new one
