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
        date_of_birth: datetime,
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
        today = datetime.now()
        return (today.year - self.date_of_birth.year) * 12 + (today.month - self.date_of_birth.month)

    def add_milestone(self, milestone: DevelopmentalMilestone):
        self.milestones[milestone.name] = milestone

    def complete_milestone(self, milestone_name: str, notes: str = ""):
        if milestone_name in self.milestones:
            self.milestones[milestone_name].complete(notes)
            self.progress_history.append({
                "milestone": milestone_name,
                "date": datetime.now().isoformat(),
                "notes": notes
            })

    def get_incomplete_milestones(self) -> List[DevelopmentalMilestone]:
        return [m for m in self.milestones.values() if not m.completed]

    def get_next_milestones(self, limit: int = 3) -> List[DevelopmentalMilestone]:
        """Get the next few age-appropriate incomplete milestones"""
        incomplete = self.get_incomplete_milestones()
        # Sort by age range and return the next few
        return sorted(incomplete, key=lambda x: x.age_range)[:limit]

    def to_dict(self):
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "date_of_birth": self.date_of_birth.isoformat(),
            "medical_considerations": self.medical_considerations,
            "current_focus_areas": self.current_focus_areas,
            "milestones": {name: milestone.to_dict() for name, milestone in self.milestones.items()},
            "progress_history": self.progress_history
        }

class UserManager:
    def __init__(self, data_dir: str = "user_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.profiles: Dict[str, ChildProfile] = self._load_profiles()

    def _load_profiles(self) -> Dict[str, ChildProfile]:
        profiles = {}
        if not os.path.exists(self.data_dir):
            return profiles

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.data_dir, filename), 'r') as f:
                    data = json.load(f)
                    profile = self._dict_to_profile(data)
                    profiles[profile.profile_id] = profile
        return profiles

    def _dict_to_profile(self, data: Dict) -> ChildProfile:
        profile = ChildProfile(
            name=data["name"],
            date_of_birth=datetime.fromisoformat(data["date_of_birth"]),
            profile_id=data["profile_id"],
            medical_considerations=data["medical_considerations"],
            current_focus_areas=data["current_focus_areas"]
        )
        
        # Load milestones
        for m_data in data["milestones"].values():
            milestone = DevelopmentalMilestone(
                name=m_data["name"],
                category=m_data["category"],
                age_range=m_data["age_range"],
                description=m_data["description"]
            )
            if m_data["completed"]:
                milestone.complete(m_data["notes"])
            profile.add_milestone(milestone)

        profile.progress_history = data["progress_history"]
        return profile

    def save_profile(self, profile: ChildProfile):
        filename = f"{profile.profile_id}.json"
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)

    def get_profile(self, profile_id: str) -> Optional[ChildProfile]:
        return self.profiles.get(profile_id)

    def create_profile(self, name: str, date_of_birth: datetime, 
                      medical_considerations: List[str] = None,
                      current_focus_areas: List[str] = None) -> ChildProfile:
        profile = ChildProfile(name, date_of_birth, 
                             medical_considerations=medical_considerations,
                             current_focus_areas=current_focus_areas)
        self.profiles[profile.profile_id] = profile
        self.save_profile(profile)
        return profile

    def update_profile(self, profile: ChildProfile):
        self.profiles[profile.profile_id] = profile
        self.save_profile(profile)
