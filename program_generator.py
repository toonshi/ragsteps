from typing import Dict, List, Optional
import openai
from datetime import datetime, timedelta
from models.user_model import ChildProfile
from rag_query import query_knowledge_base

class DevelopmentProgram:
    def __init__(self, profile: ChildProfile):
        self.profile = profile
        self.activities: List[Dict] = []
        self.progress_notes: List[Dict] = []
        self.last_assessment: Optional[Dict] = None
        
    def to_dict(self) -> Dict:
        return {
            "profile_id": self.profile.profile_id,
            "activities": self.activities,
            "progress_notes": self.progress_notes,
            "last_assessment": self.last_assessment
        }

class ProgramGenerator:
    def __init__(self):
        self.programs: Dict[str, DevelopmentProgram] = {}

    def generate_weekly_program(self, profile: ChildProfile) -> Dict:
        """Generate a personalized weekly program based on the child's profile"""
        # Create context from profile and milestone data
        context = f"""
        Child Information:
        - Name: {profile.name}
        - Age: {profile.age_months} months
        - Medical considerations: {', '.join(profile.medical_considerations)}
        - Current focus areas: {', '.join(profile.current_focus_areas)}
        
        Recent Progress:
        {self._format_recent_progress(profile)}
        
        Current Milestones Working On:
        {self._format_current_milestones(profile)}
        
        Based on this information, create a detailed weekly program that:
        1. Includes daily activities targeting current milestones
        2. Considers the child's medical needs and limitations
        3. Provides clear instructions for parents
        4. Includes progress tracking metrics
        5. Suggests fun and engaging activities
        6. Incorporates rest periods and flexibility
        """
        
        # Query the knowledge base for program generation
        program_response = query_knowledge_base(context)
        
        # Structure the program response
        weekly_program = self._structure_program(program_response)
        
        # Store the program
        if profile.profile_id not in self.programs:
            self.programs[profile.profile_id] = DevelopmentProgram(profile)
        
        self.programs[profile.profile_id].activities = weekly_program
        
        return weekly_program

    def assess_activity_completion(self, profile: ChildProfile, activity_log: str) -> Dict:
        """Assess the completion and effectiveness of activities"""
        context = f"""
        Activity Log:
        {activity_log}
        
        Child's Current Development Stage:
        - Age: {profile.age_months} months
        - Working on milestones: {self._format_current_milestones(profile)}
        
        Please assess:
        1. Level of engagement and completion
        2. Progress towards milestone goals
        3. Areas needing adjustment
        4. Recommendations for next activities
        """
        
        assessment = query_knowledge_base(context)
        
        # Store the assessment
        if profile.profile_id in self.programs:
            self.programs[profile.profile_id].progress_notes.append({
                "date": datetime.now().isoformat(),
                "log": activity_log,
                "assessment": assessment
            })
        
        return {
            "assessment": assessment,
            "timestamp": datetime.now().isoformat()
        }

    def generate_visual_guide(self, activity: Dict) -> str:
        """Generate a visual guide or instructions for an activity"""
        context = f"""
        Activity: {activity['name']}
        Description: {activity['description']}
        
        Please provide:
        1. Step-by-step instructions with visual cues
        2. Safety considerations
        3. Required materials
        4. Tips for parent engagement
        5. Signs of progress to look for
        """
        
        return query_knowledge_base(context)

    def adjust_program_difficulty(self, profile: ChildProfile, feedback: str) -> Dict:
        """Adjust program difficulty based on feedback"""
        context = f"""
        Current Program Feedback:
        {feedback}
        
        Child's Progress:
        {self._format_recent_progress(profile)}
        
        Please suggest:
        1. Difficulty adjustments needed
        2. Alternative activities if needed
        3. Additional support requirements
        """
        
        adjustments = query_knowledge_base(context)
        return {
            "adjustments": adjustments,
            "timestamp": datetime.now().isoformat()
        }

    def _format_recent_progress(self, profile: ChildProfile) -> str:
        """Format recent progress for context"""
        progress = []
        for entry in profile.progress_history[-5:]:
            progress.append(f"- {entry['date']}: {entry['milestone']}")
        return "\n".join(progress)

    def _format_current_milestones(self, profile: ChildProfile) -> str:
        """Format current milestones being worked on"""
        current = []
        for milestone in profile.get_next_milestones(3):
            current.append(f"- {milestone.name} ({milestone.category})")
        return "\n".join(current)

    def _structure_program(self, raw_program: str) -> List[Dict]:
        """Structure the raw program response into organized activities"""
        # This is a placeholder - you would implement proper parsing here
        # For now, we'll create a simple structure
        activities = []
        
        # Split the raw program into daily activities
        days = raw_program.split("\n\n")
        for day in days:
            if day.strip():
                activities.append({
                    "day": "Day X",  # You would parse this from the content
                    "activities": [{
                        "name": "Activity",  # Parse from content
                        "description": day.strip(),
                        "duration": "30 minutes",  # Parse from content
                        "materials": [],  # Parse from content
                        "progress_indicators": []  # Parse from content
                    }]
                })
        
        return activities
