"""
EduBob v2 - Capstone Project Page
Personalized project that combines all learned topics, plus a completion
certificate when the learner has finished every topic.
"""

import streamlit as st
from datetime import datetime
from core.state import init_session
from core.watsonx_client import generate_json
from core.prompts import build_capstone_prompt
from core.learning_patterns import detect_learning_patterns

init_session()

st.title("🏆 Your Capstone Project")
st.caption("A personalized project that combines everything you've learned")

if not st.session_state.curriculum:
    st.warning("Complete at least one topic first.")
    st.stop()

# ---------- Generate or load capstone ----------
if 'capstone' not in st.session_state or st.session_state.capstone is None:
    with st.status("🤖 Watsonx is designing your unique capstone project...", expanded=True) as cs_status:
        st.write("📋 Reviewing your profile and completed topics...")
        prompt = build_capstone_prompt(
            st.session_state.profile,
            st.session_state.curriculum.get('topics', [])
        )
        st.write("✨ Combining all 5 topics into one cohesive project...")
        capstone = generate_json(
            prompt=prompt,
            max_tokens=400,
            temperature=0.6,
            validator=lambda r: isinstance(r, dict) and "project_title" in r and "build_steps" in r,
        )
        st.session_state.capstone = capstone
        if capstone:
            cs_status.update(label="🎉 Capstone designed!", state="complete", expanded=False)
            st.snow()
            st.toast("🏆 Capstone unlocked!", icon="🏆")
        else:
            cs_status.update(label="⚠️ Generation failed", state="error")

capstone = st.session_state.capstone
if not capstone:
    st.error("Could not generate capstone. Try refreshing.")
    st.stop()

# ---------- Hero card ----------
st.markdown(f"""
<div class='hero-card'>
    <span class='hero-tag'>YOUR PERSONALIZED CAPSTONE</span>
    <h2>🏆 {capstone.get('project_title', 'Your Project')}</h2>
    <p style="font-size: 17px; font-style: italic;">{capstone.get('elevator_pitch', '')}</p>
</div>
""", unsafe_allow_html=True)

# ---------- Build steps + sidebar info ----------
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

# ============================================================================
# COMPLETION CERTIFICATE — shown when ALL topics are completed
# ============================================================================
all_topics = st.session_state.curriculum.get('topics', [])
all_done = (
    all_topics
    and len(st.session_state.completed_topics) == len(all_topics)
)

if all_done:
    st.markdown("---")
    st.markdown("## 🎓 Course Complete")

    profile = st.session_state.profile or {}
    patterns_data = detect_learning_patterns(st.session_state.performance)
    stats = patterns_data.get("stats", {})
    pattern_tags = " · ".join(p["tag"] for p in patterns_data.get("patterns", [])[:3]) or "Determined Learner"

    learner_descriptor = profile.get("current_field", "Python learner")
    track = st.session_state.curriculum.get("track_title", "Python Learning Path")
    today = datetime.now().strftime("%B %d, %Y")

    total_minutes = sum(p.get("time_seconds", 0) for p in st.session_state.performance) // 60

    st.markdown(f"""
    <div class='cert-card'>
        <h2>📜 Certificate of Completion</h2>
        <p style="margin: 0; color: #92400E;">This certifies that</p>
        <div class='cert-name'>{learner_descriptor}</div>
        <p style="margin: 0; color: #4B5563;">has successfully completed</p>
        <p style="font-size: 18px; font-weight: 600; color: #1F2937; margin: 8px 0;">{track}</p>
        <hr style="border: none; border-top: 1px solid #D97706; margin: 16px 0; opacity: 0.4;" />
        <div class='cert-stats'>
            <strong>{len(all_topics)}</strong> topics completed ·
            <strong>~{total_minutes}</strong> total minutes ·
            <strong>{stats.get('avg_quiz_pct', 0)}%</strong> avg quiz ·
            <strong>{stats.get('avg_code_score', 0)}/100</strong> avg code
        </div>
        <div class='cert-stats' style="margin-top: 12px;">
            <strong>Watsonx-detected learner profile:</strong> {pattern_tags}
        </div>
        <p style="margin-top: 24px; font-size: 13px; color: #92400E;">
            Issued {today} · Powered by IBM watsonx.ai · Built with IBM Bob
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.balloons()

# Made with Bob
