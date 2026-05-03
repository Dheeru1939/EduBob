"""
EduBob v2 - Curriculum Page
Displays personalized 5-topic learning path with lock/unlock mechanics
"""

import streamlit as st
import time
from core.state import init_session, is_topic_unlocked, is_topic_completed
from core.watsonx_client import generate, generate_json
from core.prompts import build_curriculum_prompt, parse_json_response

# Initialize session
init_session()

# Page config
st.title("📚 Your Learning Path")

# Check if profile exists
if not st.session_state.profile:
    st.warning("⚠️ Please complete onboarding first.")
    if st.button("Go to Onboarding"):
        st.switch_page("pages/1_🎯_Onboarding.py")
    st.stop()

# Generate curriculum if not exists
if not st.session_state.curriculum:
    st.info("✨ Generating your personalized Python curriculum...")
    
    with st.spinner("🤖 Watsonx is designing your personal Python journey..."):
        # Build curriculum prompt
        prompt = build_curriculum_prompt(st.session_state.profile)

        # Call watsonx.ai with retry-on-failure + structural validation
        # Lower max_tokens for speed; higher temp for variety across users
        curriculum = generate_json(
            prompt=prompt,
            system="You are an expert curriculum designer creating PERSONALIZED Python learning paths. Always tailor topics to the learner's stated interests.",
            max_tokens=800,
            temperature=0.7,
            validator=lambda r: isinstance(r, dict) and "topics" in r and len(r.get("topics", [])) == 5,
        )

        if curriculum:
            st.session_state.curriculum = curriculum
            st.success("✅ Curriculum generated!")
            time.sleep(1)
            st.rerun()
        else:
            # Fallback curriculum — varies by primary interest so personalization is still visible
            st.warning("⚠️ AI generation incomplete. Using interest-tailored fallback.")
            interests = st.session_state.profile.get("interests", ["general"])
            primary = (interests[0] if interests else "general").lower()

            FALLBACK_BY_INTEREST = {
                "web": {
                    "track_title": "Python for Web-Curious Beginners",
                    "topics": [
                        {"id": 1, "title": "Strings — The Building Blocks of the Web", "summary": "Manipulate the text behind every URL, header, and HTML page.", "estimated_minutes": 15},
                        {"id": 2, "title": "Lists — Handling Multiple Items", "summary": "Manage collections like search results or user comments.", "estimated_minutes": 15},
                        {"id": 3, "title": "Dictionaries — JSON in Disguise", "summary": "Work with key-value data — the same shape every web API uses.", "estimated_minutes": 15},
                        {"id": 4, "title": "Functions — Reusable Web Helpers", "summary": "Bundle URL-cleaning and data-parsing into reusable tools.", "estimated_minutes": 15},
                        {"id": 5, "title": "Conditionals & Loops — Web Logic", "summary": "Filter items, validate input, and process pages programmatically.", "estimated_minutes": 15},
                    ],
                },
                "automation": {
                    "track_title": "Python for Automating Boring Stuff",
                    "topics": [
                        {"id": 1, "title": "Variables — What Your Scripts Remember", "summary": "Store the inputs your automations operate on.", "estimated_minutes": 15},
                        {"id": 2, "title": "Strings — Cleaning Real-World Text", "summary": "Strip, split, and reformat the messy text you'll see in real files.", "estimated_minutes": 15},
                        {"id": 3, "title": "Loops — Repeating Tasks at Scale", "summary": "Apply the same operation across hundreds of items.", "estimated_minutes": 15},
                        {"id": 4, "title": "Conditionals — Smart Decisions in Scripts", "summary": "Skip, retry, or branch based on what your script encounters.", "estimated_minutes": 15},
                        {"id": 5, "title": "Functions — Building Your Automation Toolkit", "summary": "Package recurring logic so future scripts get faster to write.", "estimated_minutes": 15},
                    ],
                },
                "data": {
                    "track_title": "Python for Aspiring Data Folks",
                    "topics": [
                        {"id": 1, "title": "Numbers and Lists — Foundations of Datasets", "summary": "Hold and inspect numeric series — the smallest possible dataset.", "estimated_minutes": 15},
                        {"id": 2, "title": "Dictionaries — One Record at a Time", "summary": "Represent a row of data the way every spreadsheet column does.", "estimated_minutes": 15},
                        {"id": 3, "title": "Loops — Iterating Over Records", "summary": "Compute totals, filters, and averages across many records.", "estimated_minutes": 15},
                        {"id": 4, "title": "Conditionals — Cleaning Messy Data", "summary": "Detect missing values, outliers, and apply rules.", "estimated_minutes": 15},
                        {"id": 5, "title": "Functions — Reusable Data Pipelines", "summary": "Wrap your cleaning steps into composable transformations.", "estimated_minutes": 15},
                    ],
                },
                "ai": {
                    "track_title": "Python for the AI-Curious",
                    "topics": [
                        {"id": 1, "title": "Variables and Math — How Models Store Knowledge", "summary": "Numbers, weights, and parameters all live in plain Python variables.", "estimated_minutes": 15},
                        {"id": 2, "title": "Lists — Vectors in Disguise", "summary": "The same shape used in every neural network input.", "estimated_minutes": 15},
                        {"id": 3, "title": "Conditionals — The Logic Behind Decisions", "summary": "Every classifier eventually decides via if-this-then-that.", "estimated_minutes": 15},
                        {"id": 4, "title": "Loops — Iterating Through Data", "summary": "Train, predict, evaluate — all loops over data.", "estimated_minutes": 15},
                        {"id": 5, "title": "Functions — Composing AI Pipelines", "summary": "Pre-process → predict → post-process — pure functions chained together.", "estimated_minutes": 15},
                    ],
                },
                "games": {
                    "track_title": "Python for Future Game Builders",
                    "topics": [
                        {"id": 1, "title": "Variables — Tracking Score, Lives, and Time", "summary": "Game state is just well-named variables.", "estimated_minutes": 15},
                        {"id": 2, "title": "Conditionals — Win, Lose, or Continue", "summary": "Implement the rules that decide what happens next.", "estimated_minutes": 15},
                        {"id": 3, "title": "Loops — The Game Loop", "summary": "The heartbeat of every game runs on a loop.", "estimated_minutes": 15},
                        {"id": 4, "title": "Lists — Inventories, Boards, Levels", "summary": "Most game state is collections of items.", "estimated_minutes": 15},
                        {"id": 5, "title": "Functions — Building Reusable Game Mechanics", "summary": "Spawn, move, score — each becomes a small function.", "estimated_minutes": 15},
                    ],
                },
            }

            st.session_state.curriculum = FALLBACK_BY_INTEREST.get(primary, {
                "track_title": f"Python Fundamentals for {primary.title()} Enthusiasts",
                "topics": [
                    {"id": 1, "title": "Variables and Data Types", "summary": "Learn to store and work with different types of data in Python.", "estimated_minutes": 15},
                    {"id": 2, "title": "Control Flow: If Statements", "summary": "Make decisions in your code with conditional logic.", "estimated_minutes": 15},
                    {"id": 3, "title": "Loops and Iteration", "summary": "Repeat actions efficiently with for and while loops.", "estimated_minutes": 15},
                    {"id": 4, "title": "Functions and Modularity", "summary": "Organize your code into reusable functions.", "estimated_minutes": 15},
                    {"id": 5, "title": "Lists and Data Structures", "summary": "Work with collections of data using Python's built-in structures.", "estimated_minutes": 15},
                ],
            })
            time.sleep(1)
            st.rerun()

# Display curriculum
curriculum = st.session_state.curriculum

st.markdown(f"## {curriculum.get('track_title', 'Your Python Journey')}")
st.markdown("Complete topics in order to unlock the next one. Each topic includes a lesson, quiz, and coding challenge.")

# Personalization meter
completed_count = len(st.session_state.completed_topics)
personalization_pct = min(100, 40 + completed_count * 15)  # starts at 40%, grows with completions

st.markdown(f"""
<div class='adapt-banner'>
    <strong>🧬 Curriculum personalization: {personalization_pct}%</strong><br>
    <span style='font-size: 13px;'>
        Watsonx has analyzed {completed_count} of your completed topics and is continuously refining
        the lessons, examples, and pacing for the topics ahead.
    </span>
</div>
""", unsafe_allow_html=True)

# Show what's been refined
if completed_count > 0:
    with st.expander("🔄 What's been refined for you"):
        last_directives = st.session_state.adaptation_history[-3:] if st.session_state.adaptation_history else []
        if last_directives:
            for entry in last_directives:
                d = entry.get('directive', {})
                st.markdown(f"""
                **Topic {entry['topic_id']}** — adjusted to:
                - Depth: `{d.get('depth', 'standard')}`
                - Examples: `{d.get('examples_flavor', 'general')}`
                - Tone: `{d.get('tone', 'standard')}`
                - Emphasis: *{d.get('extra_emphasis', 'core concepts')}*
                """)
        else:
            st.caption("Complete a topic to see live personalization.")

# Why this curriculum explainer
with st.expander("💡 Why this curriculum?"):
    profile = st.session_state.profile
    st.markdown(f"""
    Watsonx.ai analyzed your onboarding answers and built this curriculum because:
    - **Your interests:** {', '.join(profile.get('interests', []))}
    - **Your motivation:** {profile.get('motivation', 'learning Python')}
    - **Your skill level:** {profile.get('skill_level', 'beginner')}
    - **Your preferred style:** {profile.get('preferred_style', 'hands-on')}
    
    Topics, ordering, and examples are all tailored to this profile.
    """)

# Show learner profile summary
with st.expander("👤 Your Learning Profile"):
    profile = st.session_state.profile
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Interests:**")
        for interest in profile.get("interests", []):
            st.markdown(f"- {interest}")
        st.markdown(f"**Skill Level:** {profile.get('skill_level', 'beginner')}")
    
    with col2:
        st.markdown(f"**Motivation:** {profile.get('motivation', 'learn Python')}")
        st.markdown(f"**Learning Style:** {profile.get('preferred_style', 'hands-on')}")

st.markdown("---")

# Display topics
for topic in curriculum.get("topics", []):
    topic_id = topic["id"]
    title = topic["title"]
    summary = topic["summary"]
    estimated_minutes = topic.get("estimated_minutes", 15)
    
    # Determine status
    is_completed = is_topic_completed(topic_id)
    is_unlocked = is_topic_unlocked(topic_id)
    
    # Status badge
    if is_completed:
        status_badge = "✅"
        status_text = "Completed"
        card_color = "#d4edda"  # Light green
    elif is_unlocked:
        status_badge = "🔓"
        status_text = "Unlocked"
        card_color = "#d1ecf1"  # Light blue
    else:
        status_badge = "🔒"
        status_text = "Locked"
        card_color = "#f8f9fa"  # Light gray
    
    # Create topic card
    with st.container():
        st.markdown(
            f"""
            <div style="
                padding: 20px;
                border-radius: 10px;
                background-color: {card_color};
                border-left: 5px solid {'#28a745' if is_completed else '#007bff' if is_unlocked else '#6c757d'};
                margin-bottom: 15px;
            ">
                <h3 style="margin: 0 0 10px 0;">{status_badge} Topic {topic_id}: {title}</h3>
                <p style="margin: 0 0 10px 0; color: #666;">{summary}</p>
                <p style="margin: 0; font-size: 0.9em; color: #888;">⏱️ Estimated time: {estimated_minutes} minutes • Status: {status_text}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Action button
        if is_unlocked and not is_completed:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(f"▶️ Start Topic {topic_id}", key=f"start_{topic_id}", type="primary", use_container_width=True):
                    st.session_state.current_topic_id = topic_id
                    st.switch_page("pages/3_📖_Topic.py")
        
        elif is_completed:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(f"📖 Review Topic {topic_id}", key=f"review_{topic_id}", use_container_width=True):
                    st.session_state.current_topic_id = topic_id
                    st.switch_page("pages/3_📖_Topic.py")
        
        elif not is_unlocked:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.button(
                    f"🔒 Complete Topic {topic_id - 1} First",
                    key=f"locked_{topic_id}",
                    disabled=True,
                    use_container_width=True
                )

# Progress summary
st.markdown("---")
completed_count = len(st.session_state.completed_topics)
total_count = len(curriculum.get("topics", []))

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Topics Completed", f"{completed_count}/{total_count}")
with col2:
    progress_pct = (completed_count / total_count) * 100
    st.metric("Progress", f"{progress_pct:.0f}%")
with col3:
    if completed_count == total_count:
        st.metric("Status", "🎉 Complete!")
    else:
        st.metric("Next", f"Topic {completed_count + 1}")

# Progress bar
st.progress(progress_pct / 100)

# Navigation
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("app.py")

with col2:
    # Find next unlocked topic
    from core.state import get_next_unlocked_topic
    next_topic = get_next_unlocked_topic()
    
    if next_topic:
        if st.button(f"▶️ Continue to Topic {next_topic}", type="primary", use_container_width=True):
            st.session_state.current_topic_id = next_topic
            st.switch_page("pages/3_📖_Topic.py")

# Footer
st.markdown("---")
st.caption("Curriculum powered by IBM watsonx.ai • Personalized to your interests")

# Made with Bob
