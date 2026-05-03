"""
IBM watsonx.ai client wrapper for EduBob v2
Single entry point for all LLM generation calls
"""

import os
import json
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import watsonx.ai SDK
try:
    from ibm_watsonx_ai import APIClient
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
except ImportError:
    print("ERROR: ibm-watsonx-ai package not installed. Run: pip install ibm-watsonx-ai")
    raise

# Configuration from environment
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
MODEL_ID = "mistralai/mistral-small-3-1-24b-instruct-2503"

# Global client instance (initialized on first use)
_client = None
_model = None


def _init_client():
    """Initialize watsonx.ai client and model (lazy initialization)"""
    global _client, _model
    
    if _client is not None:
        return
    
    if not WATSONX_API_KEY or not WATSONX_PROJECT_ID:
        raise ValueError(
            "Missing watsonx.ai credentials. Set WATSONX_API_KEY and WATSONX_PROJECT_ID in .env file"
        )
    
    try:
        # Create credentials
        credentials = Credentials(
            url=WATSONX_URL,
            api_key=WATSONX_API_KEY
        )
        
        # Initialize client
        _client = APIClient(credentials)
        
        # Initialize model
        _model = ModelInference(
            model_id=MODEL_ID,
            api_client=_client,
            project_id=WATSONX_PROJECT_ID
        )
        
        print(f"✓ Watsonx.ai client initialized (model: {MODEL_ID})")
        
    except Exception as e:
        print(f"ERROR initializing watsonx.ai client: {e}")
        raise


def generate(
    prompt: str,
    system: str = "",
    max_tokens: int = 1000,
    temperature: float = 0.3
) -> str:
    """
    Single entry point for watsonx.ai text generation.
    
    Args:
        prompt: The user prompt/question
        system: Optional system message to guide model behavior
        max_tokens: Maximum tokens to generate (default: 1500)
        temperature: Sampling temperature 0.0-1.0 (default: 0.3 for more deterministic)
    
    Returns:
        Raw model text output. Caller is responsible for parsing JSON if needed.
        Returns "{}" on failure to allow graceful degradation.
    """
    # Lazy initialization
    if _model is None:
        _init_client()
    
    try:
        # Combine system and user prompt
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"
        
        # Set generation parameters
        params = {
            GenParams.MAX_NEW_TOKENS: max_tokens,
            GenParams.TEMPERATURE: temperature,
            GenParams.TOP_P: 0.95,
            GenParams.TOP_K: 50,
            GenParams.REPETITION_PENALTY: 1.1,
        }
        
        # Generate text with timeout
        print(f"\n🤖 Calling watsonx.ai (max_tokens={max_tokens}, temp={temperature})...")
        print(f"   Prompt length: {len(full_prompt)} chars")
        
        response = _model.generate(
            prompt=full_prompt,
            params=params
        )
        
        # Extract generated text
        generated_text = response.get("results", [{}])[0].get("generated_text", "")
        
        # Log token usage
        token_info = response.get("results", [{}])[0]
        input_tokens = token_info.get("input_token_count", 0)
        output_tokens = token_info.get("generated_token_count", 0)
        
        print(f"✓ Generated {output_tokens} tokens (input: {input_tokens})")
        print(f"   Response preview: {generated_text[:100]}...")
        
        # Log AI activity if Streamlit is available
        try:
            from core.state import log_ai_activity
            log_ai_activity("AI generation", input_tokens + output_tokens)
        except Exception:
            pass  # Not in Streamlit context
        
        return generated_text.strip()
        
    except Exception as e:
        print(f"ERROR in watsonx.ai generate(): {e}")
        print(f"   Returning empty JSON fallback")
        return "{}"


def generate_json(
    prompt: str,
    system: str = "",
    max_tokens: int = 1000,
    temperature: float = 0.3,
    validator=None,
) -> Optional[dict]:
    """
    Generate, parse JSON, and retry once on failure with a stricter prompt.

    Args:
        prompt: The user prompt
        system: Optional system message
        max_tokens: Token limit
        temperature: Sampling temp (lowered automatically on retry for determinism)
        validator: Optional callable(parsed_dict) -> bool. If provided, parsed result
                   must pass validation; otherwise treated as failure.

    Returns:
        Parsed dict on success, None on failure (caller falls back).

    Side effects:
        - On success: resets the AI failure streak counter
        - On failure: increments the AI failure streak counter
    """
    # Local import to avoid circular dependency at module load time
    from core.prompts import parse_json_response

    def _try_parse(text: str) -> Optional[dict]:
        result = parse_json_response(text)
        if result is None:
            return None
        if validator and not validator(result):
            return None
        return result

    # First attempt
    response = generate(prompt, system=system, max_tokens=max_tokens, temperature=temperature)
    parsed = _try_parse(response)
    if parsed is not None:
        try:
            from core.state import reset_ai_failure_count
            reset_ai_failure_count()
        except Exception:
            pass
        return parsed

    # Retry once with a stricter system prompt and lower temperature
    print("⚠ First generation produced unparseable JSON — retrying with stricter prompt")
    strict_system = (
        (system + "\n\n" if system else "")
        + "CRITICAL: Output ONLY a single valid JSON object. No prose before or after. "
        + "No code fences. No commentary. The very first character of your response MUST be `{` "
        + "and the very last character MUST be `}`."
    )
    response = generate(
        prompt,
        system=strict_system,
        max_tokens=max_tokens,
        temperature=max(0.1, temperature - 0.2),
    )
    parsed = _try_parse(response)
    if parsed is not None:
        try:
            from core.state import reset_ai_failure_count
            reset_ai_failure_count()
        except Exception:
            pass
        return parsed

    # Both attempts failed
    try:
        from core.state import record_ai_failure
        record_ai_failure()
    except Exception:
        pass
    return None


def test_connection():
    """Test watsonx.ai connection and credentials"""
    try:
        _init_client()
        
        # Try a simple generation
        result = generate(
            prompt="Say 'Hello from watsonx.ai' in JSON format: {\"message\": \"...\"}",
            max_tokens=50
        )
        
        print(f"\n✓ Connection test successful!")
        print(f"   Response: {result}")
        return True
        
    except Exception as e:
        print(f"\n✗ Connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the client when run directly
    print("Testing watsonx.ai client...")
    test_connection()

# Made with Bob
