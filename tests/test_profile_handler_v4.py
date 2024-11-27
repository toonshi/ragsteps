from src.models.profile_embeddings_namespace_v4 import ProfileEmbeddingHandler
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
    }
}
