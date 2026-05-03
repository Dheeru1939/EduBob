"""
EduBob v2 - Adaptive AI Python Tutor
Main Streamlit Entry Point
"""

import streamlit as st
from core.state import init_session, reset_session, get_progress_summary

# Page configuration
st.set_page_config(
    page_title="EduBob — Your AI Python Tutor",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Initialize session state
# Global CSS styling
st.markdown("""
<style>
    /* Hero typography */
    h1 { font-weight: 700; letter-spacing: -0.5px; }
    /* Card-like containers */
    .stExpander { border: 1px solid #E2E8F0; border-radius: 12px; }
    /* AI badge styling */
    .ai-badge {
        display: inline-block;
        padding: 4px 12px;
        background: linear-gradient(135deg, #0066CC, #00A3E0);
        color: white;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    /* Adaptation banner */
    .adapt-banner {
        background: linear-gradient(135deg, #E0F2FE, #DBEAFE);
        border-left: 4px solid #0066CC;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 16px 0;
    }
    /* Fade-in animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .element-container { animation: fadeIn 0.4s ease-out; }
    .adapt-banner { animation: fadeIn 0.6s ease-out; }
</style>
""", unsafe_allow_html=True)

init_session()

# Sidebar
with st.sidebar:
    st.title("🤖 EduBob")
    st.markdown("*Your Adaptive AI Python Tutor*")
    st.markdown("---")
    
    # Progress summary
    if st.session_state.profile:
        progress = get_progress_summary()
        st.metric(
            "Progress",
            f"{progress['completed_topics']}/{progress['total_topics']} topics",
            f"{progress['completion_percentage']:.0f}%"
        )
        st.progress(progress['completion_percentage'] / 100)
    
    st.markdown("---")
    
    # AI Activity Log
    with st.expander("🧠 AI Activity Log"):
        log = st.session_state.get("ai_activity_log", [])
        if not log:
            st.caption("No AI calls yet")
        else:
            total_tokens = sum(item["tokens"] for item in log)
            st.metric("Total AI calls", len(log))
            st.metric("Tokens used", total_tokens)
            st.caption("**Recent activity:**")
            for item in log[-5:][::-1]:  # last 5, newest first
                st.caption(f"`{item['time']}` — {item['action']} ({item['tokens']}t)")
    
    st.markdown("---")
    
    # Reset button
    if st.button("🔄 Reset Session", use_container_width=True):
        reset_session()
        st.rerun()
    
    st.markdown("---")
    st.caption("Built with IBM Bob + watsonx.ai")

# Main content
st.title("🤖 Welcome to EduBob")

# Check onboarding status
if not st.session_state.profile:
    # User hasn't completed onboarding
    st.markdown("""
    ### Your Adaptive AI Python Tutor
    
    EduBob personalizes your learning journey:
    
    - 🎯 **Personalized curriculum** based on your interests
    - 📚 **AI-generated lessons** tailored to you
    - 💻 **Hands-on coding challenges** with instant feedback
    - 🔄 **Adaptive learning** that adjusts to your pace
    
    Let's get started by understanding what you want to learn!
    """)
    
    st.markdown("---")
    
    if st.button("🚀 Start Learning", type="primary", use_container_width=True):
        st.switch_page("pages/1_🎯_Onboarding.py")

elif not st.session_state.curriculum:
    # Profile exists but curriculum not generated yet
    st.info("✨ Generating your personalized curriculum...")
    st.switch_page("pages/2_📚_Curriculum.py")

else:
    # Show curriculum overview
    st.markdown(f"""
    ### {st.session_state.curriculum.get('track_title', 'Your Python Journey')}
    
    Your personalized learning path is ready! Continue where you left off or explore your curriculum.
    """)
    
    progress = get_progress_summary()
    
    # Show progress
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Topics Completed", f"{progress['completed_topics']}/5")
    with col2:
        st.metric("Current Topic", f"#{progress['current_topic']}")
    with col3:
        st.metric("Progress", f"{progress['completion_percentage']:.0f}%")
    
    st.markdown("---")
    
    # Quick actions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📚 View Curriculum", use_container_width=True):
            st.switch_page("pages/2_📚_Curriculum.py")
    
    with col2:
        # Find next unlocked topic
        from core.state import get_next_unlocked_topic
        next_topic = get_next_unlocked_topic()
        
        if next_topic:
            if st.button(f"▶️ Continue Topic {next_topic}", type="primary", use_container_width=True):
                st.session_state.current_topic_id = next_topic
                st.switch_page("pages/3_📖_Topic.py")
        else:
            st.success("🎉 All topics completed! Great job!")
    
    # Show recent topics
    if st.session_state.curriculum:
        st.markdown("### Your Topics")
        
        for topic in st.session_state.curriculum.get("topics", []):
            topic_id = topic["id"]
            
            # Determine status
            from core.state import is_topic_completed, is_topic_unlocked
            
            if is_topic_completed(topic_id):
                status = "✅ Completed"
                status_color = "green"
            elif is_topic_unlocked(topic_id):
                status = "🔓 Unlocked"
                status_color = "blue"
            else:
                status = "🔒 Locked"
                status_color = "gray"
            
            with st.expander(f"**Topic {topic_id}: {topic['title']}** — {status}"):
                st.markdown(topic['summary'])
                st.caption(f"⏱️ Estimated time: {topic['estimated_minutes']} minutes")
                
                if is_topic_unlocked(topic_id) and not is_topic_completed(topic_id):
                    if st.button(f"Start Topic {topic_id}", key=f"start_{topic_id}"):
                        st.session_state.current_topic_id = topic_id
                        st.switch_page("pages/3_📖_Topic.py")

# Footer
st.markdown("---")
st.caption("Powered by IBM watsonx.ai • Built with IBM Bob")

# Made with Bob
