"""
Session State Management for EduBob v2
Handles Streamlit session_state initialization and helpers
"""

import streamlit as st
from typing import Dict, Any, Optional, List


def init_session():
    """
    Initialize session state with default values.
    Idempotent - safe to call multiple times.
    """
    # Interest profile from onboarding
    if 'profile' not in st.session_state:
        st.session_state.profile = None
    
    # Generated curriculum (5 topics)
    if 'curriculum' not in st.session_state:
        st.session_state.curriculum = None
    
    # Topic contents cache: {topic_id: {lesson_markdown, quiz, challenge}}
    if 'topic_contents' not in st.session_state:
        st.session_state.topic_contents = {}
    
    # Current topic being worked on
    if 'current_topic_id' not in st.session_state:
        st.session_state.current_topic_id = 1
    
    # Performance records for completed topics
    if 'performance' not in st.session_state:
        st.session_state.performance = []
    
    # Adaptation directives history
    if 'adaptation_history' not in st.session_state:
        st.session_state.adaptation_history = []
    
    # Onboarding Q&A history
    if 'onboarding_qa' not in st.session_state:
        st.session_state.onboarding_qa = []
    
    # Track which topics are completed
    if 'completed_topics' not in st.session_state:
        st.session_state.completed_topics = set()
    
    # Current onboarding question
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    
    # Quiz answers for current topic
    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = {}
    
    # Code submission for current topic
    if 'code_submission' not in st.session_state:
        st.session_state.code_submission = None
    
    # AI activity log for transparency
    if 'ai_activity_log' not in st.session_state:
        st.session_state.ai_activity_log = []


def is_topic_unlocked(topic_id: int) -> bool:
    """
    Check if a topic is unlocked for the learner.
    Topic 1 is always unlocked.
    Other topics unlock when the previous topic is completed.
    
    Args:
        topic_id: The topic ID to check (1-5)
    
    Returns:
        True if topic is unlocked, False otherwise
    """
    # Topic 1 is always unlocked
    if topic_id == 1:
        return True
    
    # Other topics require previous topic to be completed
    previous_topic_id = topic_id - 1
    return previous_topic_id in st.session_state.completed_topics


def record_performance(record: Dict[str, Any]):
    """
    Record performance data for a completed topic.
    
    Args:
        record: Performance record dict with format:
            {
                "topic_id": int,
                "quiz_score": int,
                "quiz_total": int,
                "code_score": int,
                "code_passed": bool,
                "time_seconds": int,
                "regenerations_used": int
            }
    """
    st.session_state.performance.append(record)
    
    # Mark topic as completed if code passed
    if record.get("code_passed", False):
        st.session_state.completed_topics.add(record["topic_id"])


def get_last_performance() -> Optional[Dict[str, Any]]:
    """
    Get the most recent performance record.
    
    Returns:
        Last performance record dict or None if no records exist
    """
    if st.session_state.performance:
        return st.session_state.performance[-1]
    return None


def get_topic_performance(topic_id: int) -> Optional[Dict[str, Any]]:
    """
    Get performance record for a specific topic.
    
    Args:
        topic_id: The topic ID to get performance for
    
    Returns:
        Performance record dict or None if not found
    """
    for record in st.session_state.performance:
        if record.get("topic_id") == topic_id:
            return record
    return None


def is_topic_completed(topic_id: int) -> bool:
    """
    Check if a topic has been completed.
    
    Args:
        topic_id: The topic ID to check
    
    Returns:
        True if completed, False otherwise
    """
    return topic_id in st.session_state.completed_topics


def get_next_unlocked_topic() -> Optional[int]:
    """
    Get the ID of the next unlocked but incomplete topic.
    
    Returns:
        Topic ID (1-5) or None if all topics completed
    """
    if not st.session_state.curriculum:
        return None
    
    for topic in st.session_state.curriculum.get("topics", []):
        topic_id = topic["id"]
        if is_topic_unlocked(topic_id) and not is_topic_completed(topic_id):
            return topic_id
    
    return None


def reset_session():
    """
    Clear all session state (for "Start Over" functionality).
    """
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session()


def get_progress_summary() -> Dict[str, Any]:
    """
    Get a summary of the learner's progress.
    
    Returns:
        Dict with progress statistics
    """
    total_topics = 5
    completed = len(st.session_state.completed_topics)
    
    return {
        "total_topics": total_topics,
        "completed_topics": completed,
        "completion_percentage": (completed / total_topics) * 100,
        "current_topic": st.session_state.current_topic_id,
        "has_profile": st.session_state.profile is not None,
        "has_curriculum": st.session_state.curriculum is not None,
    }


def store_adaptation_directive(topic_id: int, directive: Dict[str, Any]):
    """
    Store an adaptation directive for a topic.
    
    Args:
        topic_id: The topic ID this directive is for
        directive: The adaptation directive dict
    """
    st.session_state.adaptation_history.append({
        "topic_id": topic_id,
        "directive": directive
    })


def get_adaptation_directive(topic_id: int) -> Optional[Dict[str, Any]]:
    """
    Get the adaptation directive for a specific topic.
    
    Args:
        topic_id: The topic ID to get directive for
    
    Returns:
        Adaptation directive dict or None if not found
    """
    for entry in st.session_state.adaptation_history:
        if entry["topic_id"] == topic_id:
            return entry["directive"]
    return None


if __name__ == "__main__":
    print("state.py - Session state management module")
    print("This module is designed to be used with Streamlit")
    print("Run with: streamlit run app.py")

# Made with Bob


def log_ai_activity(action: str, tokens: int = 0):
    """
    Record an AI call for the sidebar transparency panel.
    
    Args:
        action: Description of the AI action (e.g., "Generated onboarding question")
        tokens: Number of tokens used (approximate)
    """
    from datetime import datetime
    
    if 'ai_activity_log' in st.session_state:
        st.session_state.ai_activity_log.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "action": action,
            "tokens": tokens
        })
