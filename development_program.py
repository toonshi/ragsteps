import streamlit as st
from datetime import datetime, timedelta
from program_generator import ProgramGenerator
import plotly.graph_objects as go
import plotly.express as px

# Initialize the program generator
if 'program_generator' not in st.session_state:
    st.session_state.program_generator = ProgramGenerator()

st.title("Development Program")

# Check if a profile is selected
if 'current_profile' not in st.session_state or not st.session_state.current_profile:
    st.info("Please select a profile from the main page to view the development program.")
else:
    profile = st.session_state.current_profile
    
    # Create tabs for different program aspects
    program_tab, progress_tab, resources_tab = st.tabs([
        "Weekly Program", "Progress Tracking", "Resources & Guides"
    ])
    
    with program_tab:
        st.markdown(f"### {profile.name}'s Weekly Program")
        
        # Generate new program button
        if st.button("Generate New Weekly Program"):
            with st.spinner("Creating personalized program..."):
                weekly_program = st.session_state.program_generator.generate_weekly_program(profile)
                st.session_state.current_program = weekly_program
        
        # Display current program if it exists
        if hasattr(st.session_state, 'current_program'):
            for day in st.session_state.current_program:
                with st.expander(f"{day['day']} Activities"):
                    for activity in day['activities']:
                        st.markdown(f"**{activity['name']}** ({activity['duration']})")
                        st.write(activity['description'])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("View Detailed Guide", key=f"guide_{activity['name']}"):
                                guide = st.session_state.program_generator.generate_visual_guide(activity)
                                st.markdown(guide)
                        
                        with col2:
                            if st.button("Mark Complete", key=f"complete_{activity['name']}"):
                                st.text_area("How did it go? (Optional)", key=f"notes_{activity['name']}")
                                if st.button("Submit", key=f"submit_{activity['name']}"):
                                    notes = st.session_state[f"notes_{activity['name']}"]
                                    assessment = st.session_state.program_generator.assess_activity_completion(
                                        profile, 
                                        f"Activity: {activity['name']}\nNotes: {notes}"
                                    )
                                    st.success("Activity logged!")
                                    st.write(assessment['assessment'])
    
    with progress_tab:
        st.markdown("### Progress Tracking")
        
        # Create progress visualization
        if profile.progress_history:
            # Create timeline of completed milestones
            fig = go.Figure()
            
            for entry in profile.progress_history:
                fig.add_trace(go.Scatter(
                    x=[entry['date']],
                    y=[entry['milestone']],
                    mode='markers+text',
                    name=entry['milestone'],
                    text=[entry['milestone']],
                    textposition="top center"
                ))
            
            fig.update_layout(
                title="Milestone Timeline",
                xaxis_title="Date",
                yaxis_title="Milestones",
                showlegend=False
            )
            
            st.plotly_chart(fig)
            
            # Progress by category
            categories = {}
            for milestone in profile.milestones.values():
                if milestone.category not in categories:
                    categories[milestone.category] = {"completed": 0, "total": 0}
                categories[milestone.category]["total"] += 1
                if milestone.completed:
                    categories[milestone.category]["completed"] += 1
            
            # Create progress bars
            for category, data in categories.items():
                st.write(f"**{category}**")
                progress = data["completed"] / data["total"]
                st.progress(progress)
                st.write(f"{data['completed']}/{data['total']} completed")
        
        # Activity log
        st.markdown("### Recent Activities")
        if hasattr(st.session_state, 'program_generator') and \
           profile.profile_id in st.session_state.program_generator.programs:
            program = st.session_state.program_generator.programs[profile.profile_id]
            for note in program.progress_notes[-5:]:  # Show last 5 activities
                with st.expander(f"Activity on {note['date']}"):
                    st.write("**Log:**", note['log'])
                    st.write("**Assessment:**", note['assessment'])
    
    with resources_tab:
        st.markdown("### Resources & Guides")
        
        # Add resource categories
        resource_type = st.selectbox(
            "Select Resource Type",
            ["Activity Guides", "Development Information", "Parent Support", "Professional Resources"]
        )
        
        # Generate relevant resources based on profile and selection
        context = f"""
        Generate resources for:
        Resource Type: {resource_type}
        Child's Age: {profile.age_months} months
        Current Focus: {', '.join(profile.current_focus_areas)}
        
        Please provide:
        1. Relevant reading materials
        2. Activity suggestions
        3. Professional resources
        4. Support groups or communities
        """
        
        with st.spinner("Loading resources..."):
            resources = st.session_state.rag_system.query_knowledge_base(context)
            st.markdown(resources)
        
        # Add feedback section
        st.markdown("### Feedback")
        feedback = st.text_area("How are the current activities working? Any challenges?")
        if st.button("Submit Feedback"):
            with st.spinner("Adjusting program..."):
                adjustments = st.session_state.program_generator.adjust_program_difficulty(
                    profile, feedback
                )
                st.write("**Recommended Adjustments:**")
                st.write(adjustments['adjustments'])
