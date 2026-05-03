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
    parse_json_response
)
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
        # Get adaptation directive if exists
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

# Three tabs
tab1, tab2, tab3 = st.tabs(["📚 Lesson", "❓ Quiz", "💻 Challenge"])

# ============================================================================
# TAB 1: LESSON
# ============================================================================
with tab1:
    # Stream lesson on first reveal for visual effect
    if not st.session_state.get(f'lesson_revealed_{current_topic_id}', False):
        lesson_text = topic_content['lesson_markdown']
        st.write_stream((char for char in lesson_text))
        st.session_state[f'lesson_revealed_{current_topic_id}'] = True
    else:
        st.markdown(topic_content['lesson_markdown'])
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Take Quiz →", type="primary", use_container_width=True):
            st.session_state.active_tab = "quiz"
            st.info("Switch to the Quiz tab above ☝️")

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
            st.warning(f"📝 You got {score}/{total} correct. Review the lesson and try the challenge!")
        
        # Show correct answers
        with st.expander("📋 Review Answers"):
            for i, question in enumerate(quiz):
                correct_index = question['correct_index']
                correct_answer = question['options'][correct_index]
                st.markdown(f"**Q{i+1}:** {question['question']}")
                st.markdown(f"✅ **Correct answer:** {correct_answer}")
                st.markdown("")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Continue to Challenge →", type="primary", use_container_width=True):
                st.info("Switch to the Challenge tab above ☝️")

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
                                next_topic_title=next_topic['title']
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
