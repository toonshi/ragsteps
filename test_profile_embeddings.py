from models.profile_embeddings_pinecone import ProfileEmbeddingHandler
from datetime import datetime, timedelta

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
        },
        "milestone2": {
            "name": "Walking",
            "category": "Motor",
            "completed": True,
            "completed_date": (datetime.now() - timedelta(days=90)).isoformat()
        }
    },
    "progress_history": [
        {
            "date": (datetime.now() - timedelta(days=180)).isoformat(),
            "milestone": "First Words",
            "notes": "Said 'mama' and 'dada' clearly"
        },
        {
            "date": (datetime.now() - timedelta(days=90)).isoformat(),
            "milestone": "Walking",
            "notes": "Taking first independent steps"
        }
    ]
}

def test_profile_operations():
    # Initialize the handler
    handler = ProfileEmbeddingHandler()
    
    print("1. Storing profile...")
    handler.upsert_profile(sample_profile)
    
    print("\n2. Retrieving profile...")
    retrieved_profile = handler.get_profile_context("test_child_1")
    print(f"Retrieved profile name: {retrieved_profile['name']}")
    print(f"Retrieved profile age: {retrieved_profile['date_of_birth']}")
    
    print("\n3. Testing similarity search...")
    query = "language development milestones"
    similar_profiles = handler.get_similar_profiles(query, n_results=1)
    print(f"Found {len(similar_profiles)} similar profile(s)")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_profile_operations()
