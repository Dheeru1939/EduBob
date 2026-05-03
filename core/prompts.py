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

CRITICAL OUTPUT FORMAT — your VERY FIRST CHARACTER must be an opening curly brace. Your VERY LAST CHARACTER must be a closing curly brace. No preamble like "Here it is:", "Sure!", "Example:", or "```json". No trailing commentary. One single JSON object only."""


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

If a field truly cannot be inferred, use the first option as a safe default.

CRITICAL: First character must be an opening curly brace. No preamble. No "Here it is:" or similar. Just the JSON object."""


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

The topics array MUST contain exactly 5 entries (id 1 through 5).

CRITICAL: First character must be an opening curly brace. No preamble. No "Here is your curriculum:" or similar. Just the JSON object."""


TOPIC_CONTENT_PROMPT = """Generate complete topic content for THIS specific learner. Lesson must be friendly markdown (length: 150 words for under_18, 200-400 words otherwise). Quiz: 3 multiple-choice questions, each with 4 options. Code challenge: a function-writing task with 2 test cases. Test cases must be deterministic and runnable via `exec()` in a restricted namespace (no imports, no I/O).

ALL examples in the lesson, quiz scenarios, and code challenge MUST come from the learner's `current_field` and reflect their `life_context`. Do not use generic examples like "shopping cart" or "todo list" unless they fit the learner's domain.

Tone calibration:
- "under_18": playful, encouraging, exclamation points OK
- "18_24": peer-friendly, college-aware
- "25_34" / "35_49": professional, time-respecting, no fluff
- "50_plus": warm, patient, never patronizing

Bridge framing for "mid_career_switcher": at least one sentence in the lesson should connect this Python concept to something they already know from their current_field (e.g., "If you've used pivot tables in Excel, dictionaries are the same idea in code").

CRITICAL TEST CASE RULES (must follow precisely):
1. Each test case input must be SOLVABLE by the simplest, most natural implementation of the prompt. Do NOT add edge cases (trailing slashes, leading/trailing whitespace, mixed case, numeric precision quirks) unless the prompt EXPLICITLY says to handle them.
2. The `expected` value must equal EXACTLY what the natural implementation returns when given the `input`. Verify this by mentally running the function before writing the test case.
3. If the function builds a URL by concatenating with "/", inputs must NOT have trailing slashes. The natural implementation does NOT strip them.
4. If the function returns a string, do NOT add hidden whitespace, do NOT use unicode quotes, do NOT mix quote styles.
5. For numeric functions, use simple integers or short floats. Avoid floating-point precision traps (no 0.1 + 0.2 type tests).
6. The `starter_code` must be a clean function definition with `pass` as its body — exactly: `def function_name(args):\n    pass`. No multi-line `pass`. No imports.
7. Test case `input` format: a Python expression literal. Examples:
   - Single string: `"'hello'"`
   - Two strings: `"'a', 'b'"` or `"('a', 'b')"`
   - Number list: `"[1, 2, 3]"`
   - Two ints: `"5, 10"`
8. Test case `expected` format: the EXACT value the function returns, with NO outer wrapping quotes. The runner compares str(actual) to str(expected).
   - WRONG (do NOT do this): `"expected": "'Hello, Alice!'"` — this puts literal quote characters in the expected string.
   - RIGHT: `"expected": "Hello, Alice!"` — just the string itself.
   - For numbers: `"expected": "15"` or `"expected": 15` (both work).
   - For lists: `"expected": "[1, 2, 3]"` (the str() representation of the list).
   - For dicts: `"expected": "{{'a': 1}}"` (the str() representation; note the doubled braces because this is a format-template — the actual JSON should be the single-brace form).

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

CRITICAL OUTPUT FORMAT — your VERY FIRST CHARACTER must be an opening curly brace. Your VERY LAST CHARACTER must be a closing curly brace. No preamble like "Here it is:", "Sure!", "Example:", or "```json". No trailing commentary. One single JSON object only."""


CODE_FEEDBACK_PROMPT = """Review the student's Python code as a supportive but HONEST tutor. Be specific about strengths and improvements. Keep summary under 30 words.

SCORING RULES (apply STRICTLY based on test_results — do not score generously):

1. If test_results shows an "error" field with "SyntaxError", "IndentationError", "NameError" before any test ran:
   - Score: 0-15
   - Verdict: "failed"
   - Reason: code did not execute. Strengths can include intent/approach if visible, but be clear the code cannot run.

2. If 0 tests passed AND code executed (returned wrong values, runtime error mid-execution):
   - Score: 15-35
   - Verdict: "failed"
   - Mention what went wrong specifically.

3. If SOME tests passed but not all (partial success):
   - Score: 40-70 (more passes = higher score within this band)
   - Verdict: "passed_with_notes"
   - Highlight what's working and what edge case is missed.

4. If ALL tests passed:
   - Score: 80-100
   - Verdict: "passed"
   - Score 90+ if code is also clean/idiomatic; 80-89 if it works but has style issues.

NEVER score above 35 if test_results.passed == 0. NEVER score 80+ unless every test passed.

Look at the test_results FIRST before forming your score. Match the score to the actual execution outcome, not the apparent effort.

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

CRITICAL OUTPUT FORMAT — your VERY FIRST CHARACTER must be an opening curly brace. Your VERY LAST CHARACTER must be a closing curly brace. No preamble like "Here it is:", "Sure!", "Example:", or "```json". No trailing commentary. One single JSON object only."""


ADAPTATION_PROMPT = """Analyze this learner's full learning history and prescribe how to teach the NEXT topic. Use the LEARNING PATTERNS to identify long-term tendencies, not just the last topic. Match `examples_flavor` to their established interests.

ADAPTATION PRINCIPLES (apply based on patterns):
- "Fast Learner" + high scores: go DEEPER, raise difficulty, less hand-holding
- "Methodical" learner: keep depth but break into smaller chunks; use more examples
- "Theory Strong, Practice Building": shallower lesson, MORE practical code examples
- "Hands-On Learner": shallower lesson; reinforce concepts THROUGH the code challenge
- "Building Foundations": go shallower, more encouraging tone, smaller code challenges
- "Perfectionist": challenge with edge cases; mention "bonus" extensions in lesson
- "Improving Rapidly": match their momentum — slightly deeper than last
- "Hitting a Plateau": pull back to shallower; encouraging tone; revisit fundamentals
- "First-Try Coder": deeper material; mention "stretch" goals
- "Top Performer": consistently deeper depth; challenging tone

Last topic performance:
{performance_record}

LEARNING PATTERNS (across all topics so far):
{learning_patterns}

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

CRITICAL OUTPUT FORMAT — your VERY FIRST CHARACTER must be an opening curly brace. Your VERY LAST CHARACTER must be a closing curly brace. No preamble like "Here it is:", "Sure!", "Example:", or "```json". No trailing commentary. One single JSON object only."""


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


VIDEO_QUERIES_PROMPT = """You are recommending YouTube tutorial searches for a learner currently studying a Python topic. Generate 3 highly-targeted search queries that would surface high-quality tutorials matching this learner's level and interests.

Each query should be:
- Short (5-9 words)
- Specific to the concept (not generic "Python tutorial")
- Calibrated to the learner's skill_level
- Where natural, reflect the learner's current_field or interest area
- Use phrasing real learners actually search for

EXAMPLES of good vs bad queries for "Lists" topic:
- BAD: "python tutorial" (too generic)
- BAD: "advanced list comprehensions deep dive" (wrong level for absolute beginner)
- GOOD for marketing-pivot beginner: "python lists for spreadsheet users beginner"
- GOOD for game-curious teen: "python lists tutorial for game developers"
- GOOD for retired explorer: "python lists explained simply for beginners"

CURRENT TOPIC: {topic_title}
TOPIC SUMMARY: {topic_summary}

LEARNER PROFILE:
{profile}

Respond with ONLY valid JSON matching this schema:
{{
  "queries": [
    {{"label": "Short button label (4-6 words, friendly)", "query": "actual youtube search query"}},
    {{"label": "Another button label", "query": "another youtube search query"}},
    {{"label": "Third button label", "query": "third youtube search query"}}
  ]
}}

CRITICAL OUTPUT FORMAT — your VERY FIRST CHARACTER must be an opening curly brace. Your VERY LAST CHARACTER must be a closing curly brace. No preamble like "Here it is:", "Sure!", "Example:", or "```json". No trailing commentary. One single JSON object only."""


def build_video_queries_prompt(topic_title: str, topic_summary: str, profile: dict) -> str:
    """Build prompt for AI-generated YouTube tutorial search queries."""
    profile_str = json.dumps(profile, indent=2)
    return VIDEO_QUERIES_PROMPT.format(
        topic_title=topic_title,
        topic_summary=topic_summary,
        profile=profile_str,
    )


LESSON_MODE_PROMPT = """You are a Python tutor re-explaining a concept the learner has already seen, in a different style. Keep it CONCISE (under 250 words). Output as friendly markdown.

The learner already read the standard explanation below. Now re-explain the SAME concept but in the requested STYLE. Do not repeat the standard lesson.

STANDARD LESSON they just read (for reference — do NOT repeat it):
{lesson_markdown}

LEARNER PROFILE:
{profile}

REQUESTED STYLE: {mode}

STYLE GUIDES (apply the one matching `mode`):

- "real_example": A short, concrete walkthrough using ONE realistic scenario from the learner's `current_field`. Show the data they would actually see, the steps, and the Python code that would handle it. Make it feel like solving a real problem in their job/life.

- "code_walkthrough": A focused code snippet (10-20 lines max) that demonstrates the concept, with INLINE comments explaining each line. Then 2-3 bullet points highlighting the key takeaways. Code first, prose second.

- "analogy": Explain the concept through a vivid everyday-life analogy (cooking, sports, organizing a closet, anything relatable). Then ONE short paragraph mapping the analogy back to Python. End with a single tiny code snippet (3-5 lines max) that shows the Python version of the analogy.

Output ONLY the explanation as markdown. No preamble like "Sure, here is..." — just the content."""


def build_lesson_mode_prompt(topic_title: str, lesson_markdown: str, profile: dict, mode: str) -> str:
    """Build prompt for an alternative-style lesson explanation.

    Args:
        topic_title: Topic name
        lesson_markdown: The original standard lesson
        profile: Learner profile dict
        mode: One of "real_example", "code_walkthrough", "analogy"
    """
    profile_str = json.dumps(profile, indent=2)
    # Trim lesson to keep prompt small
    trimmed_lesson = lesson_markdown[:800]
    return LESSON_MODE_PROMPT.format(
        lesson_markdown=trimmed_lesson,
        profile=profile_str,
        mode=mode,
    )


TOPIC_CHAT_PROMPT = """You are a friendly Python tutor named Watsonx, helping a learner who is currently studying this specific topic. Answer their question conversationally and concisely (under 200 words). Use Python examples where helpful. Reference their personal interests when natural.

If they ask about something unrelated to the current topic or to Python at all, gently redirect them back to the topic.

If they ask "explain it like I'm 5" or "give me an analogy" or similar, do exactly that.

If they ask about code, show short snippets in markdown code fences.

CURRENT TOPIC:
Title: {topic_title}
Lesson summary: {lesson_summary}

LEARNER PROFILE:
{profile}

CONVERSATION HISTORY (oldest to newest):
{chat_history}

LEARNER'S NEW QUESTION:
{user_question}

Respond as plain markdown text (no JSON wrapping, no preamble like "Sure thing!" — just answer directly). Keep it under 200 words."""


def build_topic_chat_prompt(
    topic_title: str,
    lesson_markdown: str,
    profile: dict,
    chat_history: list,
    user_question: str,
) -> str:
    """Build prompt for the AI Tutor Chat sidebar on the topic page."""
    # Take a short summary of the lesson (first 300 chars) so the prompt stays small
    lesson_summary = lesson_markdown[:400].replace("\n", " ").strip()
    profile_str = json.dumps(profile, indent=2)

    if chat_history:
        history_str = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in chat_history[-6:]  # last 3 exchanges
        )
    else:
        history_str = "(no prior turns)"

    return TOPIC_CHAT_PROMPT.format(
        topic_title=topic_title,
        lesson_summary=lesson_summary,
        profile=profile_str,
        chat_history=history_str,
        user_question=user_question,
    )


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

CRITICAL OUTPUT FORMAT — your VERY FIRST CHARACTER must be an opening curly brace. Your VERY LAST CHARACTER must be a closing curly brace. No preamble like "Here it is:", "Sure!", "Example:", or "```json". No trailing commentary. One single JSON object only."""


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
    next_topic_title: str,
    learning_patterns: Dict = None,
) -> str:
    """
    Build prompt for generating adaptation directive.

    Args:
        performance_record: Last topic's performance (schema 5.5)
        prior_directives: List of previous adaptation directives
        next_topic_title: Title of the upcoming topic
        learning_patterns: Output of detect_learning_patterns (multi-topic trends)

    Returns:
        Formatted prompt string
    """
    perf_str = json.dumps(performance_record, indent=2)

    if prior_directives:
        directives_str = json.dumps(prior_directives, indent=2)
    else:
        directives_str = "No prior directives. This is the first adaptation."

    if learning_patterns and learning_patterns.get("patterns"):
        patterns_str = json.dumps(learning_patterns, indent=2)
    else:
        patterns_str = "No multi-topic patterns detected yet (this is one of the first topics)."

    return ADAPTATION_PROMPT.format(
        performance_record=perf_str,
        prior_directives=directives_str,
        next_topic_title=next_topic_title,
        learning_patterns=patterns_str,
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
