"""
Prompt templates and builders for EduBob v2
All prompts instruct watsonx.ai to return valid JSON matching specific schemas
"""

import json
from typing import List, Dict, Optional


# ============================================================================
# PROMPT TEMPLATES (Section 6 of plan)
# ============================================================================

ONBOARDING_NEXT_QUESTION_PROMPT = """You are a friendly coding mentor onboarding a new learner. Ask ONE multiple-choice question to understand their interests, motivation, or skill level. After 3 questions total, set `is_final: true` and stop. Vary your questions based on prior answers — if they said 'beginner', don't re-ask skill level.

Prior Q&A history:
{qa_history}

Respond with ONLY valid JSON matching this schema:
{{
  "question": "Your question here",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "is_final": false
}}

No prose, no markdown fences. Just the JSON."""


INTEREST_PROFILE_PROMPT = """Summarize this learner's profile from their answers. Pick 1-2 interest tags from: web, automation, data, ai, games, scripting, general.

Q&A history:
{qa_history}

Respond with ONLY valid JSON matching this schema:
{{
  "interests": ["tag1", "tag2"],
  "motivation": "brief summary of why they want to learn",
  "skill_level": "absolute beginner | beginner | intermediate",
  "preferred_style": "hands-on examples | theory-first | project-based"
}}

No prose, no markdown fences. Just the JSON."""


CURRICULUM_PROMPT = """Design a 5-topic Python curriculum SPECIFICALLY for this learner. The curriculum MUST be visibly different for different interests — do NOT default to generic "variables, loops, functions, lists, dicts."

PERSONALIZATION RULES (mandatory):
- If interests include "web": topics should reference URLs, HTML strings, JSON parsing, web data manipulation, simple HTTP-style examples
- If interests include "automation": topics should reference file processing, scheduling concepts, batch operations, command-line style scripts
- If interests include "data": topics should reference CSV-style records, statistics on lists, dictionaries as records, data cleaning
- If interests include "ai" or "ml": topics should reference number lists, math operations, simple algorithms, decision logic
- If interests include "games": topics should reference state, randomness, scoring, simple game loops
- If skill_level is "absolute beginner": Topic 1 must be the gentlest possible intro; avoid jargon
- If skill_level is "intermediate": Topic 1 can skip basics and start with something useful

EXAMPLES of well-personalized topic 1 titles (match your style to the learner):
- For web beginner: "Python Strings — Building Blocks of the Web"
- For automation beginner: "Variables — Storing What Your Scripts Remember"
- For data beginner: "Numbers and Lists — The Foundation of Datasets"
- For ai beginner: "Variables and Math — How Models Store Knowledge"
- For games beginner: "Variables — Tracking Score, Lives, and Time"

ALL topics must use only standard Python (no external libraries). Each topic must be teachable in 15 minutes and have a code-challenge component.

Learner profile:
{profile}

Now design a curriculum that a peer educator would IMMEDIATELY recognize as tailored to this exact learner. Topic titles, summaries, and the example domain must visibly reflect the profile.

Respond with ONLY valid JSON matching this schema:
{{
  "track_title": "Python for [personalized descriptor referencing their actual interest]",
  "topics": [
    {{
      "id": 1,
      "title": "Topic title that references their interest domain",
      "summary": "1-2 sentence description that names their interest in the explanation",
      "estimated_minutes": 15
    }}
  ]
}}

The topics array MUST contain exactly 5 entries (id 1 through 5). No prose, no markdown fences. Just the JSON."""


TOPIC_CONTENT_PROMPT = """Generate complete topic content. Lesson must be 200-400 words of friendly markdown. Quiz: 3 multiple-choice questions, each with 4 options. Code challenge: a function-writing task with 2 test cases. Test cases must be deterministic and runnable via `exec()` in a restricted namespace (no imports, no I/O).

Topic specification:
{topic_spec}

Learner profile:
{profile}

{adaptation_instruction}

Respond with ONLY valid JSON matching this schema:
{{
  "lesson_markdown": "## Topic Title\\n\\nLesson content here...",
  "quiz": [
    {{
      "question": "Question text?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_index": 2
    }}
    // ... 2 more questions (total 3)
  ],
  "challenge": {{
    "prompt": "Write a function `func_name(param)` that does X",
    "starter_code": "def func_name(param):\\n    pass",
    "test_cases": [
      {{"input": "'test_value'", "expected": "expected_output"}},
      {{"input": "'another_value'", "expected": "another_output"}}
    ]
  }}
}}

No prose, no markdown fences. Just the JSON."""


CODE_FEEDBACK_PROMPT = """Review the student's Python code as a supportive tutor. Score 0-100. Verdict: 'passed', 'passed_with_notes', or 'failed'. Be specific about strengths and improvements. Keep summary under 30 words.

Challenge prompt:
{challenge_prompt}

Student's code:
{student_code}

Test results:
{test_results}

Respond with ONLY valid JSON matching this schema:
{{
  "score": 85,
  "verdict": "passed_with_notes",
  "summary": "Brief summary under 30 words",
  "strengths": ["Strength 1", "Strength 2"],
  "improvements": ["Improvement 1", "Improvement 2"]
}}

No prose, no markdown fences. Just the JSON."""


ADAPTATION_PROMPT = """Analyze this learner's last topic performance and prescribe how to teach the NEXT topic. If they scored low or took long, go shallower. If they aced it, go deeper. Match `examples_flavor` to their established interests.

Last topic performance:
{performance_record}

Prior adaptation directives:
{prior_directives}

Next topic title:
{next_topic_title}

Respond with ONLY valid JSON matching this schema:
{{
  "depth": "shallower" | "standard" | "deeper",
  "examples_flavor": "web" | "automation" | "data" | "ai" | "games" | "scripting" | "general",
  "extra_emphasis": "specific concept to emphasize",
  "tone": "more_encouraging" | "standard" | "more_challenging"
}}

No prose, no markdown fences. Just the JSON."""


# ============================================================================
# HELPER FUNCTIONS (Section 7.2 of plan)
# ============================================================================

def build_onboarding_next_question_prompt(qa_history: List[Dict[str, str]]) -> str:
    """
    Build prompt for generating next onboarding question.
    
    Args:
        qa_history: List of {"question": "...", "answer": "..."} dicts
    
    Returns:
        Formatted prompt string
    """
    if not qa_history:
        history_str = "No prior questions yet. This is the first question."
    else:
        history_str = "\n".join([
            f"Q{i+1}: {qa['question']}\nA{i+1}: {qa['answer']}"
            for i, qa in enumerate(qa_history)
        ])
    
    return ONBOARDING_NEXT_QUESTION_PROMPT.format(qa_history=history_str)


def build_interest_profile_prompt(qa_history: List[Dict[str, str]]) -> str:
    """
    Build prompt for generating interest profile from Q&A history.
    
    Args:
        qa_history: List of {"question": "...", "answer": "..."} dicts
    
    Returns:
        Formatted prompt string
    """
    history_str = "\n".join([
        f"Q{i+1}: {qa['question']}\nA{i+1}: {qa['answer']}"
        for i, qa in enumerate(qa_history)
    ])
    
    return INTEREST_PROFILE_PROMPT.format(qa_history=history_str)


def build_curriculum_prompt(profile: Dict) -> str:
    """
    Build prompt for generating personalized curriculum.
    
    Args:
        profile: Interest profile dict (schema 5.1)
    
    Returns:
        Formatted prompt string
    """
    profile_str = json.dumps(profile, indent=2)
    return CURRICULUM_PROMPT.format(profile=profile_str)


CAPSTONE_PROMPT = """Design a personalized capstone project for this learner that combines ALL the topics they've learned. The project must use only standard Python, be achievable for their skill level, and align with their stated interests.

Learner profile:
{profile}

Completed topics:
{topics}

Respond with ONLY valid JSON matching this schema:
{{
  "project_title": "Catchy name based on their interests",
  "elevator_pitch": "One sentence: what they'll build and why it matters to them",
  "skills_used": ["topic 1 concept", "topic 2 concept", ...],
  "build_steps": ["Step 1: ...", "Step 2: ...", "Step 3: ...", "Step 4: ..."],
  "estimated_hours": 2
}}

No prose, no markdown fences. Just the JSON."""


def build_capstone_prompt(profile: dict, topics: list) -> str:
    """
    Build prompt for generating personalized capstone project.

    Args:
        profile: Interest profile dict
        topics: List of completed topic dicts with title and summary

    Returns:
        Formatted prompt string
    """
    profile_str = json.dumps(profile, indent=2)
    topics_str = "\n".join([f"- {t['title']}: {t.get('summary', 'Core concepts')}" for t in topics])
    return CAPSTONE_PROMPT.format(profile=profile_str, topics=topics_str)


def build_topic_content_prompt(
    topic_spec: Dict,
    profile: Dict,
    adaptation_directive: Optional[Dict] = None
) -> str:
    """
    Build prompt for generating topic content (lesson + quiz + challenge).
    
    Args:
        topic_spec: Topic dict from curriculum (schema 5.2)
        profile: Interest profile dict (schema 5.1)
        adaptation_directive: Optional adaptation directive (schema 5.6)
    
    Returns:
        Formatted prompt string
    """
    topic_str = json.dumps(topic_spec, indent=2)
    profile_str = json.dumps(profile, indent=2)
    
    # Add adaptation instruction if provided
    if adaptation_directive:
        adaptation_str = f"""
Adaptation directive (adjust content accordingly):
{json.dumps(adaptation_directive, indent=2)}

Adjust depth to `{adaptation_directive.get('depth', 'standard')}`, lean examples toward `{adaptation_directive.get('examples_flavor', 'general')}`, and emphasize `{adaptation_directive.get('extra_emphasis', 'core concepts')}`. Tone: `{adaptation_directive.get('tone', 'standard')}`."""
    else:
        adaptation_str = "No adaptation directive. Use standard depth and tone."
    
    return TOPIC_CONTENT_PROMPT.format(
        topic_spec=topic_str,
        profile=profile_str,
        adaptation_instruction=adaptation_str
    )


def build_code_feedback_prompt(
    challenge_prompt: str,
    student_code: str,
    test_results: Dict
) -> str:
    """
    Build prompt for generating AI code feedback.
    
    Args:
        challenge_prompt: The original challenge description
        student_code: The student's submitted code
        test_results: Dict with test execution results
    
    Returns:
        Formatted prompt string
    """
    test_results_str = json.dumps(test_results, indent=2)
    
    return CODE_FEEDBACK_PROMPT.format(
        challenge_prompt=challenge_prompt,
        student_code=student_code,
        test_results=test_results_str
    )


def build_adaptation_prompt(
    performance_record: Dict,
    prior_directives: List[Dict],
    next_topic_title: str
) -> str:
    """
    Build prompt for generating adaptation directive.
    
    Args:
        performance_record: Last topic's performance (schema 5.5)
        prior_directives: List of previous adaptation directives
        next_topic_title: Title of the upcoming topic
    
    Returns:
        Formatted prompt string
    """
    perf_str = json.dumps(performance_record, indent=2)
    
    if prior_directives:
        directives_str = json.dumps(prior_directives, indent=2)
    else:
        directives_str = "No prior directives. This is the first adaptation."
    
    return ADAPTATION_PROMPT.format(
        performance_record=perf_str,
        prior_directives=directives_str,
        next_topic_title=next_topic_title
    )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def parse_json_response(response: str) -> Optional[Dict]:
    """
    Parse JSON from watsonx.ai response, handling common issues.
    
    Args:
        response: Raw text response from model
    
    Returns:
        Parsed dict or None if parsing fails
    """
    try:
        # Try direct parse
        return json.loads(response)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown fences
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end > start:
                try:
                    return json.loads(response[start:end].strip())
                except json.JSONDecodeError:
                    pass
        
        # Try to find JSON object in text
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(response[start:end])
            except json.JSONDecodeError:
                pass
        
        return None


if __name__ == "__main__":
    # Test prompt builders
    print("Testing prompt builders...\n")
    
    # Test onboarding
    qa = [{"question": "What's your skill level?", "answer": "Beginner"}]
    prompt = build_onboarding_next_question_prompt(qa)
    print("Onboarding prompt length:", len(prompt))
    
    # Test profile
    profile = {
        "interests": ["web", "automation"],
        "motivation": "build tools",
        "skill_level": "beginner",
        "preferred_style": "hands-on"
    }
    prompt = build_curriculum_prompt(profile)
    print("Curriculum prompt length:", len(prompt))
    
    print("\n✓ All prompt builders working")

# Made with Bob
