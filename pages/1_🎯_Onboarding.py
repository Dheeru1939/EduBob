"""
EduBob v2 - Onboarding Page
Dynamic AI-generated questions to understand learner interests
"""

import streamlit as st
import time
from core.state import init_session
from core.watsonx_client import generate, generate_json
from core.prompts import (
    build_onboarding_next_question_prompt,
    build_interest_profile_prompt,
    parse_json_response
)

# Initialize session
init_session()

# Page config
st.title("🎯 Getting to Know You")
st.markdown("Let's personalize your learning journey with a few quick questions.")

# Initialize onboarding state if needed
if 'onboarding_qa' not in st.session_state:
    st.session_state.onboarding_qa = []

if 'current_question' not in st.session_state:
    st.session_state.current_question = None

if 'onboarding_complete' not in st.session_state:
    st.session_state.onboarding_complete = False

# Progress indicator
total_questions = 3
current_count = len(st.session_state.onboarding_qa)

if current_count < total_questions:
    st.progress(current_count / total_questions)
    st.caption(f"Question {current_count + 1} of {total_questions}")
else:
    st.progress(1.0)
    st.caption("Analyzing your profile...")

# Generate next question if needed
if not st.session_state.current_question and current_count < total_questions:
    with st.spinner("Watsonx is crafting your next question..."):
        # Build prompt for next question
        prompt = build_onboarding_next_question_prompt(st.session_state.onboarding_qa)
        
        # Call watsonx.ai
        response = generate(
            prompt=prompt,
            system="You are a friendly coding mentor conducting an onboarding interview.",
            max_tokens=300,
            temperature=0.5
        )
        
        # Parse response
        question_data = parse_json_response(response)
        
        if question_data and "question" in question_data:
            st.session_state.current_question = question_data
        else:
            # Fallback questions — vary by which question we're on so we never repeat
            fallback_questions = [
                {
                    "question": "What's your current programming skill level?",
                    "options": [
                        "Absolute beginner (never coded before)",
                        "Beginner (some basic experience)",
                        "Intermediate (comfortable with basics)",
                        "Advanced (experienced programmer)"
                    ],
                    "is_final": False
                },
                {
                    "question": "What kind of projects excite you most?",
                    "options": [
                        "Websites and web apps",
                        "Automating boring tasks",
                        "Working with data and analytics",
                        "AI and machine learning"
                    ],
                    "is_final": False
                },
                {
                    "question": "How do you learn best?",
                    "options": [
                        "Hands-on with lots of examples",
                        "Reading concepts then practicing",
                        "Building real small projects",
                        "Watching, then trying it myself"
                    ],
                    "is_final": True
                }
            ]
            st.session_state.current_question = fallback_questions[min(current_count, 2)]

# Display current question
if st.session_state.current_question and current_count < total_questions:
    question = st.session_state.current_question
    
    st.markdown("---")
    st.markdown(f"### {question['question']}")
    
    # Radio buttons for options
    answer = st.radio(
        "Choose one:",
        options=question.get('options', []),
        key=f"q_{current_count}",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Submit button
    if st.button("Next →", type="primary", use_container_width=True):
        # Record the Q&A
        st.session_state.onboarding_qa.append({
            "question": question['question'],
            "answer": answer
        })
        
        # Clear current question to trigger next generation
        st.session_state.current_question = None
        
        # Check if this was the final question
        if question.get('is_final', False) or len(st.session_state.onboarding_qa) >= total_questions:
            st.session_state.onboarding_complete = True
        
        st.rerun()

# Generate interest profile when onboarding is complete
elif st.session_state.onboarding_complete and not st.session_state.profile:
    st.markdown("---")
    st.success("✅ Questions complete!")
    
    with st.spinner("🧠 Watsonx is analyzing your profile and creating your personalized curriculum..."):
        # Build profile generation prompt
        prompt = build_interest_profile_prompt(st.session_state.onboarding_qa)

        # Call watsonx.ai with retry + validation
        profile = generate_json(
            prompt=prompt,
            system="You are an educational AI analyzing learner profiles.",
            max_tokens=400,
            temperature=0.3,
            validator=lambda r: isinstance(r, dict) and "interests" in r and isinstance(r.get("interests"), list),
        )

        if profile:
            st.session_state.profile = profile
            
            # Show profile summary
            st.markdown("### Your Learning Profile")
            st.json(profile)
            
            time.sleep(1)  # Brief pause for user to see
            
            # Redirect to curriculum page
            st.info("🎓 Generating your personalized curriculum...")
            time.sleep(1)
            st.switch_page("pages/2_📚_Curriculum.py")
        else:
            # Fallback profile
            st.warning("⚠️ Could not parse profile. Using default settings.")
            st.session_state.profile = {
                "interests": ["general"],
                "motivation": "learn Python programming",
                "skill_level": "beginner",
                "preferred_style": "hands-on examples"
            }
            time.sleep(2)
            st.switch_page("pages/2_📚_Curriculum.py")

# Already have profile - redirect
elif st.session_state.profile:
    st.success("✅ Profile already created!")
    st.info("Redirecting to curriculum...")
    time.sleep(1)
    st.switch_page("pages/2_📚_Curriculum.py")

# Footer
st.markdown("---")
st.caption("Powered by IBM watsonx.ai • Questions generated in real-time")

# Made with Bob
