from pinecone import Pinecone
import os
from dotenv import load_dotenv
import time
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import threading

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_index_with_timeout(pc, max_wait=60):
    """Create index with timeout"""
    try:
        logger.info("Creating new 'profiles' index...")
        pc.create_index(
            name="profiles",
            dimension=384,
            metric="cosine",
            spec={
                "pod": {
                    "environment": "gcp-starter"
                }
            }
        )
        return True
    except Exception as e:
        logger.error(f"Error creating index: {str(e)}")
        return False

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
            
            # Wait for deletion with timeout
            start_time = time.time()
            max_wait = 30  # Maximum seconds to wait
            
            while "profiles" in pc.list_indexes().names():
                if time.time() - start_time > max_wait:
                    raise TimeoutError("Index deletion timed out")
                logger.info("Waiting for deletion to complete...")
                time.sleep(5)
            
            logger.info("Index deleted successfully")
        
        # Create new index with timeout
        with ThreadPoolExecutor() as executor:
            future = executor.submit(create_index_with_timeout, pc)
            try:
                result = future.result(timeout=60)  # Wait max 60 seconds
                if not result:
                    raise Exception("Failed to create index")
            except TimeoutError:
                raise TimeoutError("Index creation timed out after 60 seconds")
        
        logger.info("Index created successfully!")
        
        # Quick verification
        if "profiles" not in pc.list_indexes().names():
            raise Exception("Index creation verified failed")
            
        logger.info("All operations completed successfully!")
        
    except TimeoutError as e:
        logger.error(f"Timeout error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    reset_profiles_index()
