from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from datetime import datetime, timedelta
import json
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_insert():
    try:
        # Load environment variables
        load_dotenv()
        
        # Create a minimal test profile
        test_profile = {
            "profile_id": "test1",
            "name": "Test Child",
            "date_of_birth": datetime.now().isoformat()
        }
        
        # Create text for embedding
        profile_text = f"""
        Profile ID: {test_profile['profile_id']}
        Name: {test_profile['name']}
        DOB: {test_profile['date_of_birth']}
        """
        
        logger.info("Initializing SentenceTransformer...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        logger.info("Creating embedding...")
        embedding = model.encode(profile_text).tolist()
        
        logger.info("Connecting to Pinecone...")
        pc = Pinecone()
        index = pc.Index("profiles")
        
        # Create minimal metadata
        metadata = {
            "name": test_profile['name'],
            "profile_data": json.dumps(test_profile)
        }
        
        logger.info("Attempting to upsert vector...")
        response = index.upsert(
            vectors=[{
                "id": test_profile["profile_id"],
                "values": embedding,
                "metadata": metadata
            }]
        )
        
        logger.info(f"Upsert response: {response}")
        
        # Verify the insert
        logger.info("Verifying insert...")
        stats = index.describe_index_stats()
        logger.info(f"Index stats after insert: {stats}")
        
        # Try to fetch the vector
        logger.info("Fetching inserted vector...")
        fetch_response = index.fetch(ids=[test_profile["profile_id"]])
        logger.info(f"Fetch response: {fetch_response}")
        
        logger.info("Test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        raise

if __name__ == "__main__":
    test_direct_insert()
