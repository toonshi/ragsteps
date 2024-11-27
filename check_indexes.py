from pinecone import Pinecone
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_indexes():
    # Load environment variables
    load_dotenv()
    
    # Initialize Pinecone
    pc = Pinecone()
    
    # Get list of indexes
    indexes = pc.list_indexes().names()
    logger.info(f"Current indexes: {indexes}")
    
    # Check each index's details
    for index_name in indexes:
        try:
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            logger.info(f"\nIndex '{index_name}' stats:")
            logger.info(f"Dimension: {stats.get('dimension')}")
            logger.info(f"Total vectors: {stats.get('total_vector_count')}")
            logger.info(f"Index fullness: {stats.get('index_fullness')}")
        except Exception as e:
            logger.error(f"Error getting stats for {index_name}: {str(e)}")

if __name__ == "__main__":
    check_indexes()
