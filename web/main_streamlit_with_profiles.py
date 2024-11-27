import streamlit as st
from src.rag.rag_query_streamlit import query_knowledge_base
from src.utils.pdf_loader import load_pdfs_to_pinecone
import os
from dotenv import load_dotenv
from datetime import datetime
from src.models.user_model import UserManager, ChildProfile, DevelopmentalMilestone
from src.models.milestone_data import (
    MILESTONE_CATEGORIES,
    DEVELOPMENTAL_MILESTONES,
    get_next_milestones
)

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Bright Steps: Help us grow",
    page_icon=None,
    layout="wide"
)

# Initialize session state for user management
if 'user_manager' not in st.session_state:
    st.session_state.user_manager = UserManager()

if 'current_profile' not in st.session_state:
    st.session_state.current_profile = None

# Sidebar for profile management
with st.sidebar:
    st.title("Profile Management")
    
    # Profile selection
    profiles = st.session_state.user_manager.list_profiles()
    profile_names = [profile.name for profile in profiles]
    
    if profile_names:
        selected_name = st.selectbox("Select Profile", profile_names)
        selected_profile = next(p for p in profiles if p.name == selected_name)
        
        if st.button("Load Profile"):
            st.session_state.current_profile = selected_profile
            st.success(f"Loaded profile for {selected_profile.name}")
    
    # Create new profile section
    st.markdown("---")
    st.subheader("Create New Profile")
    
    new_name = st.text_input("Child's Name")
    new_dob = st.date_input("Date of Birth")
    new_medical = st.text_input("Medical Considerations (comma-separated)")
    new_focus = st.text_input("Current Focus Areas (comma-separated)")
    
    if st.button("Create Profile"):
        if new_name and new_dob:
            medical_list = [item.strip() for item in new_medical.split(",")] if new_medical else []
            focus_list = [item.strip() for item in new_focus.split(",")] if new_focus else []
            
            new_profile = ChildProfile(
                profile_id=f"child_{len(profiles) + 1}",
                name=new_name,
                date_of_birth=new_dob.isoformat(),
                medical_considerations=medical_list,
                current_focus_areas=focus_list
            )
            
            st.session_state.user_manager.add_profile(new_profile)
            st.success(f"Created profile for {new_name}")
            st.rerun()

# Main content area
if st.session_state.current_profile:
    profile = st.session_state.current_profile
    
    # Create three columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header(f"{profile.name}'s Development")
        
        # Display basic info
        st.subheader("Basic Information")
        st.write(f"Age: {profile.age_months} months")
        st.write(f"Medical Considerations: {', '.join(profile.medical_considerations)}")
        st.write(f"Current Focus Areas: {', '.join(profile.current_focus_areas)}")
        
        # Milestone tracking
        st.subheader("Milestone Tracking")
        
        # Get next milestones for the child's age
        next_milestones = get_next_milestones(profile.age_months)
        
        if next_milestones:
            st.write("Upcoming Milestones:")
            for category, milestones in next_milestones.items():
                st.write(f"\n**{category}**")
                for milestone in milestones:
                    completed = st.checkbox(
                        milestone,
                        key=f"{profile.profile_id}_{milestone}"
                    )
                    if completed:
                        profile.add_milestone(
                            name=milestone,
                            category=category,
                            completed_date=datetime.now().isoformat()
                        )
        else:
            st.write("No upcoming milestones found for this age group.")
    
    with col2:
        st.header("Ask about Development")
        user_question = st.text_input("Ask a question about child development:")
        
        if user_question:
            with st.spinner("Finding relevant information..."):
                response = query_knowledge_base(user_question)
                st.write(response)
else:
    st.title("Welcome to Bright Steps!")
    st.write("Please select or create a profile to get started.")
