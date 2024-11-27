from datetime import datetime
from typing import List, Dict, Optional
import json
import os

class DevelopmentalMilestone:
    def __init__(self, name: str, category: str, age_range: str, description: str, completed: bool = False):
        self.name = name
        self.category = category  # e.g., "Motor", "Speech", "Social", "Cognitive"
        self.age_range = age_range
        self.description = description
        self.completed = completed
        self.completed_date = None
        self.notes = ""

    def complete(self, notes: str = ""):
        self.completed = True
        self.completed_date = datetime.now()
        self.notes = notes

    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category,
            "age_range": self.age_range,
            "description": self.description,
            "completed": self.completed,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "notes": self.notes
        }

class ChildProfile:
    def __init__(
        self,
        name: str,
        date_of_birth: str,
        profile_id: str = None,
        medical_considerations: List[str] = None,
        current_focus_areas: List[str] = None
    ):
        self.profile_id = profile_id or datetime.now().strftime("%Y%m%d%H%M%S")
        self.name = name
        self.date_of_birth = date_of_birth
        self.medical_considerations = medical_considerations or []
        self.current_focus_areas = current_focus_areas or []
        self.milestones: Dict[str, DevelopmentalMilestone] = {}
        self.progress_history: List[Dict] = []

    @property
    def age_months(self) -> int:
        """Calculate age in months"""
        dob = datetime.fromisoformat(self.date_of_birth)
        today = datetime.now()
        return ((today.year - dob.year) * 12 + today.month - dob.month -
                (today.day < dob.day))

    def add_milestone(self, name: str, category: str, completed_date: str = None):
        """Add a completed milestone"""
        if name not in self.milestones:
            milestone = DevelopmentalMilestone(
                name=name,
                category=category,
                age_range=f"{self.age_months} months",
                description=""
            )
            milestone.completed = True
            milestone.completed_date = datetime.fromisoformat(completed_date) if completed_date else datetime.now()
            self.milestones[name] = milestone

    def to_dict(self):
        """Convert profile to dictionary for storage"""
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "date_of_birth": self.date_of_birth,
            "medical_considerations": self.medical_considerations,
            "current_focus_areas": self.current_focus_areas,
            "milestones": {k: v.to_dict() for k, v in self.milestones.items()},
            "progress_history": self.progress_history
        }

class UserManager:
    def __init__(self, data_dir: str = "user_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.profiles: Dict[str, ChildProfile] = self._load_profiles()
    
    def list_profiles(self) -> List[ChildProfile]:
        """Return a list of all profiles"""
        return list(self.profiles.values())

    def _load_profiles(self):
        """Load all profiles from disk"""
        profiles = {}
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.endswith(".json"):
                    with open(os.path.join(self.data_dir, filename), 'r') as f:
                        data = json.load(f)
                        profile = self._dict_to_profile(data)
                        profiles[profile.profile_id] = profile
        return profiles

    def _dict_to_profile(self, data: Dict):
        """Convert dictionary to ChildProfile object"""
        profile = ChildProfile(
            name=data["name"],
            date_of_birth=data["date_of_birth"],
            profile_id=data["profile_id"],
            medical_considerations=data["medical_considerations"],
            current_focus_areas=data["current_focus_areas"]
        )
        profile.progress_history = data.get("progress_history", [])
        
        # Load milestones
        for milestone_data in data.get("milestones", {}).values():
            profile.add_milestone(
                name=milestone_data["name"],
                category=milestone_data["category"],
                completed_date=milestone_data.get("completed_date")
            )
        return profile

    def save_profile(self, profile: ChildProfile):
        """Save a profile to disk"""
        filename = f"{profile.profile_id}.json"
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)
        self.profiles[profile.profile_id] = profile

    def get_profile(self, profile_id: str) -> Optional[ChildProfile]:
        """Get a profile by ID"""
        return self.profiles.get(profile_id)

    def add_profile(self, profile: ChildProfile):
        """Add a new profile"""
        self.save_profile(profile)

    def update_profile(self, profile: ChildProfile):
        """Update an existing profile"""
        if profile.profile_id in self.profiles:
            self.save_profile(profile)
