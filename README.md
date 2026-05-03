# EduBob 🤖

**An adaptive AI Python tutor that personalizes both *what* you learn and *how* it's taught — in real time.**

Built end-to-end with **IBM Bob**. Powered at runtime by **IBM watsonx.ai**.
Submitted to the IBM Bob Hackathon, May 2026.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io)
[![watsonx.ai](https://img.shields.io/badge/watsonx.ai-Mistral_Small_24B-0066CC.svg)](https://www.ibm.com/products/watsonx-ai)

---

## 🎯 What it does

EduBob is a Python tutor that **knows nothing about you when you arrive and a lot about you when you leave**. The same app produces a wildly different experience for:

- A **32-year-old marketing manager** pivoting to data → curriculum framed in campaign metrics, A/B tests, audience segments
- A **16-year-old gamer** curious about web → curriculum framed in clan websites, tournament data, gaming stats
- A **60-year-old retired teacher** learning for fun → patient pace, recipe organizers, garden trackers, lesson-plan analogies

Every learner gets a personalized 5-topic Python journey, multi-mode lessons (analogy / code walkthrough / real-world example), AI-graded code reviews, an in-lesson chat with watsonx, and a personalized capstone project with a completion certificate.

---

## ✨ Feature highlights

| What you get | How it works |
|---|---|
| 🎯 **Dynamic onboarding** | watsonx asks 3–6 multiple-choice questions, decides when it has enough |
| 📚 **Personalized curriculum** | 5-topic Python path tailored to age, life context, current field, and interests |
| 🤖 **Multi-mode lessons** | Same concept, 4 modes: Standard / Real Example / Code Walkthrough / Analogy |
| 🔊 **Voice narration** | Browser-native TTS reads any lesson aloud (zero LLM cost) |
| 🎥 **AI video search** | watsonx generates 3 personalized YouTube tutorial searches per topic |
| 💬 **In-lesson AI chat** | Streaming Q&A with watsonx, topic context pre-loaded |
| 💻 **Monaco code editor** | Real syntax-highlighted editor (`streamlit-ace`) with safe execution sandbox |
| 🤖 **Honest AI code review** | watsonx scores 0–100 with strict per-test grading + actionable feedback |
| 🔄 **Adaptive next-topic** | After each topic, watsonx re-shapes the next lesson's depth, tone, and examples |
| 🧬 **Pattern detection** | "Fast Learner", "Theory Strong / Practice Building", "Hitting a Plateau", etc. |
| 🏆 **Personalized capstone** | watsonx designs a final project that combines all 5 topics |
| 📜 **Completion certificate** | Stats + watsonx-detected pattern tags + your personalized track title |

**Total AI integration points:** 10 distinct watsonx-powered moments across the learner journey.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- An **IBM Cloud account** (free tier works)
- A **watsonx.ai project** with API credentials
- ~10 minutes for first setup

### 1. Clone and install

```bash
git clone https://github.com/Dheeru1939/EduBob.git
cd EduBob
pip install -r requirements.txt
```

> **Note:** If `streamlit` is not in your PATH after install, use `python -m streamlit run app.py` instead of `streamlit run app.py`. This is the safer form on Windows.

### 2. Get your watsonx.ai credentials

You need three values. **The fastest path is to use a hackathon-provided sandbox project if you have one** (skip step 2c).

#### a) WATSONX_API_KEY
1. Open https://cloud.ibm.com/iam/apikeys
2. Click **"Create"** (top right)
3. Name it `edubob`
4. **Copy the key immediately** — IBM shows it only once

#### b) WATSONX_PROJECT_ID
1. Open https://dataplatform.cloud.ibm.com/wx/home
2. Open your watsonx.ai project (or create an empty one)
3. Top menu → **Manage** tab → **General** in the left panel
4. Copy the **Project ID** field

#### c) Associate the watsonx.ai service to your project (skip if hackathon sandbox)
1. Same project → **Manage** tab → **Services & integrations** in the left panel
2. Click **"Associate service"**
3. Pick your **watsonx.ai Runtime** instance (provision a Lite tier one if needed)
4. Save

#### d) WATSONX_URL
Match your watsonx.ai region:

| Region | URL |
|---|---|
| Dallas | `https://us-south.ml.cloud.ibm.com` |
| Frankfurt | `https://eu-de.ml.cloud.ibm.com` |
| London | `https://eu-gb.ml.cloud.ibm.com` |
| Tokyo | `https://jp-tok.ml.cloud.ibm.com` |
| Sydney | `https://au-syd.ml.cloud.ibm.com` |

If unsure → use Dallas (`https://us-south.ml.cloud.ibm.com`).

### 3. Configure `.env`

```bash
cp .env.example .env
# Open .env in any editor and paste your three values
```

Final `.env` should look like:

```env
WATSONX_API_KEY=your_actual_key_here
WATSONX_PROJECT_ID=your_actual_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

> ⚠️ `.env` is gitignored. **Never commit it.** Verify with `git status` — it should not appear.

### 4. Verify your setup

```bash
python test_setup.py
```

You should see:

```
✓ PASS: Package imports
✓ PASS: Environment config
✓ PASS: Core modules
✓ PASS: Watsonx.ai connection
```

If watsonx.ai connection fails, check:
- API key is correct (no extra spaces, full string copied)
- Project ID matches the project where you associated the watsonx.ai service
- URL matches your project's region

### 5. Launch

```bash
python -m streamlit run app.py
```

The app opens at `http://localhost:8501` automatically.

---

## 🧪 Smoke test for new users (5 minutes)

Run through the full flow once to confirm everything works:

1. **Home page** — see hero card, click **🚀 Start Learning**
2. **Onboarding** — answer 3–6 AI-generated questions
   - Try answering as a *32-year-old marketing manager wanting to pivot to data*
3. **Curriculum** — should show track titled around marketing/data, with 5 topics referencing campaigns or data
4. **Click Topic 1** → **Lesson tab** loads
5. Try the mode selector: **Standard / Real Example / Code Walkthrough / Analogy** (each non-Standard takes ~3-5s to load)
6. Click **🔊 Listen** to hear the lesson
7. Click **Generate video recommendations** → 3 YouTube buttons appear
8. Open **💬 Ask Watsonx** expander, ask "What's a list?" → response streams in
9. **Take Quiz →** auto-switches to Quiz tab, answer 3 questions, submit
10. **Continue to Challenge →** auto-switches, write code in Monaco editor
11. **Run & Submit** → see test results + AI feedback
12. After completion, sidebar **🧬 Your Learning Profile** shows pattern tags
13. Open Topic 2 → adaptation banner appears at top reflecting your performance
14. Complete all 5 topics → click **🚀 Preview Your Capstone Project**
15. After all 5 done, capstone page shows the **📜 Certificate of Completion**

Anything broken? See the [Common gotchas](#-common-gotchas) section below.

---

## 🏗️ Architecture

```
EduBob/
├── app.py                          # Streamlit entry — sidebar, hero homepage, routing
├── pages/
│   ├── 1_🎯_Onboarding.py          # Dynamic Q&A → interest profile
│   ├── 2_📚_Curriculum.py          # Generated 5-topic ladder + personalization meter
│   ├── 3_📖_Topic.py               # Lesson + Quiz + Challenge (3 tabs)
│   └── 4_🏆_Capstone.py            # Personalized capstone + completion certificate
├── core/
│   ├── watsonx_client.py           # Single watsonx.ai SDK wrapper + AI activity logging
│   ├── prompts.py                  # All prompt templates + JSON schemas + helpers
│   ├── code_runner.py              # Sandboxed Python exec (multiprocessing, Windows-safe)
│   ├── state.py                    # Streamlit session-state helpers
│   ├── adaptation.py               # Performance analysis + adaptation directive
│   └── learning_patterns.py        # Multi-topic pattern detection (heuristic, no LLM)
├── .streamlit/
│   └── config.toml                 # Theme (primary color, fonts)
├── bob_sessions/
│   └── phase4_dynamic_tutor.md     # Build session transcript with IBM Bob
├── requirements.txt                # 4 deps total
├── .env.example                    # Credential template (safe to commit)
├── .env                            # YOUR secrets (gitignored, NEVER commit)
├── test_setup.py                   # Setup verification
├── test_personalization.py         # 3-persona regression (~5K tokens)
├── test_pipeline.py                # End-to-end pipeline test (~15K tokens)
├── test_prompts.py                 # Prompt builder format-string regression (zero-cost)
├── test_runner_inputs.py           # Code runner argument-parsing regression (zero-cost)
├── DEMO_GUIDE.md                   # Hackathon demo script + recording guide
├── SETUP.md                        # Original setup walkthrough
├── NEXT_STEPS.md                   # Hackathon submission checklist
└── LICENSE                         # MIT
```

---

## 🔧 Tech stack

| Layer | Tech | Notes |
|---|---|---|
| **Frontend** | Streamlit + custom CSS | Multipage app, theme via `.streamlit/config.toml` |
| **Code editor** | `streamlit-ace` | Monaco-style editor with monokai theme + line numbers |
| **Runtime AI** | IBM watsonx.ai (`mistralai/mistral-small-3-1-24b-instruct-2503`) | Powers all 10 product features at runtime |
| **Code execution** | Python `exec()` in `multiprocessing.Process` | Restricted builtins, 5s timeout, Windows-compatible |
| **State** | `streamlit.session_state` | No DB, no persistence — refresh resets the session |
| **Dev assistant** | IBM Bob | Built the entire codebase; sessions exported to `bob_sessions/` |

### About the model choice

We initially tried `ibm/granite-3-8b-instruct` (not available in our hackathon sandbox), then `ibm/granite-4-h-small` (returned empty/garbage for our prompts), then `meta-llama/llama-3-3-70b-instruct` (worked but slow at 70B). We settled on `mistralai/mistral-small-3-1-24b-instruct-2503` — **same watsonx.ai platform, ~4.6× faster than Llama 70B with comparable JSON quality.**

The model ID is one line in `core/watsonx_client.py:28`. To swap models, change just that line.

### Watsonx.ai usage breakdown

| Feature | Prompt template | Approx. tokens / call |
|---|---|---|
| Generate next onboarding question | `ONBOARDING_NEXT_QUESTION_PROMPT` | ~600 in / ~80 out |
| Synthesize learner profile | `INTEREST_PROFILE_PROMPT` | ~450 in / ~120 out |
| Generate 5-topic curriculum | `CURRICULUM_PROMPT` | ~1,500 in / ~700 out |
| Generate topic content (lesson + quiz + challenge) | `TOPIC_CONTENT_PROMPT` | ~600 in / ~900 out |
| Re-explain in alternate mode | `LESSON_MODE_PROMPT` | ~700 in / ~300 out |
| Generate YouTube tutorial searches | `VIDEO_QUERIES_PROMPT` | ~400 in / ~150 out |
| Topic chat (Q&A) | `TOPIC_CHAT_PROMPT` | ~600 in / ~250 out |
| Review submitted code | `CODE_FEEDBACK_PROMPT` | ~600 in / ~300 out |
| Compute adaptation directive | `ADAPTATION_PROMPT` | ~350 in / ~150 out |
| Generate capstone project | `CAPSTONE_PROMPT` | ~500 in / ~400 out |

All prompts are JSON-constrained (the schema is in the prompt itself). Responses go through `parse_json_response()` which handles markdown fences and stray prose. `generate_json()` adds a retry-once-on-parse-failure layer.

---

## 🧠 How adaptive learning actually works

This is the differentiating feature — worth understanding if you're testing or reviewing the code.

### Per-topic adaptation
1. Learner completes Topic N (passes the code challenge)
2. App records a `performance_record`: `{quiz_score, quiz_total, code_score, code_passed, time_seconds}`
3. App calls `learning_patterns.detect_learning_patterns()` to compute aggregate trends across ALL topics so far (heuristic, no LLM)
4. App calls `adaptation.compute_next_directive()` which sends performance + patterns to watsonx
5. Watsonx returns an `adaptation_directive`: `{depth, examples_flavor, extra_emphasis, tone}`
6. Directive is stored in `st.session_state.adaptation_history` keyed to Topic N+1
7. When learner opens Topic N+1, the directive is:
   - Pulled from session_state
   - Passed into `TOPIC_CONTENT_PROMPT` so watsonx generates the lesson with that flavor
   - Rendered as a banner at the top of the topic page
   - Reflected in the personalization meter on the curriculum page
   - Surfaced in the sidebar's "🧬 Your Learning Profile"

### Pattern tags the system detects

| Tag | Trigger | Adaptation response |
|---|---|---|
| ⚡ **Fast Learner** | Avg < 3 min per topic | Goes deeper, less hand-holding |
| 🐢 **Methodical** | Avg > 10 min per topic | Smaller chunks, more examples |
| 🌟 **Top Performer** | 85%+ quiz AND 85+ code | Consistently deeper, challenging tone |
| 📖 **Theory Strong, Practice Building** | High quiz, low code | Shallower lesson, MORE practical code |
| 🛠️ **Hands-On Learner** | Low quiz, high code | Reinforce concepts THROUGH coding |
| 🌱 **Building Foundations** | Both low | Shallower + encouraging tone |
| 🎯 **Perfectionist** | Lots of regenerations | Stretch challenges + edge cases |
| 📈 **Improving Rapidly** | Recent scores >> early | Match the momentum, slightly deeper |
| 📊 **Hitting a Plateau** | Recent scores << early | Pull back, encouraging tone |
| ✅ **First-Try Coder** | Every challenge passed first attempt + 3 topics | Stretch goals mentioned |

### Failure recovery
If a learner fails the quiz (<67%) or the code challenge, they're offered a **"Regenerate this topic"** button. This forces a `{depth: shallower, tone: more_encouraging}` directive and clears the topic cache, producing a fresh easier version. **Capped at 2 regenerations per topic** to prevent abuse.

---

## ⚙️ Customization

These are the most common knobs to turn.

| Want to change | File | Where |
|---|---|---|
| The watsonx model | `core/watsonx_client.py` | `MODEL_ID = "..."` |
| Min/max onboarding questions | `pages/1_🎯_Onboarding.py` | `MIN_QUESTIONS`, `MAX_QUESTIONS` |
| How many topics in curriculum | `core/prompts.py` (`CURRICULUM_PROMPT`) | "exactly 5 entries" |
| Max regenerations per topic | `pages/3_📖_Topic.py` | `MAX_REGENERATIONS = 2` |
| Theme colors | `.streamlit/config.toml` | `primaryColor` etc. |
| Code execution timeout | `pages/3_📖_Topic.py` | `timeout_s=5` |
| Restricted builtins for code sandbox | `core/code_runner.py` | `safe_builtins = {...}` |
| Pattern detection thresholds | `core/learning_patterns.py` | All numeric thresholds |

---

## 🧪 Running tests

All tests are in the repo root.

```bash
# Verify your setup works
python test_setup.py

# Verify all 11 prompt builders format cleanly (zero-cost, no LLM)
python test_prompts.py

# Verify the code runner handles every input format the LLM produces (zero-cost)
python test_runner_inputs.py

# Verify personalization works across 3 distinct personas (~5K tokens, ~20s)
python test_personalization.py

# Full end-to-end pipeline test (~15K tokens, ~3 min)
python test_pipeline.py
```

Run `test_prompts.py` after editing any prompt — it will catch the unescaped-brace bug class instantly.

---

## ⚠️ Known limitations (intentional / time-boxed)

- **No persistence** — refresh the browser, lose your progress. By design (POC scope).
- **No auth / multi-user** — single learner per session.
- **Sandboxed code execution is demo-grade** — restricted builtins + multiprocessing isolation are sufficient for honest learners but not adversarial ones. Don't deploy to public internet without proper containerization.
- **Latency is real** — even on Mistral Small, generating a fresh topic takes 5–15s. Mitigated by `st.write_stream` for perceived speed and per-interest fallbacks if generation fails.
- **LLM-generated test cases occasionally have edge-case bugs** — e.g., expected values wrapped in literal quotes. The runner now auto-unwraps these. If you spot a new edge case, add a regression test to `test_runner_inputs.py`.

---

## 🧯 Common gotchas

| Symptom | Likely cause / fix |
|---|---|
| `streamlit: command not found` | Use `python -m streamlit run app.py` |
| `ImportError: streamlit_ace` | Run `pip install -r requirements.txt` again |
| `KeyError` from `prompts.py` | Unescaped `{` or `}` in a new prompt — run `python test_prompts.py` |
| Test case fails despite correct code | LLM may have generated a buggy test case. Click "Regenerate the topic for me" |
| Spinner runs forever | watsonx auth issue or quota — check sidebar warning banner + terminal logs |
| Same curriculum every time | watsonx returning malformed JSON; fallback (per-interest) firing — still varied. Check terminal for the actual response |
| Voice button silent | Browser autoplay policy — click anywhere on the page once, then click Listen |
| Chat tab missing | Chat lives **inside the Lesson tab** as an expander (not a separate tab) |

---

## 📚 Documentation

- **[DEMO_GUIDE.md](DEMO_GUIDE.md)** — Recording the demo video + submission paste-text
- **[SETUP.md](SETUP.md)** — Original setup walkthrough (covers fallback paths)
- **[NEXT_STEPS.md](NEXT_STEPS.md)** — Hackathon submission checklist
- **[bob_sessions/phase4_dynamic_tutor.md](bob_sessions/phase4_dynamic_tutor.md)** — Bob's build session transcript

---

## 🏆 Hackathon submission

**IBM Bob Hackathon — May 2026.** See [DEMO_GUIDE.md](DEMO_GUIDE.md) for the full pitch + paste-ready writeup text.

### Bob's role
The entire codebase, prompt templates, JSON schemas, and architecture decisions were generated through Bob sessions. Bob authored every source file. The `bob_sessions/` folder documents the full transcript.

### Watsonx.ai's role
Powers **10 distinct product features at runtime**: onboarding, profile synthesis, curriculum design, lesson generation in 4 modes, video search recommendations, topic chat, code review, adaptation directives, and capstone project ideation.

### Submission deliverables
- ✅ Public code repository (this repo)
- ✅ Exported Bob session in `bob_sessions/`
- ✅ MIT license
- ✅ Two regression test suites (prompts + runner)
- ⏳ Video demonstration (URL added on submission)
- ⏳ Written problem/solution + tech statement (paste from DEMO_GUIDE.md)

---

## 📝 License

MIT — see [LICENSE](LICENSE).

---

## 🙏 Acknowledgments

- **IBM Bob** — development partner; built this entire codebase
- **IBM watsonx.ai** — runtime AI platform, serving Mistral Small 3.1 24B Instruct
- **Streamlit + streamlit-ace** — the UI stack that made same-day polish possible

---

**Built end-to-end with IBM Bob, on IBM watsonx.ai, in less than a day.**
