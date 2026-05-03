"""
EduBob v2 - Adaptive AI Python Tutor
Main Streamlit Entry Point
"""

import streamlit as st
from core.state import init_session, reset_session, get_progress_summary, get_ai_failure_count
from core.learning_patterns import detect_learning_patterns

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
    /* Hero card on home page */
    .hero-card {
        background: linear-gradient(135deg, #0066CC 0%, #00A3E0 50%, #6366F1 100%);
        color: white;
        padding: 40px 32px;
        border-radius: 18px;
        margin: 8px 0 24px 0;
        box-shadow: 0 8px 24px rgba(0, 102, 204, 0.18);
    }
    .hero-card h2 { color: white !important; margin-top: 0; font-size: 32px; }
    .hero-card p { color: rgba(255,255,255,0.92); font-size: 16px; line-height: 1.6; margin: 8px 0; }
    .hero-tag {
        display: inline-block;
        background: rgba(255,255,255,0.18);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }
    /* Feature pills on home page */
    .feature-pill {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 16px;
        text-align: center;
        height: 100%;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .feature-pill:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.06);
    }
    .feature-pill .icon { font-size: 28px; margin-bottom: 8px; }
    .feature-pill .title { font-weight: 700; font-size: 14px; color: #1A1A1A; margin-bottom: 4px; }
    .feature-pill .desc { font-size: 12px; color: #64748B; }
    /* Topic flow breadcrumb */
    .flow-breadcrumb {
        display: flex;
        gap: 4px;
        margin: 8px 0 16px 0;
        font-size: 13px;
    }
    .flow-step {
        padding: 6px 14px;
        border-radius: 16px;
        background: #F0F4F8;
        color: #64748B;
        font-weight: 500;
    }
    .flow-step.active {
        background: linear-gradient(135deg, #0066CC, #00A3E0);
        color: white;
    }
    .flow-step.done {
        background: #DCFCE7;
        color: #166534;
    }
    /* Certificate styling */
    .cert-card {
        background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
        border: 3px double #D97706;
        border-radius: 12px;
        padding: 32px 28px;
        text-align: center;
        margin: 24px 0;
        box-shadow: 0 4px 12px rgba(217, 119, 6, 0.12);
    }
    .cert-card h2 { color: #92400E !important; margin: 0 0 8px 0; }
    .cert-card .cert-name { font-size: 24px; font-weight: 700; color: #1F2937; margin: 16px 0; }
    .cert-card .cert-stats { color: #4B5563; font-size: 14px; margin: 8px 0; }
    /* Fade-in animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .element-container { animation: fadeIn 0.4s ease-out; }
    .adapt-banner { animation: fadeIn 0.6s ease-out; }
    .hero-card { animation: fadeIn 0.5s ease-out; }
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
    
    # Your Learning Profile (multi-topic pattern view)
    if st.session_state.get("performance"):
        patterns_data = detect_learning_patterns(st.session_state.performance)
        with st.expander("🧬 Your Learning Profile", expanded=True):
            st.caption(patterns_data["summary"])
            stats = patterns_data["stats"]

            mc1, mc2 = st.columns(2)
            with mc1:
                st.metric("Avg quiz", f"{stats['avg_quiz_pct']}%")
                st.metric("Avg time", f"{stats['avg_time_seconds']}s")
            with mc2:
                st.metric("Avg code", f"{stats['avg_code_score']}/100")
                st.metric("Trend", stats['recent_trend'])

            if patterns_data["patterns"]:
                st.markdown("**Detected patterns:**")
                for p in patterns_data["patterns"]:
                    st.markdown(
                        f"<div style='padding:6px 10px; margin:4px 0; "
                        f"background:linear-gradient(135deg,#E0F2FE,#DBEAFE); "
                        f"border-left:3px solid #0066CC; border-radius:6px; font-size:13px;'>"
                        f"{p['icon']} <strong>{p['tag']}</strong><br>"
                        f"<span style='color:#555; font-size:12px;'>{p['evidence']}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("Complete more topics to reveal patterns.")

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
    
    # AI failure warning (shown only when there's a problem)
    failure_count = get_ai_failure_count()
    if failure_count >= 2:
        st.warning(
            f"⚠️ Watsonx.ai has failed {failure_count} consecutive times. "
            "Check your `.env` credentials, watsonx project quota, and internet. "
            "The app will keep working with fallback content."
        )

    st.markdown("---")
    st.caption("Built with IBM Bob + watsonx.ai")

# ============================================================================
# Main content
# ============================================================================

# Check onboarding status
if not st.session_state.profile:
    # ---------- Hero card ----------
    st.markdown("""
    <div class='hero-card'>
        <span class='hero-tag'>POWERED BY IBM watsonx.ai</span>
        <h2>🤖 Meet EduBob — Your Adaptive AI Python Tutor</h2>
        <p>EduBob doesn't just teach Python. It learns <strong>how you learn</strong>, then re-shapes
        every lesson, quiz, example, and project around your age, profession, interests, and pace.
        No two learners get the same curriculum.</p>
        <p style="margin-top:12px;">Built end-to-end with <strong>IBM Bob</strong>, powered by
        <strong>IBM watsonx.ai</strong>, in less than a day.</p>
    </div>
    """, unsafe_allow_html=True)

    # ---------- 4 feature pills ----------
    fcols = st.columns(4)
    features = [
        ("🎯", "Dynamic Onboarding", "AI asks 3-6 questions to deeply understand you"),
        ("📚", "Personalized Curriculum", "5 topics tailored to your field and goals"),
        ("🤖", "Adaptive Lessons", "Multi-mode explanations + AI chat per topic"),
        ("🧬", "Pattern Detection", "AI learns how you learn, evolves with you"),
    ]
    for col, (icon, title, desc) in zip(fcols, features):
        with col:
            st.markdown(f"""
            <div class='feature-pill'>
                <div class='icon'>{icon}</div>
                <div class='title'>{title}</div>
                <div class='desc'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("")

    # ---------- CTA + secondary info ----------
    cta_col1, cta_col2, cta_col3 = st.columns([1, 2, 1])
    with cta_col2:
        if st.button("🚀  Start Learning  →", type="primary", use_container_width=True):
            st.switch_page("pages/1_🎯_Onboarding.py")

    st.markdown("")
    with st.expander("💡 What makes this different from a generic tutorial?"):
        st.markdown("""
        Most tutorials show the same path to everyone. **EduBob is different:**

        - **A 32-year-old marketing manager** wanting to learn data → gets curriculum framed in
          campaign metrics, A/B tests, and audience segments
        - **A 16-year-old gamer** curious about web → gets curriculum framed in clan websites,
          gaming clans, and tournament data
        - **A 60-year-old retired teacher** learning for fun → gets gentle pace, recipe organizers,
          garden trackers, and patient tone

        Behind the scenes, **7 different watsonx.ai prompts** drive every product moment:
        onboarding, profile synthesis, curriculum design, lesson generation, code review,
        adaptation directives, and capstone project ideation.

        After every topic, watsonx analyzes your performance and re-shapes the next lesson's
        depth, examples, and tone. The pattern detection sidebar (visible after your first topic)
        shows you what EduBob has learned about you in real time.
        """)

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
