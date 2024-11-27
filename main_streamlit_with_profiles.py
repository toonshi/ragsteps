import streamlit as st
from rag_query_streamlit import query_knowledge_base
from pdf_loader import load_pdfs_to_chroma
import os
from dotenv import load_dotenv
from datetime import datetime
from models.user_model import UserManager, ChildProfile, DevelopmentalMilestone
from models.milestone_data import (
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

# Initialize UserManager
if 'user_manager' not in st.session_state:
    st.session_state.user_manager = UserManager()

# Initialize session states
if 'current_profile' not in st.session_state:
    st.session_state.current_profile = None

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Title
st.title("Bright Steps: Help us grow")

# Sidebar for profile management and document upload
with st.sidebar:
    st.sidebar.title("Profile Management")
    
    # Profile selection or creation
    profile_action = st.sidebar.radio(
        "Choose an action:",
        ["Select Existing Profile", "Create New Profile"]
    )
    
    if profile_action == "Select Existing Profile":
        if st.session_state.user_manager.profiles:
            profile_names = {profile.name: profile_id 
                           for profile_id, profile in st.session_state.user_manager.profiles.items()}
            selected_name = st.sidebar.selectbox(
                "Select a profile:",
                options=list(profile_names.keys())
            )
            if selected_name:
                profile_id = profile_names[selected_name]
                st.session_state.current_profile = st.session_state.user_manager.get_profile(profile_id)
        else:
            st.sidebar.info("No profiles exist yet. Create a new profile to get started!")
    
    else:  # Create New Profile
        with st.sidebar.form("new_profile"):
            st.write("Create New Profile")
            new_name = st.text_input("Child's Name")
            new_dob = st.date_input("Date of Birth")
            new_considerations = st.text_area(
                "Medical Considerations (one per line)",
                help="Enter any medical considerations, one per line"
            )
            new_focus_areas = st.text_area(
                "Current Focus Areas (one per line)",
                help="Enter current areas of focus, one per line"
            )
            
            submit_profile = st.form_submit_button("Create Profile")
            
            if submit_profile and new_name and new_dob:
                considerations_list = [c.strip() for c in new_considerations.split("\n") if c.strip()]
                focus_areas_list = [f.strip() for f in new_focus_areas.split("\n") if f.strip()]
                
                new_profile = st.session_state.user_manager.create_profile(
                    name=new_name,
                    date_of_birth=datetime.combine(new_dob, datetime.min.time()),
                    medical_considerations=considerations_list,
                    current_focus_areas=focus_areas_list
                )
                st.session_state.current_profile = new_profile
                st.sidebar.success(f"Profile created for {new_name}!")

    # Document Management section
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Document Management")
    uploaded_file = st.sidebar.file_uploader("Upload PDF Document", type=['pdf'])
    if uploaded_file:
        with st.spinner("Processing document..."):
            # Save the uploaded file temporarily
            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.getvalue())
            # Load the PDF into the knowledge base
            load_pdfs_to_chroma(["temp.pdf"])
            os.remove("temp.pdf")
            st.sidebar.success("Document processed successfully!")

# Main content area
if st.session_state.current_profile:
    profile = st.session_state.current_profile
    
    # Create three columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"### {profile.name}'s Profile")
        st.write(f"Age: {profile.age_months} months")
        
        # Display current focus areas
        st.markdown("#### Current Focus Areas")
        for area in profile.current_focus_areas:
            st.write(f"- {area}")
            
        # Display medical considerations
        if profile.medical_considerations:
            st.markdown("#### Medical Considerations")
            for consideration in profile.medical_considerations:
                st.write(f"- {consideration}")
        
        # Display next milestones
        st.markdown("#### Next Milestones")
        next_milestones = get_next_milestones(profile.age_months)
        for milestone in next_milestones:
            with st.expander(f"{milestone['name']} ({milestone['category']})"):
                st.write(f"Age Range: {milestone['age_range']}")
                st.write(f"Description: {milestone['description']}")
                # Check if milestone exists and is completed
                milestone_obj = profile.milestones.get(milestone['name'])
                is_completed = milestone_obj.completed if milestone_obj else False
                
                if not is_completed:
                    if st.button(f"Mark Complete", key=f"complete_{milestone['name']}"):
                        if milestone['name'] not in profile.milestones:
                            new_milestone = DevelopmentalMilestone(
                                name=milestone['name'],
                                category=milestone['category'],
                                age_range=milestone['age_range'],
                                description=milestone['description']
                            )
                            profile.add_milestone(new_milestone)
                        profile.complete_milestone(milestone['name'])
                        st.session_state.user_manager.save_profile(profile)
                        st.success(f"Marked {milestone['name']} as complete!")
                else:
                    st.success("✓ Completed")
    
    with col2:
        st.markdown("### Chat Assistant")
        st.write("Ask questions about developmental milestones and get personalized advice.")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask a question about developmental milestones..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Create a context-aware prompt
            context = f"""
            Child's Name: {profile.name}
            Age: {profile.age_months} months
            Focus Areas: {', '.join(profile.current_focus_areas)}
            Medical Considerations: {', '.join(profile.medical_considerations)}
            
            User Question: {prompt}
            
            Please provide advice specific to this child's age and situation, considering they have Down syndrome.
            """
            
            # Get response from RAG system
            with st.spinner("Thinking..."):
                response = query_knowledge_base(context)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Display the response
                with st.chat_message("assistant"):
                    st.markdown(response)

else:
    st.info("Please select or create a profile to get started!")

# Save any changes to the current profile
if st.session_state.current_profile:
    st.session_state.user_manager.save_profile(st.session_state.current_profile)
