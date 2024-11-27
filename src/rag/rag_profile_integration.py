from typing import Dict, List, Optional
from src.models.user_model import ChildProfile
from src.models.profile_embeddings_namespace_v4 import ProfileEmbeddingHandler
from src.rag.rag_query_pinecone import query_knowledge_base

class ProfileAwareRAG:
    def __init__(self):
        self.profile_handler = ProfileEmbeddingHandler()
        
    def generate_profile_context(self, profile: ChildProfile, query: str) -> str:
        """Generate context about the child's profile relevant to the query"""
        profile_data = self.profile_handler.get_profile_context(profile.profile_id, query)
        
        # Create a context string that focuses on relevant aspects of the child's development
        context = f"""
        Context about {profile.name}:
        - Age: {profile.age_months} months
        - Medical considerations: {', '.join(profile.medical_considerations)}
        - Current focus areas: {', '.join(profile.current_focus_areas)}
        
        Recent Progress:
        """
