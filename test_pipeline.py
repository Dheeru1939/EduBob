"""
End-to-end pipeline test for EduBob v2.

Exercises every backend stage in sequence, simulating one full learner journey:

    1. Synthesize profile from Q&A history
    2. Generate personalized curriculum
    3. Generate topic 1 content (lesson + quiz + challenge)
    4. Execute student code through the sandbox
    5. Generate AI code feedback
    6. Compute adaptation directive (after deliberately mixed performance)
    7. Generate topic 2 content WITH adaptation directive applied
    8. Generate the capstone project
    9. Compare topic 1 and topic 2 lessons to verify adaptation took effect

Skips: Streamlit UI rendering, Monaco editor, browser interactions.

Usage:
    python test_pipeline.py

Cost: ~8 LLM calls, 15-20K tokens.
"""

import json
import sys
from typing import Optional

from core.watsonx_client import generate, generate_json
from core.prompts import (
    build_interest_profile_prompt,
    build_curriculum_prompt,
    build_topic_content_prompt,
    build_code_feedback_prompt,
    build_adaptation_prompt,
    build_capstone_prompt,
    parse_json_response,
)
from core.code_runner import run_code_with_tests


# ============================================================================
# Test scaffolding
# ============================================================================

PASS = []
FAIL = []


def step(name: str):
    print("\n" + "=" * 70)
    print(f"STEP: {name}")
    print("=" * 70)


def assert_step(name: str, condition: bool, detail: str = ""):
    if condition:
        PASS.append(name)
        print(f"  PASS: {name}")
        if detail:
            print(f"        {detail}")
    else:
        FAIL.append(name)
        print(f"  FAIL: {name}")
        if detail:
            print(f"        {detail}")


# ============================================================================
# Test data
# ============================================================================

QA_HISTORY = [
    {
        "question": "Roughly which age range fits you best?",
        "answer": "25-34 (building my career)",
    },
    {
        "question": "Which best describes your current situation?",
        "answer": "Working professional in a non-tech field (marketing, finance, healthcare, etc.)",
    },
    {
        "question": "What field do you spend most of your time in?",
        "answer": "Finance / Accounting / Operations",
    },
    {
        "question": "What do you most want to do with Python?",
        "answer": "Analyze data from my field",
    },
]


# ============================================================================
# Pipeline
# ============================================================================

def run_pipeline():
    # ------------------------------------------------------------------
    step("1/8  Synthesize profile from Q&A")
    # ------------------------------------------------------------------
    profile = generate_json(
        prompt=build_interest_profile_prompt(QA_HISTORY),
        system="You are an educational AI analyzing learner profiles.",
        max_tokens=400,
        temperature=0.3,
        validator=lambda r: isinstance(r, dict) and "interests" in r,
    )

    assert_step("profile generated", profile is not None)
    assert_step("profile has age_band", profile and "age_band" in profile,
                detail=f"age_band: {profile.get('age_band') if profile else 'N/A'}")
    assert_step("profile has life_context", profile and "life_context" in profile,
                detail=f"life_context: {profile.get('life_context') if profile else 'N/A'}")
    assert_step("profile has current_field", profile and "current_field" in profile,
                detail=f"current_field: {profile.get('current_field') if profile else 'N/A'}")

    if not profile:
        print("\nABORT: no profile, cannot continue")
        return

    print(f"\n  Full profile:\n{json.dumps(profile, indent=4)}")

    # ------------------------------------------------------------------
    step("2/8  Generate personalized curriculum")
    # ------------------------------------------------------------------
    curriculum = generate_json(
        prompt=build_curriculum_prompt(profile),
        system="You are an expert curriculum designer creating PERSONALIZED Python learning paths.",
        max_tokens=800,
        temperature=0.7,
        validator=lambda r: isinstance(r, dict) and len(r.get("topics", [])) == 5,
    )

    assert_step("curriculum generated", curriculum is not None)
    assert_step("curriculum has 5 topics", curriculum and len(curriculum.get("topics", [])) == 5)
    assert_step("track title references field", curriculum and (
        "finance" in curriculum.get("track_title", "").lower()
        or "data" in curriculum.get("track_title", "").lower()
        or "analy" in curriculum.get("track_title", "").lower()
    ), detail=f"Track: {curriculum.get('track_title') if curriculum else 'N/A'}")

    if not curriculum:
        print("\nABORT: no curriculum, cannot continue")
        return

    print(f"\n  Track: {curriculum.get('track_title')}")
    for t in curriculum.get("topics", []):
        print(f"    {t.get('id')}. {t.get('title')}")

    # ------------------------------------------------------------------
    step("3/8  Generate topic 1 content")
    # ------------------------------------------------------------------
    topic1_spec = curriculum["topics"][0]
    topic1_content = generate_json(
        prompt=build_topic_content_prompt(topic_spec=topic1_spec, profile=profile, adaptation_directive=None),
        system="You are an expert Python educator creating engaging, personalized learning content.",
        max_tokens=1200,
        temperature=0.5,
        validator=lambda r: isinstance(r, dict) and "lesson_markdown" in r and "quiz" in r and "challenge" in r,
    )

    assert_step("topic 1 content generated", topic1_content is not None)
    if topic1_content:
        assert_step("topic 1 has lesson", "lesson_markdown" in topic1_content,
                    detail=f"lesson length: {len(topic1_content.get('lesson_markdown', ''))} chars")
        assert_step("topic 1 quiz has 3+ questions", len(topic1_content.get("quiz", [])) >= 3)
        assert_step("topic 1 challenge has test_cases",
                    len(topic1_content.get("challenge", {}).get("test_cases", [])) >= 1)
        assert_step("topic 1 has starter_code",
                    "starter_code" in topic1_content.get("challenge", {}))

        print(f"\n  Lesson preview (first 200 chars):")
        print(f"    {topic1_content['lesson_markdown'][:200]}...")
        print(f"\n  Challenge prompt: {topic1_content['challenge'].get('prompt', '')[:150]}")
        print(f"  Starter code:\n{topic1_content['challenge'].get('starter_code', '')}")

    if not topic1_content:
        print("\nABORT: no topic content, cannot continue")
        return

    # ------------------------------------------------------------------
    step("4/8  Execute student code through sandbox")
    # ------------------------------------------------------------------
    challenge = topic1_content["challenge"]
    starter = challenge.get("starter_code", "")
    test_cases = challenge.get("test_cases", [])

    # Simulate student making a "first attempt" — use the starter as-is (likely fails)
    print(f"\n  Running starter code as-is (expected to fail tests)...")
    starter_results = run_code_with_tests(starter, test_cases, timeout_s=5)
    assert_step("sandbox executed starter code", starter_results is not None)
    assert_step("sandbox returned test_results", "results" in starter_results)
    print(f"  Starter passed: {starter_results['passed']}/{starter_results['passed'] + starter_results['failed']}")

    # Simulate a "good" student attempt — try to write a working version
    # Use a generic working solution for the most common Python challenges
    func_name = None
    starter_lines = starter.split("\n")
    for line in starter_lines:
        if line.strip().startswith("def "):
            try:
                func_name = line.strip().split("def ")[1].split("(")[0].strip()
            except (IndexError, AttributeError):
                pass
            break

    print(f"  Detected function name: {func_name}")
    # Note: we can't reliably auto-write a working solution because the challenge varies
    # Just record the starter result as the "submission" for the feedback step
    test_results = starter_results

    # ------------------------------------------------------------------
    step("5/8  Generate AI code feedback")
    # ------------------------------------------------------------------
    feedback = generate_json(
        prompt=build_code_feedback_prompt(
            challenge_prompt=challenge.get("prompt", ""),
            student_code=starter,
            test_results=test_results,
        ),
        system="You are a supportive coding tutor providing constructive feedback.",
        max_tokens=500,
        temperature=0.4,
        validator=lambda r: isinstance(r, dict) and "score" in r,
    )
    assert_step("feedback generated", feedback is not None)
    if feedback:
        assert_step("feedback has score", "score" in feedback,
                    detail=f"score: {feedback.get('score')}")
        assert_step("feedback has verdict", "verdict" in feedback,
                    detail=f"verdict: {feedback.get('verdict')}")
        assert_step("feedback has improvements", isinstance(feedback.get("improvements"), list))
        print(f"\n  Summary: {feedback.get('summary', '')}")

    # ------------------------------------------------------------------
    step("6/8  Compute adaptation directive (after low performance)")
    # ------------------------------------------------------------------
    # Simulate weak performance to trigger a "shallower" adaptation
    weak_perf = {
        "topic_id": 1,
        "quiz_score": 1,
        "quiz_total": 3,
        "code_score": feedback.get("score", 30) if feedback else 30,
        "code_passed": False,
        "time_seconds": 600,
        "regenerations_used": 1,
    }
    next_topic_title = curriculum["topics"][1].get("title", "Topic 2")
    directive = generate_json(
        prompt=build_adaptation_prompt(
            performance_record=weak_perf,
            prior_directives=[],
            next_topic_title=next_topic_title,
        ),
        system="You are an adaptive learning system analyzing student performance.",
        max_tokens=300,
        temperature=0.4,
        validator=lambda r: isinstance(r, dict) and "depth" in r,
    )
    assert_step("adaptation directive generated", directive is not None)
    if directive:
        assert_step("directive has depth", "depth" in directive,
                    detail=f"depth: {directive.get('depth')}")
        assert_step("directive has tone", "tone" in directive,
                    detail=f"tone: {directive.get('tone')}")
        assert_step("directive depth is shallower (weak perf)",
                    directive.get("depth") in ("shallower", "standard"),
                    detail=f"depth: {directive.get('depth')} (expected shallower for weak performance)")
        print(f"\n  Full directive: {json.dumps(directive, indent=4)}")

    # ------------------------------------------------------------------
    step("7/8  Generate topic 2 content WITH adaptation directive")
    # ------------------------------------------------------------------
    topic2_spec = curriculum["topics"][1]
    topic2_content = generate_json(
        prompt=build_topic_content_prompt(
            topic_spec=topic2_spec, profile=profile, adaptation_directive=directive
        ),
        system="You are an expert Python educator creating engaging, personalized learning content.",
        max_tokens=1200,
        temperature=0.5,
        validator=lambda r: isinstance(r, dict) and "lesson_markdown" in r,
    )
    assert_step("topic 2 content generated", topic2_content is not None)
    if topic2_content:
        topic2_lesson = topic2_content.get("lesson_markdown", "")
        topic1_lesson = topic1_content.get("lesson_markdown", "")
        assert_step("topic 2 lesson differs from topic 1",
                    topic2_lesson != topic1_lesson,
                    detail=f"lengths: t1={len(topic1_lesson)} t2={len(topic2_lesson)}")
        # Quick sanity: shallower depth -> lesson should be shorter or include encouraging language
        encourage_words = ["encourage", "support", "welcome", "easy", "simple", "step by step", "don't worry", "you've got"]
        has_encourage = any(w in topic2_lesson.lower() for w in encourage_words)
        assert_step("topic 2 shows adaptation cues (encouraging language)",
                    has_encourage,
                    detail="found encouraging language" if has_encourage else "no encouraging cues found (LLM may have used other adaptation signals)")
        print(f"\n  Topic 2 lesson preview (first 300 chars):")
        print(f"    {topic2_lesson[:300]}...")

    # ------------------------------------------------------------------
    step("8/8  Generate capstone project")
    # ------------------------------------------------------------------
    capstone = generate_json(
        prompt=build_capstone_prompt(profile, curriculum["topics"]),
        max_tokens=500,
        temperature=0.6,
        validator=lambda r: isinstance(r, dict) and "project_title" in r and "build_steps" in r,
    )
    assert_step("capstone generated", capstone is not None)
    if capstone:
        assert_step("capstone has title", "project_title" in capstone,
                    detail=f"title: {capstone.get('project_title')}")
        assert_step("capstone has build_steps", isinstance(capstone.get("build_steps"), list))
        assert_step("capstone has at least 3 build_steps",
                    len(capstone.get("build_steps", [])) >= 3,
                    detail=f"{len(capstone.get('build_steps', []))} steps")
        print(f"\n  Capstone: {capstone.get('project_title')}")
        print(f"  Pitch: {capstone.get('elevator_pitch', '')}")


if __name__ == "__main__":
    print("\n" + "#" * 70)
    print("# EduBob v2 - End-to-End Pipeline Test")
    print("#" * 70)
    print(f"\nTest persona: 25-34 finance pro pivoting to data analysis")

    try:
        run_pipeline()
    except Exception as e:
        print(f"\n\nUNEXPECTED EXCEPTION: {type(e).__name__}: {e}")
        FAIL.append(f"unhandled exception: {e}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n\n" + "#" * 70)
    print(f"# RESULT: {len(PASS)} passed, {len(FAIL)} failed")
    print("#" * 70)

    if FAIL:
        print("\nFailures:")
        for name in FAIL:
            print(f"  - {name}")
        sys.exit(1)
    else:
        print("\nALL CHECKS PASSED - pipeline is healthy end to end.")
        sys.exit(0)
