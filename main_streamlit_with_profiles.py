import streamlit as st
from datetime import datetime
from src.models.user_model import UserManager, ChildProfile
from src.models.milestone_data import DEVELOPMENTAL_MILESTONES, get_next_milestones
from src.rag.rag_query_streamlit import query_knowledge_base
from src.utils.pdf_loader import load_pdfs_to_pinecone
import os
from dotenv import load_dotenv

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
    
    # If there are no profiles, set the selectbox to display a default message
    if profile_names:
        selected_name = st.selectbox("Select Profile", profile_names)
    else:
        selected_name = st.selectbox("Select Profile", ["No profiles available"])
    
    selected_profile = next((p for p in profiles if p.name == selected_name), None)

    if selected_name != "No profiles available" and st.button("Load Profile"):
        if selected_profile:
            st.session_state.current_profile = selected_profile
            st.success(f"Loaded profile for {selected_profile.name}")
            st.rerun()  # Reload the page to reset fields

    # Create new profile section
    st.markdown("---")
    st.subheader("Create New Profile")
    
    new_name = st.text_input("Child's Name", value="")
    new_dob = st.date_input("Date of Birth", value=None)
    new_medical = st.text_input("Medical Considerations (comma-separated)", value="")
    new_focus = st.text_input("Current Focus Areas (comma-separated)", value="")
    
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
            
            # Reset fields after creating profile
            new_name = ""  # Clear the input field
            new_dob = None
            new_medical = ""  # Clear the input fields
            new_focus = ""  # Clear the input fields
            # After creating a profile or loading a profile, reset the fields and trigger a rerun
            st.rerun()  # Reload the page to clear session data and reset the fields

# Main content area
if st.session_state.current_profile:
    profile = st.session_state.current_profile
    
    # Create two columns for Development Info and Milestone Tracker
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header(f"{profile.name}'s Development Overview")
        
        # Display basic profile info
        st.subheader("Basic Information")
        st.write(f"**Age:** {profile.age_months} months")
        st.write(f"**Medical Considerations:** {', '.join(profile.medical_considerations)}")
        st.write(f"**Current Focus Areas:** {', '.join(profile.current_focus_areas)}")

        # Ask a development-related question
        st.subheader("Ask about Development")
        user_question = st.text_input("Ask a question about child development:")
        
        if user_question:
            with st.spinner("Finding relevant information..."):
                response = query_knowledge_base(user_question)
                st.write(response)
    
    with col2:
        st.header("Developmental Milestone Tracker")
        
        # Fetch milestones dynamically
        next_milestones = get_next_milestones(profile.age_months)
        
        # Display milestones in categories
        if next_milestones:
            st.write("**Upcoming Milestones**")
            for milestone in next_milestones:
                # Display milestone details
                st.markdown(f"""
                **Milestone:** {milestone['name']}
                - **Category:** {milestone['category']}
                - **Age Range:** {milestone['age_range']}
                - **Description:** {milestone['description']}
                """)

                # Interactive checkbox for completion
                completed = st.checkbox(
                    f"Mark '{milestone['name']}' as Completed",
                    key=f"{profile.profile_id}_{milestone['name']}"
                )
                if completed:
                    profile.add_milestone(
                        name=milestone["name"],
                        category=milestone["category"],
                        completed_date=datetime.now().isoformat()
                    )
                    st.success(f"Marked '{milestone['name']}' as completed!")
        else:
            st.write("No upcoming milestones found for this age group.")
    
    # Show completed milestones
    if profile.milestones:
        st.subheader("Completed Milestones")
        with st.expander("View Completed Milestones"):
            for milestone in profile.milestones:
                # Check if milestone is a dictionary
                if isinstance(milestone, dict):
                    milestone_name = milestone.get('name', 'Unknown Name')
                    milestone_completed_date = milestone.get('completed_date', 'Not Completed')
                else:  # Assuming milestone is an object
                    milestone_name = getattr(milestone, 'name', 'Unknown Name')
                    milestone_completed_date = getattr(milestone, 'completed_date', 'Not Completed')

                st.markdown(f"- **{milestone_name}** (Completed on {milestone_completed_date})")
    else:
        st.write("No milestones completed yet.")
else:
    st.title("Welcome to Bright Steps!")
    st.info("Please select or create a profile to begin tracking milestones.")

# Add a WhatsApp button in the sidebar
with st.sidebar:
    st.markdown("---")
    st.subheader("Contact Us on WhatsApp")

    whatsapp_url = "https://wa.me/15551234567?text=Hello! I need assistance with Bright Steps."  # Replace with your number
    st.markdown(
        f"""
        <a href="{whatsapp_url}" target="_blank" style="
            background-color: #25D366;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            font-size: 16px;
            font-weight: bold;
        ">
            Chat with Us on WhatsApp
        </a>
        """,
        unsafe_allow_html=True
    )
  # Add the Education button
    st.subheader("Learn More About Child Development")

    education_url = "https://toonshi.github.io/brightsteps_edu/#science"  # Replace with your education link
    st.markdown(
        f"""
        <a href="{education_url}" target="_blank" style="
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            font-size: 16px;
            font-weight: bold;
        ">
             Brightsteps Education
        </a>
        """,
        unsafe_allow_html=True
    )