from models.profile_embeddings_namespace_v4 import ProfileEmbeddingHandler
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a sample profile
sample_profile = {
    "profile_id": "test_child_1",
    "name": "Test Child",
    "date_of_birth": (datetime.now() - timedelta(days=365*2)).isoformat(),  # 2 years old
    "medical_considerations": ["None"],
    "current_focus_areas": ["Language Development", "Motor Skills"],
    "milestones": {
        "milestone1": {
            "name": "First Words",
            "category": "Language",
            "completed": True,
            "completed_date": (datetime.now() - timedelta(days=180)).isoformat()
        }
    },
    "progress_history": [
        {
            "date": (datetime.now() - timedelta(days=180)).isoformat(),
            "milestone": "First Words",
            "notes": "Said 'mama' and 'dada' clearly"
        }
    ]
}

def test_profile_operations():
    try:
        logger.info("Starting profile operations test...")
        
        # Initialize the handler
        logger.info("Creating ProfileEmbeddingHandler...")
        handler = ProfileEmbeddingHandler()
        
        # Test profile storage
        logger.info("\n1. Storing profile...")
        success = handler.upsert_profile(sample_profile)
        if success:
            logger.info("Profile stored and verified successfully")
        else:
            logger.error("Profile storage verification failed")
        
        # Test profile retrieval
        logger.info("\n2. Retrieving profile...")
        retrieved_profile = handler.get_profile_context("test_child_1")
        if retrieved_profile:
            logger.info(f"Retrieved profile name: {retrieved_profile['name']}")
            logger.info(f"Retrieved profile age: {retrieved_profile['date_of_birth']}")
            logger.info(f"Retrieved profile focus areas: {retrieved_profile['current_focus_areas']}")
        else:
            logger.error("Failed to retrieve profile")
        
        # Test similarity search
        logger.info("\n3. Testing similarity search...")
        query = "language development milestones"
        similar_profiles = handler.get_similar_profiles(query, n_results=1)
        logger.info(f"Found {len(similar_profiles)} similar profile(s)")
        if similar_profiles:
            logger.info(f"First similar profile name: {similar_profiles[0]['name']}")
        
        logger.info("\nTest completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        raise

if __name__ == "__main__":
    test_profile_operations()
