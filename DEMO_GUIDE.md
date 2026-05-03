# EduBob — Demo & Submission Guide

This file is for the team member recording the hackathon demo video and filling
out the submission form. Everything you need is here: pre-flight checks, the
exact 90-second video script, persona walk-throughs, paste-ready writeup text,
and a backup plan if something breaks mid-recording.

> **Submission form fields covered:**
> 1. Video demonstration URL
> 2. Written problem and solution statement (≤500 words) — see §4
> 3. Written statement on technology — see §5
> 4. Code repository (public): `https://github.com/Dheeru1939/EduBob`
> 5. Exported IBM Bob report — included at `bob_sessions/phase4_dynamic_tutor.md`

---

## 1. Pre-flight checklist (do this 30 minutes before recording)

### Environment
- [ ] Pull the latest `main` from the repo so you're recording the final version
- [ ] Run `python test_setup.py` — must show 4× `✓ PASS`
- [ ] Run `python test_prompts.py` — must show all 11 PASS (zero-cost)
- [ ] Run `python test_runner_inputs.py` — must show all 8 PASS (zero-cost)
- [ ] Run `python -m streamlit run app.py` and confirm the home page loads
- [ ] Click "🔄 Reset Session" in the sidebar to clear any prior state
- [ ] Browser cache cleared (Ctrl+Shift+R on the Streamlit page)

### Recording setup
- [ ] **OBS Studio** installed (free) or QuickTime Player on Mac
- [ ] Screen resolution set to **1920×1080** (recording at native res keeps text sharp)
- [ ] Microphone tested — record a 5-second clip and listen back
- [ ] Browser zoomed to **125%** for legible text on video playback
- [ ] **Disable notifications** (Windows Focus Assist on / macOS Do Not Disturb)
- [ ] Close other tabs / apps that might pop up
- [ ] Open the Streamlit app in a fresh **Incognito/Private** window
- [ ] **YouTube account ready** for upload (test a 5-second unlisted upload first)

### Submission staging
- [ ] Personal repo URL handy: `https://github.com/Dheeru1939/EduBob`
- [ ] §4 (500-word writeup) and §5 (tech statement) of this guide open in a tab for paste

---

## 2. The 90-second demo script

This is the script. Stick to it. Each line below is roughly one beat (5–10 seconds).

### Persona for the demo: 32-year-old marketing manager pivoting to data
The most relatable persona — "career switcher in a non-tech field" — and produces the most visibly tailored output.

### Beat-by-beat script

#### **0:00 – 0:08** | Hero homepage
**Show:** the home page with the gradient hero card.
**Voiceover:**
> "EduBob is an adaptive AI Python tutor — built with IBM Bob, powered by IBM watsonx.ai. It doesn't just teach Python. It learns *how* you learn, then re-shapes every lesson around you."

**Click:** 🚀 Start Learning

#### **0:08 – 0:20** | Dynamic onboarding
**Show:** answering 3-4 questions.
- Q1: pick **"25–34 (building my career)"**
- Q2: pick **"Working professional in a non-tech field..."**
- Q3: pick **"Marketing / Sales / Communications"**
- Q4 (if asked): pick **"Analyze data from my field"**

**Voiceover:**
> "Watsonx asks me 3 to 6 questions — it decides when it has enough. I'm telling it I'm a 32-year-old marketing manager, and I want to learn data."

#### **0:20 – 0:32** | Curriculum reveal
**Show:** the curriculum page after a few seconds of generation.
**Click:** 💡 Why this curriculum? (expand the explainer)
**Show:** the personalization meter at the top.

**Voiceover:**
> "In seconds, watsonx generated a 5-topic Python curriculum specifically for marketing managers pivoting to data. Every topic title references campaigns, audience segments, conversion rates. Not generic Python."

#### **0:32 – 0:55** | Topic 1 deep dive
**Click:** Start Topic 1.

**Show in this order, ~5 seconds each:**
1. The streaming lesson reveal
2. **Click the mode selector** → switch to **🎯 Analogy** → show watsonx generating an analogy
3. **Click 🔊 Listen** → let it speak for 2-3 seconds → click ⏸ Stop
4. **Click Generate video recommendations** → show the 3 YouTube buttons appearing
5. **Open the 💬 Ask Watsonx expander**, type *"What if my data is empty?"* → response streams in

**Voiceover (rapid):**
> "Inside one topic, I get four AI-generated lesson modes — standard, real example, code walkthrough, analogy. Each click triggers a fresh watsonx call. There's voice narration, AI-curated YouTube recommendations, and an in-lesson chat where I can ask anything."

#### **0:55 – 1:10** | Quiz + Code Challenge
**Click:** Take Quiz → (auto-switches tab)
- Answer 3 quiz questions (deliberately get one wrong to demonstrate the regenerate flow)
**Click:** Continue to Challenge → (auto-switches tab)
- Show the Monaco code editor briefly
- Type a quick simple solution
- **Click Run & Submit**
- Show test results passing + AI feedback

**Voiceover:**
> "The quiz is auto-graded. The code editor is real syntax-highlighted Monaco. Watsonx reviews my code with strict scoring — it doesn't just say 'good job', it tells me exactly what to improve."

#### **1:10 – 1:25** | Adaptive learning + sidebar
**Show:** the sidebar's 🧬 Your Learning Profile (now showing pattern tags + stats)
**Open Topic 2:** show the adaptation banner at the top.

**Voiceover:**
> "After each topic, watsonx detects patterns — am I a Fast Learner, a Theory-Strong learner, am I plateauing? It re-shapes the next topic accordingly. The sidebar shows me what the AI has learned about me, and Topic 2 starts with a banner: 'Adapted for you, based on your performance.'"

#### **1:25 – 1:30** | Capstone close
**Click:** 🚀 Preview Your Capstone Project
**Show:** the snow effect + the personalized capstone title.

**Voiceover:**
> "And finally — the capstone. Watsonx designs a personalized final project that combines everything I learned, themed to my field. EduBob: built end-to-end with IBM Bob, on IBM watsonx.ai. Thanks for watching."

**End card:** Brief pause on the capstone hero. Stop recording.

### Timing reality check
The real timing tends to run 1:45–2:00 instead of 1:30. That's fine — submission allows up to 3 minutes. Don't rush the voiceover.

---

## 3. Backup plans if something breaks mid-recording

| Failure | Recovery |
|---|---|
| **Topic generation hangs >30s** | Wait 10 more seconds — Mistral can be slow. If still nothing, click "Regenerate" or refresh. Try a different topic. |
| **A test case fails despite correct code** | Click "🔄 Regenerate the topic for me" — fresh test cases. |
| **Voice button silent** | Click somewhere on the page first (browser autoplay policy), then retry. Or skip this beat in the script. |
| **Watsonx returns garbage** | The retry-once layer should catch it. If still bad, the per-interest fallback curriculum kicks in — still demonstrable. |
| **Streamlit hangs/crashes** | Have a second terminal pre-open with `python -m streamlit run app.py` ready to start a fresh session. Reset session in browser, restart from beat. |
| **Internet drops** | The lesson + chat will fail. Pause recording. Restart when stable. |

**General rule:** if a beat takes longer than expected, it's better to let it play through than to cut. Judges watching the video know LLM latency is real and visible "AI is thinking" moments are *good* — they prove the work is real.

---

## 4. Written problem and solution statement (≤500 words)

> **Paste this into the form's "Written problem and solution statement" field.** Personalize lightly — adjust opening sentence, add a sentence about your team if you want.

---

**Problem.** New learners abandon coding because they hit two walls: (1) generic curricula that ignore *why* they wanted to learn, and (2) static feedback loops that don't adjust when the learner is struggling or bored. Existing platforms offer the same Python "variables → loops → functions" path to a marketing student, a future ML engineer, and a 60-year-old hobbyist — and grade their code with mechanical pass/fail. The result: high drop-off, low confidence, weak transfer to real projects. The same pattern hurts internal corporate upskilling, junior engineer onboarding, and certification programs across industries.

**Solution.** EduBob is an adaptive AI Python tutor that personalizes both *what* you learn and *how* it's taught — in real time. The learner answers 3–6 dynamic onboarding questions (the AI decides how many it needs). IBM watsonx.ai then synthesizes a rich learner profile (age band, life context, current field, interests, motivation, skill level) and designs a personalized 5-topic Python curriculum where every topic title and example references the learner's actual domain. A 32-year-old marketing manager pivoting to data gets topics framed in campaign metrics and A/B tests. A 16-year-old gamer building a clan website gets Python framed in tournament data and clan rosters. A 60-year-old retired teacher gets recipe organizers and garden trackers, with a patient tone.

Every topic is built on the fly: lesson, multiple-choice quiz, and Monaco-editor code challenge — generated by watsonx.ai. The lesson can be re-explained in 4 modes (Standard / Real Example / Code Walkthrough / Analogy), narrated aloud by browser TTS, and supplemented by 3 AI-curated YouTube tutorial searches. An in-lesson chat lets the learner ask watsonx anything with the topic context already loaded.

When the learner submits code, watsonx reviews it with strict per-test scoring and actionable feedback. If the quiz or challenge fails, the learner is offered to regenerate the entire topic with a shallower depth and more encouraging tone — capped to prevent abuse. After every topic, a heuristic engine detects multi-topic learning patterns ("Fast Learner", "Theory Strong / Practice Building", "Hitting a Plateau") and feeds them back into watsonx to compute an adaptation directive that re-shapes the next topic's depth, examples, and tone. After all 5 topics, watsonx generates a personalized capstone project that combines everything learned, plus a completion certificate with the learner's stats and detected patterns.

**Business value.** Adaptive learning has been proven to drive retention but historically required teams of curriculum designers and ML engineers — economically out of reach for most platforms. EduBob shows that watsonx.ai collapses that into a single weekend's work, making true personalization viable for any platform, internal training program, or enterprise reskilling initiative. The same architecture generalizes immediately beyond Python — any code-teachable subject is a prompt change, not a rebuild.

**Bob's role.** EduBob was designed and built end-to-end with IBM Bob during the hackathon. Bob owned the architecture, generated every source file, designed the prompt schemas, and produced the test-case formats. The repository's `bob_sessions/` folder documents the full transcript. Bob accelerated a multi-week project into a one-day hackathon submission.

---

## 5. Written statement on technology

> **Paste this into the form's "Written statement on technology" field.** Edit the model footnote if you swap to a different model before submission.

---

EduBob was built end-to-end with **IBM Bob** during the hackathon. Bob designed the architecture, generated all source code (~3,500 lines across 17 files), wrote the prompt templates and JSON schemas, produced the test case formats for the code execution sandbox, and authored the test suites. The complete development transcript is exported to `bob_sessions/phase4_dynamic_tutor.md` in the repository.

At runtime, **IBM watsonx.ai** powers 10 distinct product features:

1. Dynamic onboarding question generation (decides 3–6 questions based on prior answers)
2. Learner profile synthesis (age band, life context, current field, interests)
3. Personalized 5-topic Python curriculum design
4. Per-topic content generation (lesson + quiz + code challenge)
5. Multi-mode lesson re-explanations (Standard / Real Example / Code Walkthrough / Analogy)
6. Personalized YouTube tutorial search query generation
7. In-lesson chat with topic context (streaming responses)
8. Strict per-test code review with 0–100 scoring
9. Multi-topic adaptation directive computation (depth, examples, tone)
10. Personalized capstone project ideation

We initially tried `ibm/granite-3-8b-instruct` (not in our hackathon sandbox's curated model list) and `ibm/granite-4-h-small` (returned empty/garbage on our prompts). We then ran on `meta-llama/llama-3-3-70b-instruct` for several iterations — reliable JSON output but slow at 70B. We finally settled on `mistralai/mistral-small-3-1-24b-instruct-2503`, also served via watsonx.ai, which is **~4.6× faster than Llama 70B** on our regression test (78s → 17s for the 3-persona personalization sweep) with comparable JSON quality. The architecture is model-agnostic — swapping models is a one-line config change in `core/watsonx_client.py:28`, demonstrating watsonx.ai's value as a unified inference platform across IBM and partner models.

A resilience layer (`generate_json()`) wraps every structured call with retry-once-on-parse-failure plus per-call validators. A failure-streak counter surfaces a user-visible warning if watsonx repeatedly fails. Two regression test suites (`test_prompts.py`, `test_runner_inputs.py`) prevent the most common bug classes from shipping.

Watsonx Orchestrate was not used in this iteration. Future versions could expose EduBob's curriculum, lesson, and review endpoints as MCP tools so an Orchestrate agent could invoke them as part of a larger learning-management workflow — natural next step for enterprise deployment.

---

## 6. Final submission checklist

In the submission form, paste:

- [ ] **Video demonstration URL:** (your YouTube unlisted URL)
- [ ] **Written problem and solution statement:** §4 above
- [ ] **Written statement on technology:** §5 above
- [ ] **Code repository:** `https://github.com/Dheeru1939/EduBob`

Repo content checklist (verify before submitting):

- [ ] Repository is **Public** (Settings → top of page)
- [ ] README renders cleanly on the GitHub page
- [ ] LICENSE file is MIT
- [ ] `.env` is **not** in the file list (only `.env.example`)
- [ ] `bob_sessions/phase4_dynamic_tutor.md` is present and references the actual model used (Mistral via watsonx.ai)
- [ ] The "How to test" section in the README is accurate

Final timing buffer:

- [ ] Submission deadline confirmed (date + time + timezone)
- [ ] Aim to submit **at least 30 minutes** before the deadline to absorb any upload glitches
- [ ] Save a screenshot of the submission confirmation

---

## 7. Quick reference: the 10 watsonx interactions in one table

For your own reference / pitch talking points:

| # | Where in the app | What watsonx does |
|---|---|---|
| 1 | Onboarding | Generates each next question dynamically |
| 2 | Onboarding end | Synthesizes the rich learner profile |
| 3 | Curriculum page | Designs 5-topic personalized path |
| 4 | Topic page (first visit) | Generates lesson + quiz + challenge |
| 5 | Topic page (mode switch) | Re-explains in chosen mode |
| 6 | Topic page (videos) | Picks 3 YouTube searches |
| 7 | Topic page (chat) | Answers questions with topic context |
| 8 | Topic page (Run & Submit) | Reviews code with strict scoring |
| 9 | Topic page (after pass) | Computes adaptation directive |
| 10 | Capstone page | Designs personalized final project |

---

**Built with IBM Bob. Powered by IBM watsonx.ai. Submitted to the IBM Bob Hackathon, May 2026.**
