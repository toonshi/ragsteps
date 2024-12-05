from datetime import datetime
from src.models.milestone_data import DEVELOPMENTAL_MILESTONES

class ChildProfile:
    def __init__(self, profile_id, name, date_of_birth, medical_considerations, current_focus_areas):
        self.profile_id = profile_id
        self.name = name
        self.date_of_birth = date_of_birth
        self.medical_considerations = medical_considerations
        self.current_focus_areas = current_focus_areas
        self.milestones = []  # Store completed milestones
    
    def add_milestone(self, name: str, category: str, completed_date: str):
        """Add a milestone to the completed list."""
        self.milestones.append({
            "name": name,
            "category": category,
            "completed_date": completed_date
        })
