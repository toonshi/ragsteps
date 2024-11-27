from typing import Dict, List, Optional
from models.user_model import ChildProfile
from models.profile_embeddings import ProfileEmbeddingHandler
from rag_query import query_knowledge_base

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
        
        # Add recent milestone completions
        for entry in profile.progress_history[-3:]:  # Last 3 milestones
            context += f"- Completed {entry['milestone']} on {entry['date']}\n"
        
        # Add upcoming milestones
        next_milestones = profile.get_next_milestones(3)
        context += "\nUpcoming Milestones:\n"
        for milestone in next_milestones:
            context += f"- {milestone.name} ({milestone.category})\n"
            
        return context

    def query_with_profile(self, profile: ChildProfile, query: str) -> str:
        """
        Query the knowledge base with awareness of the child's profile
        """
        # Get profile-specific context
        profile_context = self.generate_profile_context(profile, query)
        
        # Create an enhanced query that includes profile context
        enhanced_query = f"""
        Child Profile Information:
        {profile_context}
        
        User Question: {query}
        
        Please provide advice that is:
        1. Specific to this child's age and development stage
        2. Considers their medical history and current focus areas
        3. Builds upon their recent progress
        4. Helps work towards their upcoming milestones
        """
        
        # Query the knowledge base with the enhanced context
        response = query_knowledge_base(enhanced_query)
        return response

    def assess_progress(self, profile: ChildProfile) -> Dict:
        """
        Assess the child's developmental progress and provide insights
        """
        # Calculate progress metrics
        total_milestones = len(profile.milestones)
        completed_milestones = len([m for m in profile.milestones.values() if m.completed])
        
        # Get milestone completion rate by category
        category_progress = {}
        for category in set(m.category for m in profile.milestones.values()):
            category_milestones = [m for m in profile.milestones.values() if m.category == category]
            completed = len([m for m in category_milestones if m.completed])
            total = len(category_milestones)
            category_progress[category] = {
                "completed": completed,
                "total": total,
                "percentage": (completed / total * 100) if total > 0 else 0
            }
        
        # Generate progress insights
        progress_query = f"""
        Analyze the following progress for {profile.name} (age: {profile.age_months} months):
        
        Overall Progress: {completed_milestones}/{total_milestones} milestones completed
        
        Progress by Category:
        {self._format_category_progress(category_progress)}
        
        Recent Completions:
        {self._format_recent_completions(profile.progress_history)}
        
        Please provide:
        1. An assessment of current progress
        2. Areas that need more focus
        3. Recommendations for next steps
        """
        
        insights = query_knowledge_base(progress_query)
        
        return {
            "metrics": {
                "total_progress": {
                    "completed": completed_milestones,
                    "total": total_milestones,
                    "percentage": (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0
                },
                "category_progress": category_progress
            },
            "insights": insights
        }
    
    def _format_category_progress(self, category_progress: Dict) -> str:
        """Format category progress for the query"""
        return "\n".join([
            f"- {category}: {data['completed']}/{data['total']} ({data['percentage']:.1f}%)"
            for category, data in category_progress.items()
        ])
    
    def _format_recent_completions(self, progress_history: List[Dict]) -> str:
        """Format recent completions for the query"""
        recent = progress_history[-5:]  # Last 5 completions
        return "\n".join([
            f"- {entry['date']}: {entry['milestone']} - {entry['notes']}"
            for entry in recent
        ])

    def find_similar_cases(self, profile: ChildProfile, n_results: int = 3) -> List[Dict]:
        """
        Find similar profiles to help provide comparative insights
        (Note: This should be used carefully to maintain privacy)
        """
        query = f"""
        Child with:
        - Age: {profile.age_months} months
        - Focus areas: {', '.join(profile.current_focus_areas)}
        - Medical considerations: {', '.join(profile.medical_considerations)}
        """
        return self.profile_handler.get_similar_profiles(query, n_results)
