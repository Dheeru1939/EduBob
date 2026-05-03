# EduBob v2 Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd edubob_v2
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your IBM watsonx.ai credentials
# You need:
# - WATSONX_API_KEY (from IBM Cloud)
# - WATSONX_PROJECT_ID (from watsonx.ai project)
# - WATSONX_URL (default: https://us-south.ml.cloud.ibm.com)
```

### 3. Test Setup

```bash
python test_setup.py
```

This will verify:
- ✓ All packages are installed
- ✓ Environment variables are configured
- ✓ Core modules load correctly
- ✓ Watsonx.ai connection works

### 4. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## Getting IBM watsonx.ai Credentials

### Step 1: IBM Cloud Account
1. Go to [cloud.ibm.com](https://cloud.ibm.com)
2. Sign up or log in

### Step 2: Create watsonx.ai Project
1. Navigate to watsonx.ai service
2. Create a new project
3. Note your **Project ID** (found in project settings)

### Step 3: Get API Key
1. Go to IBM Cloud dashboard
2. Navigate to "Manage" → "Access (IAM)" → "API keys"
3. Create a new API key
4. Copy the key immediately (you won't see it again)

### Step 4: Configure .env
```
WATSONX_API_KEY=your_actual_api_key_here
WATSONX_PROJECT_ID=your_actual_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

---

## Project Structure

```
edubob_v2/
├── app.py                      # Main entry point
├── pages/
│   ├── 1_🎯_Onboarding.py     # Dynamic Q&A
│   ├── 2_📚_Curriculum.py     # 5-topic path
│   └── 3_📖_Topic.py          # Lesson/Quiz/Challenge
├── core/
│   ├── watsonx_client.py      # AI generation
│   ├── prompts.py             # Prompt templates
│   ├── code_runner.py         # Safe execution
│   ├── state.py               # Session management
│   └── adaptation.py          # Performance analysis
├── requirements.txt
├── .env.example
├── .env                        # Your credentials (gitignored)
├── test_setup.py              # Setup verification
└── README.md
```

---

## Testing the App

### Manual Test Flow

1. **Onboarding** (3 questions)
   - Answer questions about your interests
   - Profile is generated

2. **Curriculum** (5 topics)
   - Personalized topic list appears
   - Topics unlock sequentially

3. **Topic 1** (Lesson → Quiz → Challenge)
   - Read the lesson
   - Take the 3-question quiz
   - Complete the coding challenge
   - Get AI feedback

4. **Adaptation**
   - After completing Topic 1, Topic 2 adapts based on your performance
   - If you struggled: shallower, more encouraging
   - If you excelled: deeper, more challenging

### Test Personas

**Persona 1: Beginner Web Developer**
- Q1: "I'm an absolute beginner"
- Q2: "I want to build websites"
- Q3: "I prefer hands-on examples"
- Expected: Web-themed examples (HTML, HTTP, strings)

**Persona 2: Data Enthusiast**
- Q1: "I have some programming experience"
- Q2: "I'm interested in data analysis"
- Q3: "I like understanding theory first"
- Expected: Data-themed examples (lists, dicts, CSV concepts)

---

## Troubleshooting

### "Import streamlit could not be resolved"
```bash
pip install streamlit>=1.30
```

### "Import ibm_watsonx_ai could not be resolved"
```bash
pip install ibm-watsonx-ai>=1.0
```

### "Watsonx.ai connection failed"
- Check your API key is correct
- Verify project ID matches your watsonx.ai project
- Ensure you have internet connection
- Try the test: `python -c "from core.watsonx_client import test_connection; test_connection()"`

### "Code execution timed out"
- This is expected for infinite loops
- The timeout is 5 seconds (configurable in code_runner.py)
- Windows users: multiprocessing is used instead of signal.SIGALRM

### "Streamlit page not found"
- Make sure you're in the `edubob_v2/` directory
- Run: `streamlit run app.py` (not from parent directory)

### Session state issues
- Click "Reset Session" in the sidebar
- Or close and restart the Streamlit app

---

## Development Notes

### Adding New Topics
Edit the fallback curriculum in `pages/2_📚_Curriculum.py` if watsonx.ai generation fails.

### Modifying Prompts
All prompts are in `core/prompts.py`. Edit the constants and helper functions.

### Adjusting Code Safety
Edit `SAFE_BUILTINS` in `core/code_runner.py` to allow/restrict functions.

### Changing Adaptation Logic
Heuristics are in `core/adaptation.py` (`suggest_depth_adjustment`, `suggest_tone_adjustment`).

---

## Performance Tips

### Caching
- Topic content is cached in `st.session_state.topic_contents`
- Curriculum is cached in `st.session_state.curriculum`
- Clear cache with "Reset Session" button

### Token Usage
- Onboarding: ~300 tokens per question
- Curriculum: ~1200 tokens
- Topic content: ~1500 tokens per topic
- Code feedback: ~500 tokens per submission
- Adaptation: ~300 tokens per topic completion

**Total for 1 complete run:** ~10,000 tokens

---

## Security Notes

⚠️ **This is a demo application. Production use requires:**

1. **Proper sandboxing** beyond restricted builtins
2. **Rate limiting** on AI calls
3. **User authentication** if multi-user
4. **Input validation** on all user code
5. **Secrets management** (not .env files)

The current implementation:
- ✓ Restricts Python builtins
- ✓ Times out long-running code
- ✓ Blocks dangerous imports
- ✗ Does NOT prevent all malicious code
- ✗ Does NOT persist data (session-only)

---

## License

MIT License - See LICENSE file

---

## Support

Built with IBM Bob for the IBM Bob Hackathon (May 2026)

For issues or questions:
1. Check this SETUP.md
2. Run `python test_setup.py`
3. Review error messages in terminal
4. Check Streamlit logs in browser console