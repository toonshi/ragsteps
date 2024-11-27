from models.profile_embeddings_pinecone import ProfileEmbeddingHandler
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
        
        logger.info("1. Storing profile...")
        handler.upsert_profile(sample_profile)
        logger.info("Profile stored successfully")
        
        logger.info("Test completed!")
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        raise

if __name__ == "__main__":
    test_profile_operations()
