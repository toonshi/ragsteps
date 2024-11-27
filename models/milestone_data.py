from typing import List, Dict

# Define milestone categories
MILESTONE_CATEGORIES = [
    "Gross Motor",
    "Fine Motor",
    "Speech and Language",
    "Social and Emotional",
    "Cognitive",
    "Self-Help"
]

# Define developmental milestones with age ranges specific to children with Down syndrome
DEVELOPMENTAL_MILESTONES: List[Dict] = [
    # Gross Motor
    {
        "name": "Head Control",
        "category": "Gross Motor",
        "age_range": "2-4 months",
        "description": "Able to hold head steady while being held upright"
    },
    {
        "name": "Rolling Over",
        "category": "Gross Motor",
        "age_range": "6-8 months",
        "description": "Can roll from back to stomach and stomach to back"
    },
    {
        "name": "Sitting Independently",
        "category": "Gross Motor",
        "age_range": "8-12 months",
        "description": "Can sit without support for several minutes"
    },
    {
        "name": "Crawling",
        "category": "Gross Motor",
        "age_range": "12-18 months",
        "description": "Moving by crawling or scooting"
    },
    {
        "name": "Walking",
        "category": "Gross Motor",
        "age_range": "18-24 months",
        "description": "Taking independent steps and walking"
    },

    # Fine Motor
    {
        "name": "Reaching for Objects",
        "category": "Fine Motor",
        "age_range": "3-5 months",
        "description": "Reaching and grasping for toys or objects"
    },
    {
        "name": "Transferring Objects",
        "category": "Fine Motor",
        "age_range": "6-8 months",
        "description": "Moving objects from one hand to another"
    },
    {
        "name": "Pincer Grasp",
        "category": "Fine Motor",
        "age_range": "10-12 months",
        "description": "Using thumb and index finger to pick up small objects"
    },

    # Speech and Language
    {
        "name": "First Sounds",
        "category": "Speech and Language",
        "age_range": "4-6 months",
        "description": "Making vowel sounds and beginning consonant sounds"
    },
    {
        "name": "Babbling",
        "category": "Speech and Language",
        "age_range": "8-10 months",
        "description": "Producing repeated syllables like 'ba-ba' or 'ma-ma'"
    },
    {
        "name": "First Words",
        "category": "Speech and Language",
        "age_range": "12-18 months",
        "description": "Using simple words meaningfully"
    },

    # Social and Emotional
    {
        "name": "Social Smile",
        "category": "Social and Emotional",
        "age_range": "2-3 months",
        "description": "Smiling in response to others' smiles"
    },
    {
        "name": "Interactive Play",
        "category": "Social and Emotional",
        "age_range": "6-9 months",
        "description": "Engaging in simple games like peek-a-boo"
    },
    {
        "name": "Social Referencing",
        "category": "Social and Emotional",
        "age_range": "9-12 months",
        "description": "Looking to caregivers for emotional cues"
    },

    # Cognitive
    {
        "name": "Object Permanence",
        "category": "Cognitive",
        "age_range": "8-12 months",
        "description": "Understanding objects exist when out of sight"
    },
    {
        "name": "Cause and Effect",
        "category": "Cognitive",
        "age_range": "9-12 months",
        "description": "Understanding actions have consequences"
    },
    {
        "name": "Simple Problem Solving",
        "category": "Cognitive",
        "age_range": "12-18 months",
        "description": "Finding solutions to simple problems like reaching for distant toys"
    },

    # Self-Help
    {
        "name": "Feeding",
        "category": "Self-Help",
        "age_range": "12-18 months",
        "description": "Beginning to feed self with fingers"
    },
    {
        "name": "Drinking",
        "category": "Self-Help",
        "age_range": "12-18 months",
        "description": "Drinking from a cup with help"
    }
]

def get_milestones_by_category(category: str) -> List[Dict]:
    """Get all milestones for a specific category"""
    return [m for m in DEVELOPMENTAL_MILESTONES if m["category"] == category]

def get_milestones_by_age_range(age_range: str) -> List[Dict]:
    """Get all milestones for a specific age range"""
    return [m for m in DEVELOPMENTAL_MILESTONES if m["age_range"] == age_range]

def get_next_milestones(current_age_months: int, limit: int = 3) -> List[Dict]:
    """Get the next appropriate milestones based on the child's age"""
    # Convert age ranges to months for comparison
    def age_range_to_months(age_range: str) -> tuple:
        start, end = age_range.split("-")
        start_num = int(start.strip().split()[0])
        end_num = int(end.strip().split()[0])
        return (start_num, end_num)
    
    appropriate_milestones = []
    for milestone in DEVELOPMENTAL_MILESTONES:
        start_month, end_month = age_range_to_months(milestone["age_range"])
        if start_month <= current_age_months <= end_month + 3:  # Include milestones slightly ahead
            appropriate_milestones.append(milestone)
    
    # Sort by age range and return the next few
    appropriate_milestones.sort(key=lambda x: age_range_to_months(x["age_range"])[0])
    return appropriate_milestones[:limit]
