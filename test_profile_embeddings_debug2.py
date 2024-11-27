from models.profile_embeddings_pinecone import ProfileEmbeddingHandler
from datetime import datetime, timedelta
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an even simpler profile for testing
sample_profile = {
    "profile_id": "test_child_1",
    "name": "Test Child",
    "date_of_birth": (datetime.now() - timedelta(days=365*2)).isoformat(),
    "medical_considerations": ["None"],
    "current_focus_areas": ["Language"],
    "milestones": {},
    "progress_history": []
}

def test_profile_operations():
    try:
        logger.info("Starting profile operations test...")
        
        # Initialize the handler
        logger.info("Creating ProfileEmbeddingHandler...")
        handler = ProfileEmbeddingHandler()
        
        # Create the profile text and embedding
        logger.info("Creating profile text...")
        profile_text = handler._create_profile_text(sample_profile)
        logger.info(f"Profile text length: {len(profile_text)}")
        
        logger.info("Creating embedding...")
        embedding = handler.model.encode(profile_text).tolist()
        logger.info(f"Embedding dimension: {len(embedding)}")
        
        # Create metadata
        logger.info("Creating metadata...")
        metadata = handler._create_profile_metadata(sample_profile)
        metadata["full_data"] = json.dumps(sample_profile)
        logger.info(f"Metadata size: {len(str(metadata))} bytes")
        
        # Attempt upsert with explicit checks
        logger.info("Upserting to Pinecone...")
        vector_data = {
            "id": sample_profile["profile_id"],
            "values": embedding,
            "metadata": metadata
        }
        
        logger.info("Verifying vector data...")
        logger.info(f"Vector ID: {vector_data['id']}")
        logger.info(f"Vector dimension: {len(vector_data['values'])}")
        logger.info(f"Metadata keys: {list(vector_data['metadata'].keys())}")
        
        handler.index.upsert(vectors=[vector_data])
        logger.info("Upsert completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        raise

if __name__ == "__main__":
    test_profile_operations()
