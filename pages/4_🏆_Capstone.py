"""
EduBob v2 - Capstone Project Page
Personalized project that combines all learned topics
"""

import streamlit as st
from core.state import init_session
from core.watsonx_client import generate_json
from core.prompts import build_capstone_prompt

init_session()

st.title("🏆 Your Capstone Project")
st.caption("A personalized project that combines everything you've learned")

if not st.session_state.curriculum:
    st.warning("Complete at least one topic first.")
    st.stop()

# Generate or load capstone
if 'capstone' not in st.session_state or st.session_state.capstone is None:
    with st.spinner("🤖 Watsonx is designing your unique capstone project..."):
        prompt = build_capstone_prompt(
            st.session_state.profile,
            st.session_state.curriculum.get('topics', [])
        )
        # Retry-on-failure + validate the result has required fields
        capstone = generate_json(
            prompt=prompt,
            max_tokens=500,
            temperature=0.6,
            validator=lambda r: isinstance(r, dict) and "project_title" in r and "build_steps" in r,
        )
        st.session_state.capstone = capstone
        if capstone:
            st.snow()  # Moment of magic for capstone reveal

capstone = st.session_state.capstone
if not capstone:
    st.error("Could not generate capstone. Try refreshing.")
    st.stop()

# Hero card
st.markdown(f"## {capstone.get('project_title', 'Your Project')}")
st.markdown(f"*{capstone.get('elevator_pitch', '')}*")
st.markdown("---")

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("### 🛠️ Build Steps")
    for i, step in enumerate(capstone.get('build_steps', []), 1):
        st.markdown(f"**{i}.** {step}")

with col2:
    st.markdown("### 💡 Skills You'll Use")
    for skill in capstone.get('skills_used', []):
        st.markdown(f"- {skill}")
    st.metric("Estimated time", f"~{capstone.get('estimated_hours', 2)} hours")

st.markdown("---")
st.success("This project is uniquely generated for YOUR profile and learning path.")

if st.button("🔄 Generate a different project"):
    st.session_state.capstone = None
    st.rerun()

# Made with Bob
