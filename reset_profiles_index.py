from pinecone import Pinecone
import os
from dotenv import load_dotenv
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_profiles_index():
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize Pinecone
        logger.info("Connecting to Pinecone...")
        pc = Pinecone()
        
        # List current indexes
        current_indexes = pc.list_indexes().names()
        logger.info(f"Current indexes: {current_indexes}")
        
        # Delete if exists
        if "profiles" in current_indexes:
            logger.info("Deleting existing 'profiles' index...")
            pc.delete_index("profiles")
            
            # Wait for deletion to complete
            logger.info("Waiting for deletion to complete...")
            time.sleep(20)  # Wait longer to ensure complete deletion
            
            # Verify deletion
            current_indexes = pc.list_indexes().names()
            if "profiles" in current_indexes:
                raise Exception("Failed to delete index")
            logger.info("Index deleted successfully")
        
        # Create new index
        logger.info("Creating new 'profiles' index...")
        pc.create_index(
            name="profiles",
            dimension=384,  # dimension for all-MiniLM-L6-v2
            metric="cosine",
            spec={
                "pod": {
                    "environment": "gcp-starter",
                    "pod_type": "p1.x1"  # Explicitly specify pod type
                }
            }
        )
        
        # Wait for creation
        logger.info("Waiting for index to be ready...")
        time.sleep(20)
        
        # Verify creation
        if "profiles" not in pc.list_indexes().names():
            raise Exception("Failed to create index")
            
        logger.info("Index created successfully!")
        
        # Describe the new index
        index = pc.Index("profiles")
        stats = index.describe_index_stats()
        logger.info(f"Index stats: {stats}")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    reset_profiles_index()
