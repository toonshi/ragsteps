from typing import Dict, List
from datetime import datetime
import json
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfileEmbeddingHandler:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        logger.info("Initializing ProfileEmbeddingHandler...")
        
        # Initialize Pinecone
        logger.info("Connecting to Pinecone...")
        self.pc = Pinecone()
        self.index = self.pc.Index("studyrag")
        self.namespace = "profiles"
        
        # Initialize the embedding model
        logger.info("Loading SentenceTransformer model...")
        self.model = SentenceTransformer('bert-base-nli-mean-tokens')
        logger.info("Initialization complete")

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
            "type": "profile",
            "profile_id": profile_data["profile_id"],
            "name": profile_data["name"],
            "date_of_birth": profile_data["date_of_birth"],
            "age_months": (datetime.now() - datetime.fromisoformat(profile_data["date_of_birth"])).days // 30,
            "last_updated": datetime.now().isoformat(),
            "full_data": json.dumps(profile_data)  # Store full data directly in metadata
        }

    def upsert_profile(self, profile_data: Dict):
        """Update or insert a profile into the vector database"""
        try:
            logger.info(f"Creating embedding for profile {profile_data['profile_id']}...")
            profile_text = self._create_profile_text(profile_data)
            profile_metadata = self._create_profile_metadata(profile_data)
            
            # Create embedding
            logger.info("Generating embedding...")
            embedding = self.model.encode(profile_text).tolist()
            
            vector_id = f"profile_{profile_data['profile_id']}"
            logger.info(f"Upserting vector with ID: {vector_id}")
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[{
                    "id": vector_id,
                    "values": embedding,
                    "metadata": profile_metadata
                }],
                namespace=self.namespace
            )
            logger.info("Upsert completed successfully")
            
            # Verify the upsert with a query
            logger.info("Verifying upsert with query...")
            query_result = self.index.query(
                vector=embedding,
                filter={"type": "profile", "profile_id": profile_data["profile_id"]},
                namespace=self.namespace,
                top_k=1,
                include_metadata=True
            )
            
            if query_result and query_result.matches:
                logger.info("Verification successful - profile found in index")
                return True
            else:
                logger.warning("Verification failed - profile not found after upsert")
                return False
                
        except Exception as e:
            logger.error(f"Error during upsert: {str(e)}")
            raise

    def get_profile_context(self, profile_id: str, query: str = None, n_results: int = 1) -> Dict:
        """Get the profile context, optionally with query-specific information"""
        try:
            if query:
                # Search by query
                logger.info(f"Searching for profile {profile_id} with query: {query}")
                query_embedding = self.model.encode(query).tolist()
                results = self.index.query(
                    vector=query_embedding,
                    filter={"type": "profile", "profile_id": profile_id},
                    namespace=self.namespace,
                    top_k=n_results,
                    include_metadata=True
                )
            else:
                # Get profile text and create embedding
                logger.info(f"Searching for profile {profile_id}")
                # Use a simple query to find the profile
                dummy_query = f"Profile for {profile_id}"
                query_embedding = self.model.encode(dummy_query).tolist()
                results = self.index.query(
                    vector=query_embedding,
                    filter={"type": "profile", "profile_id": profile_id},
                    namespace=self.namespace,
                    top_k=1,
                    include_metadata=True
                )

            if results and results.matches:
                logger.info(f"Found profile {profile_id}")
                return json.loads(results.matches[0].metadata["full_data"])
            else:
                logger.warning(f"No results found for profile ID: {profile_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving profile: {str(e)}")
            return None

    def get_similar_profiles(self, query: str, n_results: int = 3) -> List[Dict]:
        """Find similar profiles based on a query"""
        try:
            logger.info(f"Searching for profiles similar to query: {query}")
            query_embedding = self.model.encode(query).tolist()
            results = self.index.query(
                vector=query_embedding,
                filter={"type": "profile"},
                namespace=self.namespace,
                top_k=n_results,
                include_metadata=True
            )
            
            similar_profiles = []
            if results and results.matches:
                for match in results.matches:
                    profile_data = json.loads(match.metadata["full_data"])
                    similar_profiles.append(profile_data)
                logger.info(f"Found {len(similar_profiles)} similar profiles")
            else:
                logger.info("No similar profiles found")
            
            return similar_profiles
            
        except Exception as e:
            logger.error(f"Error during similarity search: {str(e)}")
            return []

    def delete_profile(self, profile_id: str):
        """Delete a profile from the vector database"""
        vector_id = f"profile_{profile_id}"
        try:
            self.index.delete(
                ids=[vector_id],
                namespace=self.namespace
            )
            logger.info(f"Successfully deleted profile: {profile_id}")
        except Exception as e:
            logger.error(f"Error deleting profile: {str(e)}")
            raise
