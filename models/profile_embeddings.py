from typing import Dict, List
import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime
import json

class ProfileEmbeddingHandler:
    def __init__(self, collection_name: str = "child_profiles"):
        self.client = chromadb.Client()
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        # Create or get collection for child profiles
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )

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

        # Store the complete profile data as a document
        document = json.dumps(profile_data)

        self.collection.upsert(
            ids=[profile_data["profile_id"]],
            documents=[document],
            metadatas=[profile_metadata],
            embeddings=self.embedding_function([profile_text])
        )

    def get_profile_context(self, profile_id: str, query: str = None, n_results: int = 1) -> Dict:
        """
        Get the profile context, optionally with query-specific information
        Returns the full profile data and any relevant context
        """
        if query:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"profile_id": profile_id}
            )
        else:
            results = self.collection.get(
                ids=[profile_id],
            )

        if not results["documents"]:
            return None

        # Parse the stored JSON document back into a dictionary
        profile_data = json.loads(results["documents"][0])
        return profile_data

    def get_similar_profiles(self, query: str, n_results: int = 3) -> List[Dict]:
        """Find similar profiles based on a query"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        similar_profiles = []
        for doc in results["documents"]:
            profile_data = json.loads(doc)
            similar_profiles.append(profile_data)
        
        return similar_profiles

    def delete_profile(self, profile_id: str):
        """Delete a profile from the vector database"""
        self.collection.delete(ids=[profile_id])
