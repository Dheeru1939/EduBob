"""
Regression test for prompt builders.

Catches the unescaped-curly-brace bug where prompt templates contain
literal { or } without escaping them as {{ or }}, which causes
str.format() to raise KeyError.

Each builder is invoked with realistic inputs and any unescaped brace
will surface as an exception.

Usage:
    python test_prompts.py

Cost: zero (no LLM calls).
"""

from core.prompts import (
    build_onboarding_next_question_prompt,
    build_interest_profile_prompt,
    build_curriculum_prompt,
    build_topic_content_prompt,
    build_code_feedback_prompt,
    build_adaptation_prompt,
    build_capstone_prompt,
    build_topic_chat_prompt,
    build_lesson_mode_prompt,
    build_video_queries_prompt,
)


SAMPLE_QA = [{"question": "Test?", "answer": "Yes"}]
SAMPLE_PROFILE = {
    "age_band": "25_34",
    "life_context": "student",
    "current_field": "test",
    "interests": ["data"],
    "motivation": "test",
    "skill_level": "beginner",
    "preferred_style": "hands-on",
}
SAMPLE_TOPIC = {"id": 1, "title": "Test", "summary": "Test"}


CHECKS = [
    ("onboarding question", lambda: build_onboarding_next_question_prompt(SAMPLE_QA)),
    ("interest profile", lambda: build_interest_profile_prompt(SAMPLE_QA)),
    ("curriculum", lambda: build_curriculum_prompt(SAMPLE_PROFILE)),
    ("topic content (no adaptation)", lambda: build_topic_content_prompt(SAMPLE_TOPIC, SAMPLE_PROFILE, None)),
    ("topic content (with adaptation)", lambda: build_topic_content_prompt(
        SAMPLE_TOPIC, SAMPLE_PROFILE, {"depth": "shallower", "examples_flavor": "data", "extra_emphasis": "x", "tone": "more_encouraging"}
    )),
    ("code feedback", lambda: build_code_feedback_prompt("prompt", "def x(): pass", {"passed": 0})),
    ("adaptation directive", lambda: build_adaptation_prompt({"topic_id": 1}, [], "Next", None)),
    ("capstone", lambda: build_capstone_prompt(SAMPLE_PROFILE, [SAMPLE_TOPIC])),
    ("topic chat", lambda: build_topic_chat_prompt("Test", "Lesson", SAMPLE_PROFILE, [], "How?")),
    ("lesson mode (analogy)", lambda: build_lesson_mode_prompt("Test", "Lesson", SAMPLE_PROFILE, "analogy")),
    ("video queries", lambda: build_video_queries_prompt("Test", "summary", SAMPLE_PROFILE)),
]


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Prompt builder regression test (catches unescaped braces)")
    print("=" * 60)

    failures = []
    for name, fn in CHECKS:
        try:
            result = fn()
            assert isinstance(result, str) and len(result) > 0
            print(f"  PASS  {name}")
        except Exception as e:
            failures.append((name, e))
            print(f"  FAIL  {name}")
            print(f"        {type(e).__name__}: {e}")

    print("=" * 60)
    if failures:
        print(f"FAIL: {len(failures)} builder(s) raised on a clean format call.")
        print("Common cause: a literal { or } in the template that needs to be escaped as {{ or }}.")
        raise SystemExit(1)
    else:
        print(f"ALL {len(CHECKS)} CHECKS PASSED")
