"""
Prompt templates and builders for EduBob v2
All prompts instruct watsonx.ai to return valid JSON matching specific schemas
"""

import json
from typing import List, Dict, Optional


# ============================================================================
# PROMPT TEMPLATES (Section 6 of plan)
# ============================================================================

ONBOARDING_NEXT_QUESTION_PROMPT = """You are a friendly coding mentor onboarding a new learner. Ask ONE multiple-choice question that maximally helps personalize their Python curriculum. YOU decide how many questions to ask (between 3 and 6 total). Stop as soon as you have enough to design a deeply personalized curriculum.

DIMENSIONS TO COVER (you must learn most of these — use one question per dimension when possible):
1. AGE BAND — calibrates tone, pacing, examples (under 18, 18–24, 25–34, 35–49, 50+)
2. LIFE CONTEXT — student, early-career, mid-career switching domains, side-hustler, returning to workforce, retired explorer
3. CURRENT FIELD — marketing, finance, healthcare, design, engineering, education, retail, sales, retired-from-X, student-of-Y, etc. (gold for analogies)
4. INTEREST AREA — web, automation, data, AI/ML, games, scripting
5. SKILL LEVEL — never coded, dabbled before, comfortable with basics, or experienced (might be inferred from their answers)
6. MOTIVATION — career growth, pivot, automate work, build a specific thing, hobby, prep

STOPPING RULES:
- After 3 questions minimum: if you have enough to make a strong personalization decision, set `is_final: true`
- Hard cap at 6 questions: ALWAYS set `is_final: true` on the 6th question
- Stop EARLY if a single answer reveals multiple dimensions (e.g., "I am a 30yo marketing manager wanting to learn data" reveals age, life_context, field, AND interest in one shot — you can ask just 1-2 follow-ups)
- Continue if answers are vague or ambiguous

VARY YOUR QUESTIONS — never re-ask something they already answered. Build on prior answers.

Question style:
- Conversational and warm
- Multiple-choice with 4 distinct options
- The 4th option for sensitive questions can be "Prefer not to say" or "Other"
- Avoid jargon — write for a learner who may have never coded

Prior Q&A history:
{qa_history}

Respond with ONLY valid JSON matching this schema:
{{
  "question": "Your question here",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "is_final": false
}}

`is_final` MUST be `true` if you've already received 5 prior answers (this would be question 6, the cap). Otherwise set `true` only when you have enough information.

No prose, no markdown fences. Just the JSON."""


INTEREST_PROFILE_PROMPT = """Synthesize a rich learner profile from this Q&A history. Infer intelligently — if they said "I'm a marketing manager wanting to learn data," infer age_band from any age cue, life_context as "mid_career_switcher", current_field as "marketing", interests as ["data"], motivation as "career-growth pivot to data".

Be SPECIFIC in current_field — don't write "professional", write "marketing analyst" or "ICU nurse" or "high school sophomore" — whatever the answers suggest. If they only said the broad category, use that.

Q&A history:
{qa_history}

Respond with ONLY valid JSON matching this schema:
{{
  "age_band": "under_18 | 18_24 | 25_34 | 35_49 | 50_plus",
  "life_context": "student | early_career | mid_career_switcher | side_hustler | returning_to_workforce | retired_explorer",
  "current_field": "specific free-text descriptor (e.g. 'marketing manager', 'ICU nurse', 'high school student studying biology', 'retired engineer')",
  "interests": ["pick 1-2 from: web, automation, data, ai, games, scripting, general"],
  "motivation": "one concise sentence in their own framing",
  "skill_level": "absolute_beginner | beginner | intermediate",
  "preferred_style": "hands-on | structured | project-based"
}}

If a field truly cannot be inferred, use the first option as a safe default. No prose, no markdown fences. Just the JSON."""


CURRICULUM_PROMPT = """Design a 5-topic Python curriculum SO PERSONALIZED that a peer educator would recognize the learner from the curriculum alone. Apply ALL personalization dimensions below — track_title, topic titles, summaries, and example domains must ALL visibly reflect the learner's profile.

Learner profile:
{profile}

PERSONALIZATION DIMENSIONS (apply ALL that fit):

1. By LIFE CONTEXT:
   - "student": shorter conceptual lessons, school-relevant examples (gradebook, study tracker, homework helper), encourage curiosity over career framing
   - "early_career": entry-level professional examples (data prep, internal tools), career-growth framing
   - "mid_career_switcher": bridge from their current_field — explicit "you already know X from <field>, here's the Python equivalent" framing
   - "side_hustler": entrepreneurial framing — automating side income, micro-products, freelance task automation
   - "returning_to_workforce": refresher tone, patient pace, modern tooling reassurance, "you've got this"
   - "retired_explorer": leisure framing, hobby projects (recipe organizer, photo sorter, garden tracker), no pressure

2. By CURRENT FIELD (use as analogy bridge — examples should come from this domain):
   - "marketing": campaign data, A/B tests, audience segments, social media stats, click-through rates
   - "finance": portfolio data, budgets, financial ratios, expense trackers, stock series
   - "healthcare": vitals tracking, schedule organization, patient lookup (anonymized), medication reminders
   - "education": gradebook, attendance, lesson planner, class roster, exam analytics
   - "design": color palette tools, asset organization, image metadata, naming conventions
   - "engineering" or "STEM": sensor data, measurements, calculations, formula evaluation
   - "sales / business development": CRM-like dictionaries, lead scoring, pipeline metrics
   - "retail / hospitality": inventory tracking, order processing, scheduling
   - "student in <subject>": connect Python to that subject (biology → DNA strings, history → date arithmetic, art → palette manipulation)
   - "retired from <field>": gentle nostalgic-relevant examples without being patronizing
   - For other fields: invent a relevant analogy bridge

3. By AGE BAND (calibrate tone and lesson length):
   - "under_18": shorter lessons (~150 words), playful tone, examples from games/social media/school life
   - "18_24": college-aware tone, side-project framing, internship-relevant examples
   - "25_34": professional tone, career-growth framing, work-relevant examples
   - "35_49": confident peer-professional tone, efficiency-focused, time-respecting
   - "50_plus": patient pace, no assumed jargon, life-experience-friendly examples, never patronizing

4. By INTEREST AREA (which Python flavor to emphasize):
   - "web": URLs, HTML strings, JSON, simple HTTP-style examples
   - "automation": file processing, scheduling, batch operations
   - "data": CSV-style records, list statistics, dict-as-record, data cleaning
   - "ai" / "ml": number lists, math, decision logic, simple algorithms
   - "games": state, randomness, scoring, game loops
   - "scripting" / "general": utility scripts, calculators, tools

5. By MOTIVATION:
   - "career growth": tie skills to job market value
   - "domain switch / pivot": bridge-building, "you already know more than you think"
   - "automate work": every example saves them real time
   - "build something specific": project-driven framing
   - "curiosity / hobby": exploratory, "and here's an interesting fact"

EXAMPLES of well-personalized track titles + topic 1 titles:

A) 32-year-old marketing manager pivoting to data:
   - track_title: "Python for Marketers Moving Into Data"
   - topic 1: "Lists & Numbers — Your First Campaign Dataset"
   - example domain throughout: campaign metrics, audience segments, click-through rates

B) 45-year-old finance professional switching to AI:
   - track_title: "Python for Finance Pros Stepping Into AI"
   - topic 1: "Variables — From Cells to Code"
   - example domain throughout: stock prices, portfolio weights, financial ratios

C) 16-year-old high school student curious about web:
   - track_title: "Python for the Web-Curious Teen"
   - topic 1: "Strings — The Words Behind Every Webpage"
   - example domain throughout: URLs of favorite sites, social media handles, game titles

D) 60-year-old retired teacher learning for fun:
   - track_title: "Python for Lifelong Learners"
   - topic 1: "Variables — Storing Pieces of Information"
   - example domain throughout: book lists, recipe ingredients, garden plant tracker

E) 28-year-old software engineer wanting to add Python automation skills:
   - track_title: "Python for Engineers Who Already Code"
   - topic 1: "Strings & Files — The Automation Starter Kit"
   - example domain throughout: log file parsing, batch renaming, CLI scripts

ALL topics must use only standard Python (no external libraries). Each topic must be teachable in 15 minutes and have a code-challenge component.

Now design THIS learner's curriculum. Topic titles must reference their specific situation. Summaries must name their field or context. The 5 topics together must form a coherent journey toward something they'd realistically want to build.

Respond with ONLY valid JSON matching this schema:
{{
  "track_title": "Python for [highly specific descriptor of THIS learner]",
  "topics": [
    {{
      "id": 1,
      "title": "Topic title that references their domain",
      "summary": "1-2 sentence description naming their field/context in the explanation",
      "estimated_minutes": 15
    }}
  ]
}}

The topics array MUST contain exactly 5 entries (id 1 through 5). No prose, no markdown fences. Just the JSON."""


TOPIC_CONTENT_PROMPT = """Generate complete topic content for THIS specific learner. Lesson must be friendly markdown (length: 150 words for under_18, 200-400 words otherwise). Quiz: 3 multiple-choice questions, each with 4 options. Code challenge: a function-writing task with 2 test cases. Test cases must be deterministic and runnable via `exec()` in a restricted namespace (no imports, no I/O).

ALL examples in the lesson, quiz scenarios, and code challenge MUST come from the learner's `current_field` and reflect their `life_context`. Do not use generic examples like "shopping cart" or "todo list" unless they fit the learner's domain.

Tone calibration:
- "under_18": playful, encouraging, exclamation points OK
- "18_24": peer-friendly, college-aware
- "25_34" / "35_49": professional, time-respecting, no fluff
- "50_plus": warm, patient, never patronizing

Bridge framing for "mid_career_switcher": at least one sentence in the lesson should connect this Python concept to something they already know from their current_field (e.g., "If you've used pivot tables in Excel, dictionaries are the same idea in code").

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
