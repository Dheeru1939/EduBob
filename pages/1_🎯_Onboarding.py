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

# Progress indicator — dynamic question count (AI decides between MIN and MAX)
MIN_QUESTIONS = 3
MAX_QUESTIONS = 6
current_count = len(st.session_state.onboarding_qa)

if not st.session_state.onboarding_complete:
    # Visual progress: how close we are to the minimum at minimum, but show cap as the upper bound
    progress_pct = min(1.0, current_count / MAX_QUESTIONS)
    st.progress(progress_pct)
    if current_count < MIN_QUESTIONS:
        st.caption(f"Question {current_count + 1} (Watsonx asks 3–6 questions, depending on your answers)")
    else:
        st.caption(f"Question {current_count + 1} of up to {MAX_QUESTIONS} — Watsonx may stop early when it has enough")
else:
    st.progress(1.0)
    st.caption("Analyzing your profile...")

# Generate next question if needed (until cap reached or AI signals done)
if not st.session_state.current_question and current_count < MAX_QUESTIONS and not st.session_state.onboarding_complete:
    with st.spinner("Watsonx is crafting your next question..."):
        # Build prompt for next question
        prompt = build_onboarding_next_question_prompt(st.session_state.onboarding_qa)
        
        # Call watsonx.ai (questions are tiny — 200 tokens is plenty)
        response = generate(
            prompt=prompt,
            system="You are a friendly coding mentor conducting an onboarding interview.",
            max_tokens=200,
            temperature=0.5
        )
        
        # Parse response
        question_data = parse_json_response(response)
        
        if question_data and "question" in question_data:
            st.session_state.current_question = question_data
        else:
            # Fallback questions — covers all dimensions if AI fails
            # Final fallback always sets is_final at MIN_QUESTIONS or MAX_QUESTIONS
            fallback_questions = [
                {
                    "question": "Roughly which age range fits you best?",
                    "options": [
                        "Under 18 (still in school)",
                        "18–24 (college / early career)",
                        "25–34 (building my career)",
                        "35+ (established or pivoting)"
                    ],
                    "is_final": False
                },
                {
                    "question": "Which best describes your current situation?",
                    "options": [
                        "Student exploring tech",
                        "Working professional in a non-tech field (marketing, finance, healthcare, etc.)",
                        "Working professional in tech wanting more skills",
                        "Career switcher / returning to workforce / lifelong learner"
                    ],
                    "is_final": False
                },
                {
                    "question": "What field do you spend most of your time in?",
                    "options": [
                        "Marketing / Sales / Communications",
                        "Finance / Accounting / Operations",
                        "Healthcare / Education / Public Service",
                        "Engineering / Design / Tech / Other"
                    ],
                    "is_final": False
                },
                {
                    "question": "What do you most want to do with Python?",
                    "options": [
                        "Build websites or web tools",
                        "Automate tasks at work or home",
                        "Analyze data from my field",
                        "Explore AI / ML or just learn for fun"
                    ],
                    "is_final": False
                },
                {
                    "question": "How do you learn best?",
                    "options": [
                        "Hands-on with lots of examples",
                        "Step-by-step structured explanations",
                        "Project-based — build first, learn as I go",
                        "Mix of all three"
                    ],
                    # Mark final at MIN_QUESTIONS so we don't drag past 5 with fallbacks
                    "is_final": True
                },
                {
                    "question": "Anything else important about how you want to learn?",
                    "options": [
                        "I want it to be fun and casual",
                        "I want depth and challenge",
                        "I want short, daily-sized lessons",
                        "I want a steady, focused pace"
                    ],
                    "is_final": True
                }
            ]
            st.session_state.current_question = fallback_questions[min(current_count, len(fallback_questions) - 1)]
            # Force is_final at the cap regardless of fallback content
            if current_count >= MAX_QUESTIONS - 1:
                st.session_state.current_question["is_final"] = True

# Display current question
if st.session_state.current_question and not st.session_state.onboarding_complete:
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

        # Stop conditions:
        # - AI flagged is_final AND we've met the minimum question count
        # - Hard cap of MAX_QUESTIONS reached regardless of is_final
        new_count = len(st.session_state.onboarding_qa)
        ai_says_done = question.get('is_final', False)
        hit_minimum = new_count >= MIN_QUESTIONS
        hit_cap = new_count >= MAX_QUESTIONS

        if hit_cap or (ai_says_done and hit_minimum):
            st.session_state.onboarding_complete = True

        st.rerun()

# Generate interest profile when onboarding is complete
elif st.session_state.onboarding_complete and not st.session_state.profile:
    st.markdown("---")
    st.success("✅ Questions complete!")
    
    with st.spinner("🧠 Watsonx is analyzing your profile and creating your personalized curriculum..."):
        # Build profile generation prompt
        prompt = build_interest_profile_prompt(st.session_state.onboarding_qa)

        # Call watsonx.ai with retry + validation (profile is small JSON — 300 plenty)
        profile = generate_json(
            prompt=prompt,
            system="You are an educational AI analyzing learner profiles.",
            max_tokens=300,
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
            # Fallback profile — infer best-effort from QA history
            st.warning("⚠️ Could not parse profile. Using inferred defaults from your answers.")
            qa_text = " ".join([f"{qa['answer']}" for qa in st.session_state.onboarding_qa]).lower()

            # Infer age band
            if "under 18" in qa_text or "school" in qa_text:
                age = "under_18"
            elif "18" in qa_text or "24" in qa_text or "college" in qa_text:
                age = "18_24"
            elif "25" in qa_text or "34" in qa_text or "career" in qa_text:
                age = "25_34"
            else:
                age = "35_49"

            # Infer life context
            if "student" in qa_text:
                ctx = "student"
            elif "non-tech" in qa_text or "marketing" in qa_text or "finance" in qa_text:
                ctx = "mid_career_switcher"
            elif "tech wanting" in qa_text or "in tech" in qa_text:
                ctx = "early_career"
            elif "switcher" in qa_text or "returning" in qa_text or "lifelong" in qa_text:
                ctx = "mid_career_switcher"
            else:
                ctx = "early_career"

            # Infer interest
            if "data" in qa_text or "analyze" in qa_text:
                interest = "data"
            elif "automat" in qa_text:
                interest = "automation"
            elif "web" in qa_text:
                interest = "web"
            elif "ai" in qa_text or "ml" in qa_text:
                interest = "ai"
            else:
                interest = "general"

            st.session_state.profile = {
                "age_band": age,
                "life_context": ctx,
                "current_field": "general",
                "interests": [interest],
                "motivation": "learn Python for personal growth",
                "skill_level": "beginner",
                "preferred_style": "hands-on"
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
