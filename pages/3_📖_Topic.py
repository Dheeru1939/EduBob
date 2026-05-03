"""
EduBob v2 - Topic Page
Three-tab interface: Lesson → Quiz → Challenge
"""

import streamlit as st
import time
from datetime import datetime
from streamlit_ace import st_ace
from core.state import (
    init_session, 
    is_topic_unlocked, 
    is_topic_completed,
    record_performance,
    get_adaptation_directive
)
from core.watsonx_client import generate, generate_json
from core.prompts import (
    build_topic_content_prompt,
    build_code_feedback_prompt,
    build_topic_chat_prompt,
    build_lesson_mode_prompt,
    build_video_queries_prompt,
    parse_json_response
)
import streamlit.components.v1 as components
import json as _json
import urllib.parse as _urlparse
from core.code_runner import run_code_with_tests
from core.adaptation import compute_next_directive

# Initialize session
init_session()

# Get current topic
current_topic_id = st.session_state.current_topic_id

# Validate access
if not st.session_state.curriculum:
    st.warning("⚠️ Please complete onboarding first.")
    if st.button("Go to Curriculum"):
        st.switch_page("pages/2_📚_Curriculum.py")
    st.stop()

if not is_topic_unlocked(current_topic_id):
    st.error(f"🔒 Topic {current_topic_id} is locked. Complete previous topics first.")
    if st.button("Back to Curriculum"):
        st.switch_page("pages/2_📚_Curriculum.py")
    st.stop()

# Get topic info
topics = st.session_state.curriculum.get("topics", [])
current_topic = None
for topic in topics:
    if topic["id"] == current_topic_id:
        current_topic = topic
        break

if not current_topic:
    st.error("Topic not found")
    st.stop()

# Page header
st.title(f"📖 Topic {current_topic_id}: {current_topic['title']}")
st.markdown(current_topic['summary'])
st.markdown("---")

# Generate topic content if not cached
if current_topic_id not in st.session_state.topic_contents:
    st.info("✨ Generating personalized content for this topic...")
    
    with st.spinner("🤖 Watsonx is preparing your lesson, quiz, and challenge..."):
        # Forced directive (set when user requests a regeneration after failing) takes precedence
        forced_directive = st.session_state.get(f'forced_directive_{current_topic_id}')
        if forced_directive:
            adaptation_directive = forced_directive
            # Consume the forced directive so it only applies once per regeneration
            del st.session_state[f'forced_directive_{current_topic_id}']
        else:
            adaptation_directive = get_adaptation_directive(current_topic_id)

        # Build prompt
        prompt = build_topic_content_prompt(
            topic_spec=current_topic,
            profile=st.session_state.profile,
            adaptation_directive=adaptation_directive
        )

        # Call watsonx.ai with retry + schema validation
        # max_tokens 1000 — lesson 200-400 words + 3 quiz Qs + challenge fits in ~700-900 tokens
        content = generate_json(
            prompt=prompt,
            system="You are an expert Python educator creating engaging, personalized learning content.",
            max_tokens=1000,
            temperature=0.5,
            validator=lambda r: (
                isinstance(r, dict)
                and "lesson_markdown" in r
                and "quiz" in r
                and "challenge" in r
                and isinstance(r.get("quiz"), list)
                and len(r.get("quiz", [])) >= 1
            ),
        )

        if content:
            st.session_state.topic_contents[current_topic_id] = content
            st.success("✅ Content generated!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("⚠️ Could not generate content. Please try again.")
            if st.button("Retry"):
                st.rerun()
            st.stop()

# Get topic content
topic_content = st.session_state.topic_contents[current_topic_id]

# Initialize topic-specific state
if f'quiz_submitted_{current_topic_id}' not in st.session_state:
    st.session_state[f'quiz_submitted_{current_topic_id}'] = False

if f'quiz_score_{current_topic_id}' not in st.session_state:
    st.session_state[f'quiz_score_{current_topic_id}'] = 0

if f'code_submitted_{current_topic_id}' not in st.session_state:
    st.session_state[f'code_submitted_{current_topic_id}'] = False

if f'code_feedback_{current_topic_id}' not in st.session_state:
    st.session_state[f'code_feedback_{current_topic_id}'] = None

if f'start_time_{current_topic_id}' not in st.session_state:
    st.session_state[f'start_time_{current_topic_id}'] = time.time()

# Show adaptation banner if this topic was adapted
adaptation_directive = get_adaptation_directive(current_topic_id)
if adaptation_directive:
    st.markdown(f"""
    <div class='adapt-banner'>
        <strong>🎯 Adapted for you:</strong>
        Based on your performance in Topic {current_topic_id - 1},
        this lesson is <strong>{adaptation_directive.get('depth', 'standard')}</strong>
        with <strong>{adaptation_directive.get('examples_flavor', 'general')}</strong> examples.
        Tone: <em>{adaptation_directive.get('tone', 'standard').replace('_', ' ')}</em>.
    </div>
    """, unsafe_allow_html=True)

# Initialize per-topic chat history (shown inline on the Lesson tab)
if f'chat_history_{current_topic_id}' not in st.session_state:
    st.session_state[f'chat_history_{current_topic_id}'] = []

# Initialize regeneration counter (caps to prevent infinite re-asks)
if f'regen_count_{current_topic_id}' not in st.session_state:
    st.session_state[f'regen_count_{current_topic_id}'] = 0
MAX_REGENERATIONS = 2


def _request_topic_regeneration(reason_tag: str):
    """Clear cached topic content + force a shallower/encouraging directive, then rerun."""
    forced = {
        "depth": "shallower",
        "examples_flavor": (st.session_state.profile.get("interests", ["general"]) or ["general"])[0],
        "extra_emphasis": "fundamentals — explain what this concept actually does in plain English first, then show it",
        "tone": "more_encouraging",
    }
    st.session_state[f'forced_directive_{current_topic_id}'] = forced
    # Clear all caches related to this topic
    for k in [
        f'topic_contents',  # we'll handle differently below
    ]:
        pass
    if current_topic_id in st.session_state.get('topic_contents', {}):
        del st.session_state['topic_contents'][current_topic_id]
    for key_prefix in [
        f'lesson_modes_', f'lesson_revealed_', f'quiz_submitted_',
        f'quiz_score_', f'video_queries_',
    ]:
        full_key = f'{key_prefix}{current_topic_id}'
        if full_key in st.session_state:
            del st.session_state[full_key]
    st.session_state[f'regen_count_{current_topic_id}'] = (
        st.session_state.get(f'regen_count_{current_topic_id}', 0) + 1
    )
    st.session_state[f'last_regen_reason_{current_topic_id}'] = reason_tag
    st.rerun()


# Three tabs (Lesson, Quiz, Challenge). Chat lives inside Lesson tab now.
tab1, tab2, tab3 = st.tabs(["📚 Lesson", "❓ Quiz", "💻 Challenge"])

# ============================================================================
# TAB 1: LESSON (with multi-mode explanations + voice narration)
# ============================================================================
with tab1:
    # ---------- Regeneration banner (shown right after a refresh-on-fail) ----------
    last_reason = st.session_state.get(f'last_regen_reason_{current_topic_id}')
    if last_reason:
        if last_reason == "quiz_fail":
            st.success(
                "🔄 **Lesson refreshed for you.** Watsonx noticed you missed some quiz questions, "
                "so this version is shallower, more encouraging, and grounded in fundamentals. Take your time — "
                "and use the chat below if anything still feels unclear."
            )
        elif last_reason == "code_fail":
            st.success(
                "🔄 **Lesson refreshed for you.** Watsonx noticed the code challenge was tough, "
                "so this version focuses on the building blocks first. Re-read it, then head back to the challenge."
            )
        # Show the banner only once per regeneration
        del st.session_state[f'last_regen_reason_{current_topic_id}']

    # ---------- Mode selector: Standard / Example / Walkthrough / Analogy ----------
    mode_label_to_key = {
        "📖 Standard": "standard",
        "🌍 Real Example": "real_example",
        "🔍 Code Walkthrough": "code_walkthrough",
        "🎯 Analogy": "analogy",
    }
    selected_label = st.radio(
        "How would you like this explained?",
        options=list(mode_label_to_key.keys()),
        horizontal=True,
        key=f"lesson_mode_{current_topic_id}",
        help="Standard = the original lesson. Other modes re-explain the same concept differently — generated on demand by Watsonx.",
    )
    selected_mode = mode_label_to_key[selected_label]

    # Cache lazy-loaded modes per topic
    if f'lesson_modes_{current_topic_id}' not in st.session_state:
        st.session_state[f'lesson_modes_{current_topic_id}'] = {}
    modes_cache = st.session_state[f'lesson_modes_{current_topic_id}']

    if selected_mode == "standard":
        # Stream lesson on first reveal for visual effect
        if not st.session_state.get(f'lesson_revealed_{current_topic_id}', False):
            lesson_text = topic_content['lesson_markdown']
            st.write_stream((char for char in lesson_text))
            st.session_state[f'lesson_revealed_{current_topic_id}'] = True
        else:
            st.markdown(topic_content['lesson_markdown'])
        current_lesson_text = topic_content['lesson_markdown']
    else:
        # Lazy-load alternative mode
        if selected_mode not in modes_cache:
            with st.spinner(f"Watsonx is preparing the {selected_label.split(' ', 1)[1].lower()} version..."):
                alt_prompt = build_lesson_mode_prompt(
                    topic_title=current_topic['title'],
                    lesson_markdown=topic_content['lesson_markdown'],
                    profile=st.session_state.profile,
                    mode=selected_mode,
                )
                alt_text = generate(
                    prompt=alt_prompt,
                    max_tokens=400,
                    temperature=0.6,
                )
                if not alt_text or alt_text == "{}":
                    alt_text = "_(Watsonx had trouble generating this version. Try Standard or another mode.)_"
                modes_cache[selected_mode] = alt_text
                st.session_state[f'lesson_modes_{current_topic_id}'] = modes_cache
        st.markdown(modes_cache[selected_mode])
        current_lesson_text = modes_cache[selected_mode]

    # ---------- Voice narration (browser TTS, zero LLM cost) ----------
    st.markdown("")
    # Strip markdown markers so TTS sounds clean
    import re as _re
    speakable = _re.sub(r'[#*`_~\[\]()>]', '', current_lesson_text)
    speakable_js = _json.dumps(speakable)  # safely JSON-escape for JS string

    components.html(f"""
    <div style="display:flex; gap:8px; align-items:center;">
        <button onclick="edubobSpeak()" style="
            background: linear-gradient(135deg, #0066CC, #00A3E0);
            color: white;
            border: none;
            padding: 8px 18px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
        ">🔊 Listen to this lesson</button>
        <button onclick="edubobStop()" style="
            background: #EF4444;
            color: white;
            border: none;
            padding: 8px 18px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
        ">⏸ Stop</button>
        <span id="edubob_status" style="font-size:13px; color:#666; margin-left:8px;"></span>
    </div>
    <script>
        const lessonText_{current_topic_id}_{selected_mode} = {speakable_js};
        function edubobSpeak() {{
            window.speechSynthesis.cancel();
            const utt = new SpeechSynthesisUtterance(lessonText_{current_topic_id}_{selected_mode});
            utt.rate = 1.0;
            utt.pitch = 1.0;
            utt.volume = 1.0;
            utt.onstart = () => document.getElementById('edubob_status').textContent = '🔊 Speaking...';
            utt.onend = () => document.getElementById('edubob_status').textContent = '✓ Done';
            utt.onerror = () => document.getElementById('edubob_status').textContent = '⚠ Speech failed';
            window.speechSynthesis.speak(utt);
        }}
        function edubobStop() {{
            window.speechSynthesis.cancel();
            document.getElementById('edubob_status').textContent = '⏹ Stopped';
        }}
    </script>
    """, height=55)

    st.markdown("---")

    # ---------- AI-curated video tutorials (lazy-loaded) ----------
    st.markdown("### 🎥 Watch related videos")
    st.caption("Watsonx picked these YouTube searches based on your topic and profile.")

    video_cache_key = f'video_queries_{current_topic_id}'
    if video_cache_key not in st.session_state:
        if st.button("Generate video recommendations", key=f"gen_videos_{current_topic_id}"):
            with st.spinner("Watsonx is finding the best tutorial searches for you..."):
                vq_prompt = build_video_queries_prompt(
                    topic_title=current_topic['title'],
                    topic_summary=current_topic.get('summary', ''),
                    profile=st.session_state.profile,
                )
                vq_result = generate_json(
                    prompt=vq_prompt,
                    max_tokens=300,
                    temperature=0.5,
                    validator=lambda r: isinstance(r, dict) and isinstance(r.get("queries"), list) and len(r["queries"]) >= 1,
                )
                if vq_result:
                    st.session_state[video_cache_key] = vq_result["queries"][:3]
                else:
                    # Fallback: 1 generic query so the button is never empty
                    st.session_state[video_cache_key] = [
                        {"label": f"📺 {current_topic['title']} tutorial", "query": f"python {current_topic['title']} tutorial for beginners"}
                    ]
                st.rerun()
    else:
        # Render the cached queries as link buttons
        queries = st.session_state[video_cache_key]
        cols = st.columns(len(queries))
        for col, q in zip(cols, queries):
            with col:
                yt_url = f"https://www.youtube.com/results?search_query={_urlparse.quote(q['query'])}"
                st.link_button(q['label'], yt_url, use_container_width=True)
                st.caption(f"_{q['query']}_")
        # Allow regen
        if st.button("🔄 Regenerate video picks", key=f"regen_videos_{current_topic_id}"):
            del st.session_state[video_cache_key]
            st.rerun()

    st.markdown("---")

    # ---------- 💬 Ask Watsonx (lives inside the Lesson tab; not on Quiz/Challenge) ----------
    chat_key = f'chat_history_{current_topic_id}'
    chat_history = st.session_state[chat_key]

    with st.expander("💬 Ask Watsonx anything about this topic", expanded=bool(chat_history)):
        st.caption("Confused or curious? Watsonx has the lesson loaded.")

        # Quick-prompt buttons
        quick_cols = st.columns(3)
        quick_prompts = [
            ("🧒 ELI5", "Explain this topic to me like I'm 5 years old."),
            ("🌍 Real example", "Give me a real-world example using something from my field."),
            ("⚠️ Common mistake", "What's the most common mistake beginners make with this concept?"),
        ]
        pending_question = None
        for col, (label, prompt) in zip(quick_cols, quick_prompts):
            with col:
                if st.button(label, key=f"quick_{label}_{current_topic_id}", use_container_width=True):
                    pending_question = prompt

        # Render existing chat history
        if chat_history:
            st.markdown("---")
        for msg in chat_history:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])

        # Free-form input
        typed_question = st.chat_input("Type your question...", key=f"chat_input_{current_topic_id}")
        user_question = pending_question or typed_question

        if user_question:
            chat_history.append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)
            with st.chat_message("assistant"):
                with st.spinner("Watsonx is thinking..."):
                    chat_prompt = build_topic_chat_prompt(
                        topic_title=current_topic['title'],
                        lesson_markdown=topic_content.get('lesson_markdown', ''),
                        profile=st.session_state.profile,
                        chat_history=chat_history[:-1],
                        user_question=user_question,
                    )
                    answer = generate(prompt=chat_prompt, max_tokens=350, temperature=0.5)
                    if not answer or answer == "{}":
                        answer = "Hmm, I'm having trouble responding right now. Try rephrasing, or check the AI Activity Log in the sidebar."
                    st.markdown(answer)
            chat_history.append({"role": "assistant", "content": answer})
            st.session_state[chat_key] = chat_history
            st.rerun()

        if chat_history:
            if st.button("🗑️ Clear chat", key=f"clear_chat_{current_topic_id}"):
                st.session_state[chat_key] = []
                st.rerun()

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Take Quiz →", type="primary", use_container_width=True, key=f"goto_quiz_{current_topic_id}"):
            # Auto-switch to the Quiz tab via JS (Streamlit tabs don't support programmatic switch natively)
            components.html("""
            <script>
                const tabs = window.parent.document.querySelectorAll('button[role="tab"]');
                if (tabs.length > 1) tabs[1].click();
            </script>
            """, height=0)

# ============================================================================
# TAB 2: QUIZ
# ============================================================================
with tab2:
    quiz = topic_content['quiz']
    
    if not st.session_state[f'quiz_submitted_{current_topic_id}']:
        st.markdown("### Test Your Understanding")
        st.markdown("Answer these questions based on the lesson.")
        
        quiz_answers = []
        
        for i, question in enumerate(quiz):
            st.markdown(f"**Question {i+1}:** {question['question']}")
            answer = st.radio(
                "Choose one:",
                options=question['options'],
                key=f"quiz_q{i}_{current_topic_id}",
                label_visibility="collapsed"
            )
            quiz_answers.append(answer)
            st.markdown("")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Submit Quiz", type="primary", use_container_width=True):
                # Grade quiz
                correct_count = 0
                for i, question in enumerate(quiz):
                    correct_index = question['correct_index']
                    if quiz_answers[i] == question['options'][correct_index]:
                        correct_count += 1
                
                st.session_state[f'quiz_score_{current_topic_id}'] = correct_count
                st.session_state[f'quiz_submitted_{current_topic_id}'] = True
                st.rerun()
    
    else:
        # Show results
        score = st.session_state[f'quiz_score_{current_topic_id}']
        total = len(quiz)
        percentage = (score / total) * 100
        
        if percentage == 100:
            st.success(f"🎉 Perfect score! {score}/{total} correct!")
        elif percentage >= 67:
            st.success(f"✅ Good job! {score}/{total} correct!")
        else:
            st.warning(f"📝 You got {score}/{total} correct. Don't worry — let's reinforce these concepts.")

        # Show correct answers
        with st.expander("📋 Review Answers"):
            for i, question in enumerate(quiz):
                correct_index = question['correct_index']
                correct_answer = question['options'][correct_index]
                st.markdown(f"**Q{i+1}:** {question['question']}")
                st.markdown(f"✅ **Correct answer:** {correct_answer}")
                st.markdown("")

        # ---------- Fail handling: offer to regenerate topic if score is low ----------
        regen_count = st.session_state.get(f'regen_count_{current_topic_id}', 0)
        if percentage < 67 and regen_count < MAX_REGENERATIONS:
            st.markdown("---")
            st.info(
                "🤔 **Want Watsonx to re-explain this topic differently?** "
                "It will rewrite the lesson with a shallower depth, more encouraging tone, "
                "and clearer fundamentals — tailored to where you struggled."
            )
            cregen1, cregen2 = st.columns(2)
            with cregen1:
                if st.button("🔄 Yes — regenerate this topic", type="primary",
                             key=f"regen_after_quiz_{current_topic_id}", use_container_width=True):
                    _request_topic_regeneration("quiz_fail")
            with cregen2:
                if st.button("👉 No thanks — try the challenge anyway",
                             key=f"skip_regen_after_quiz_{current_topic_id}", use_container_width=True):
                    pass  # falls through to Continue button below
        elif percentage < 67 and regen_count >= MAX_REGENERATIONS:
            st.markdown("---")
            st.info(
                "💡 You've already regenerated this topic. Try the challenge or use the chat on the "
                "Lesson tab to ask Watsonx anything specific."
            )

        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Continue to Challenge →", type="primary", use_container_width=True, key=f"goto_challenge_{current_topic_id}"):
                # Auto-switch to Challenge tab (index 2)
                components.html("""
                <script>
                    const tabs = window.parent.document.querySelectorAll('button[role="tab"]');
                    if (tabs.length > 2) tabs[2].click();
                </script>
                """, height=0)

# ============================================================================
# TAB 3: CHALLENGE
# ============================================================================
with tab3:
    challenge = topic_content['challenge']
    
    st.markdown("### Coding Challenge")
    st.markdown(challenge['prompt'])
    
    st.markdown("---")
    
    # Code editor
    if f'code_input_{current_topic_id}' not in st.session_state:
        st.session_state[f'code_input_{current_topic_id}'] = challenge['starter_code']
    
    st.markdown("**Write your code here:**")
    code = st_ace(
        value=st.session_state[f'code_input_{current_topic_id}'],
        language='python',
        theme='monokai',
        height=300,
        font_size=14,
        show_gutter=True,
        show_print_margin=False,
        wrap=False,
        auto_update=True,
        key=f"ace_editor_{current_topic_id}"
    )
    
    st.session_state[f'code_input_{current_topic_id}'] = code
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Reset to Starter Code", use_container_width=True):
            st.session_state[f'code_input_{current_topic_id}'] = challenge['starter_code']
            st.rerun()
    
    with col2:
        if st.button("▶️ Run & Submit", type="primary", use_container_width=True):
            with st.spinner("Running your code and testing..."):
                # Run tests
                test_results = run_code_with_tests(
                    code=code,
                    test_cases=challenge['test_cases'],
                    timeout_s=5
                )
                
                # Display test results
                st.markdown("### Test Results")
                
                passed = test_results['passed']
                failed = test_results['failed']
                total = passed + failed
                
                if test_results.get('error') and not test_results['results']:
                    st.error(f"❌ Execution Error: {test_results['error']}")

                    # Try to extract line number from the error and highlight it
                    import re
                    line_match = re.search(r'line\s+(\d+)', test_results['error'])
                    if line_match:
                        bad_line_num = int(line_match.group(1))
                        code_lines = code.split('\n')
                        if 0 < bad_line_num <= len(code_lines):
                            bad_line_text = code_lines[bad_line_num - 1]
                            st.markdown(f"**Look at line {bad_line_num} of your code:**")
                            st.code(f"  {bad_line_text}", language="python")
                            # Common gotcha hint
                            if 'passdef' in bad_line_text or 'passimport' in bad_line_text or 'passreturn' in bad_line_text:
                                st.info(
                                    "💡 Hint: It looks like the starter `pass` and your new code got merged onto the same line. "
                                    "Add a newline between them, or delete `pass` entirely before writing your function body."
                                )
                else:
                    # Show each test result
                    for result in test_results['results']:
                        if result['passed']:
                            st.success(f"✅ Test {result['test_number']}: Passed")
                        else:
                            st.error(f"❌ Test {result['test_number']}: Failed")
                            st.code(f"Input: {result['input']}\nExpected: {result['expected']}\nGot: {result['actual']}")
                            if result.get('error'):
                                st.caption(f"Error: {result['error']}")
                
                # Get AI feedback
                with st.spinner("🤖 Watsonx is reviewing your code like a senior dev..."):
                    feedback_prompt = build_code_feedback_prompt(
                        challenge_prompt=challenge['prompt'],
                        student_code=code,
                        test_results=test_results
                    )
                    
                    feedback_response = generate(
                        prompt=feedback_prompt,
                        system="You are a supportive coding tutor providing constructive feedback.",
                        max_tokens=400,
                        temperature=0.4
                    )
                    
                    feedback = parse_json_response(feedback_response)
                    
                    if not feedback:
                        feedback = {
                            "score": 50 if passed > 0 else 0,
                            "verdict": "passed" if passed == total else "failed",
                            "summary": "Code executed.",
                            "strengths": ["Attempted the challenge"],
                            "improvements": ["Review the lesson"]
                        }
                    
                    st.session_state[f'code_feedback_{current_topic_id}'] = feedback
                
                # Display feedback
                st.markdown("---")
                st.markdown("### 🤖 AI Feedback")
                
                score = feedback.get('score', 0)
                verdict = feedback.get('verdict', 'failed')
                
                if verdict == 'passed':
                    st.success(f"✅ **Score: {score}/100** — {feedback.get('summary', '')}")
                elif verdict == 'passed_with_notes':
                    st.info(f"✔️ **Score: {score}/100** — {feedback.get('summary', '')}")
                else:
                    st.warning(f"📝 **Score: {score}/100** — {feedback.get('summary', '')}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**💪 Strengths:**")
                    for strength in feedback.get('strengths', []):
                        st.markdown(f"- {strength}")
                
                with col2:
                    st.markdown("**🎯 Improvements:**")
                    for improvement in feedback.get('improvements', []):
                        st.markdown(f"- {improvement}")

                # ---------- Fail handling: offer regenerate when challenge didn't pass ----------
                if passed != total:
                    regen_count = st.session_state.get(f'regen_count_{current_topic_id}', 0)
                    st.markdown("---")
                    if regen_count < MAX_REGENERATIONS:
                        st.info(
                            "🤔 **The challenge didn't pass yet.** Watsonx can regenerate the lesson "
                            "with a shallower depth and a gentler challenge — then come back here and try again."
                        )
                        cregen1, cregen2 = st.columns(2)
                        with cregen1:
                            if st.button("🔄 Regenerate the topic for me",
                                         type="primary",
                                         key=f"regen_after_code_{current_topic_id}",
                                         use_container_width=True):
                                _request_topic_regeneration("code_fail")
                        with cregen2:
                            if st.button("👉 Let me try again as-is",
                                         key=f"retry_code_{current_topic_id}",
                                         use_container_width=True):
                                pass  # nothing happens; user just edits the editor and resubmits
                    else:
                        st.info(
                            "💡 You've already regenerated this topic. Use the chat on the **Lesson** tab "
                            "to ask Watsonx specific questions about your code, then try again here."
                        )

                # Record performance if passed
                if passed == total:
                    elapsed_time = int(time.time() - st.session_state[f'start_time_{current_topic_id}'])
                    
                    performance_record = {
                        "topic_id": current_topic_id,
                        "quiz_score": st.session_state[f'quiz_score_{current_topic_id}'],
                        "quiz_total": len(quiz),
                        "code_score": score,
                        "code_passed": True,
                        "time_seconds": elapsed_time,
                        "regenerations_used": 0
                    }
                    
                    record_performance(performance_record)
                    
                    # Compute adaptation for next topic if not last
                    if current_topic_id < 5:
                        next_topic_id = current_topic_id + 1
                        next_topic = topics[next_topic_id - 1]
                        
                        with st.spinner("Watsonx noticed how you learn — adjusting the next topic..."):
                            directive = compute_next_directive(
                                last_perf=performance_record,
                                prior_directives=st.session_state.adaptation_history,
                                next_topic_title=next_topic['title'],
                                full_performance_history=st.session_state.performance,
                            )
                            
                            from core.state import store_adaptation_directive
                            store_adaptation_directive(next_topic_id, directive)
                    
                    st.markdown("---")
                    st.success(f"🎉 Topic {current_topic_id} completed!")
                    
                    if current_topic_id < 5:
                        st.balloons()
                        st.info(f"✨ Topic {current_topic_id + 1} is now unlocked!")
                        
                        if st.button("📚 Back to Curriculum", type="primary", use_container_width=True):
                            st.switch_page("pages/2_📚_Curriculum.py")
                    else:
                        st.balloons()
                        st.success("🏆 Congratulations! You've completed all topics!")
                        
                        if st.button("🏠 Back to Home", type="primary", use_container_width=True):
                            st.switch_page("app.py")

# Capstone unlock trigger
if st.session_state.completed_topics:
    st.markdown("---")
    st.markdown("### 🏆 Capstone Project Available")
    st.caption("Watsonx generated a personalized project that combines what you've learned")
    if st.button("🚀 Preview Your Capstone Project", type="primary", use_container_width=True):
        st.switch_page("pages/4_🏆_Capstone.py")

# Navigation footer
st.markdown("---")
if st.button("← Back to Curriculum"):
    st.switch_page("pages/2_📚_Curriculum.py")

# Footer
st.caption("Content powered by IBM watsonx.ai • Code execution in safe sandbox")

# Made with Bob
