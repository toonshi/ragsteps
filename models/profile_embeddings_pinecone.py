from typing import Dict, List
from datetime import datetime
import json
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

class ProfileEmbeddingHandler:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize Pinecone
        self.pc = Pinecone()
        self.index = self.pc.Index("profiles")
        
        # Initialize the embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def _create_profile_text(self, profile_data: Dict) -> str:
        """Create a detailed text representation of the profile for embedding"""
        age_months = (datetime.now() - datetime.fromisoformat(profile_data["date_of_birth"])).days // 30
        
        # Basic information
        text = f"""
        Child Profile:
        Name: {profile_data['name']}
        Age: {age_months} months
        Medical Considerations: {', '.join(profile_data['medical_considerations'])}
        Current Focus Areas: {', '.join(profile_data['current_focus_areas'])}
        """

        # Add milestone information
        completed_milestones = []
        incomplete_milestones = []
        for milestone in profile_data["milestones"].values():
            if milestone["completed"]:
                completed_milestones.append(
                    f"{milestone['name']} ({milestone['category']}) - Completed on {milestone['completed_date']}"
                )
            else:
                incomplete_milestones.append(
                    f"{milestone['name']} ({milestone['category']}) - Not completed"
                )

        text += "\nCompleted Milestones:\n" + "\n".join(completed_milestones)
        text += "\n\nUpcoming Milestones:\n" + "\n".join(incomplete_milestones)

        # Add progress history
        text += "\n\nProgress History:\n"
        for entry in profile_data["progress_history"]:
            text += f"- {entry['date']}: {entry['milestone']} - {entry['notes']}\n"

        return text

    def _create_profile_metadata(self, profile_data: Dict) -> Dict:
        """Create metadata for the profile"""
        return {
            "profile_id": profile_data["profile_id"],
            "name": profile_data["name"],
            "date_of_birth": profile_data["date_of_birth"],
            "age_months": (datetime.now() - datetime.fromisoformat(profile_data["date_of_birth"])).days // 30,
            "last_updated": datetime.now().isoformat()
        }

    def upsert_profile(self, profile_data: Dict):
        """Update or insert a profile into the vector database"""
        profile_text = self._create_profile_text(profile_data)
        profile_metadata = self._create_profile_metadata(profile_data)
        
        # Create embedding
        embedding = self.model.encode(profile_text).tolist()
        
        # Add the complete profile data to metadata
        profile_metadata["full_data"] = json.dumps(profile_data)
        
        # Upsert to Pinecone
        self.index.upsert(
            vectors=[{
                "id": profile_data["profile_id"],
                "values": embedding,
                "metadata": profile_metadata
            }]
        )

    def get_profile_context(self, profile_id: str, query: str = None, n_results: int = 1) -> Dict:
        """
        Get the profile context, optionally with query-specific information
        Returns the full profile data and any relevant context
        """
        if query:
            # If query provided, use it to search within the profile
            query_embedding = self.model.encode(query).tolist()
            results = self.index.query(
                vector=query_embedding,
                filter={"profile_id": profile_id},
                top_k=n_results,
                include_metadata=True
            )
        else:
            # Otherwise just fetch the profile directly
            results = self.index.fetch(ids=[profile_id])

        if not results.matches:
            return None

        # Parse the stored JSON document back into a dictionary
        profile_data = json.loads(results.matches[0].metadata["full_data"])
        return profile_data

    def get_similar_profiles(self, query: str, n_results: int = 3) -> List[Dict]:
        """Find similar profiles based on a query"""
        query_embedding = self.model.encode(query).tolist()
        results = self.index.query(
            vector=query_embedding,
            top_k=n_results,
            include_metadata=True
        )
        
        similar_profiles = []
        for match in results.matches:
            profile_data = json.loads(match.metadata["full_data"])
            similar_profiles.append(profile_data)
        
        return similar_profiles

    def delete_profile(self, profile_id: str):
        """Delete a profile from the vector database"""
        self.index.delete(ids=[profile_id])
