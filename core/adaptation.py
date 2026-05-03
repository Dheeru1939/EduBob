"""
Adaptive Learning Engine for EduBob v2
Analyzes learner performance and generates adaptation directives
"""

import json
from typing import Dict, List, Optional, Any

from .watsonx_client import generate
from .prompts import build_adaptation_prompt, parse_json_response


def compute_next_directive(
    last_perf: Dict[str, Any],
    prior_directives: List[Dict[str, Any]],
    next_topic_title: str
) -> Dict[str, Any]:
    """
    Analyze learner's last topic performance and compute adaptation directive
    for the next topic.
    
    Args:
        last_perf: Performance record from last completed topic (schema 5.5)
        prior_directives: List of previous adaptation directives
        next_topic_title: Title of the upcoming topic
    
    Returns:
        Adaptation directive dict (schema 5.6):
        {
            "depth": "shallower" | "standard" | "deeper",
            "examples_flavor": "web" | "automation" | "data" | "ai" | "games" | "scripting" | "general",
            "extra_emphasis": "specific concept to emphasize",
            "tone": "more_encouraging" | "standard" | "more_challenging"
        }
        
        Falls back to standard directive on parse failure.
    """
    # Build the adaptation prompt
    prompt = build_adaptation_prompt(last_perf, prior_directives, next_topic_title)
    
    try:
        # Call watsonx.ai to generate adaptation directive
        response = generate(
            prompt=prompt,
            system="You are an adaptive learning system analyzing student performance.",
            max_tokens=200,  # directive is a small JSON — 200 plenty
            temperature=0.4  # Slightly higher for more varied adaptations
        )
        
        # Parse JSON response
        directive = parse_json_response(response)
        
        if directive and _validate_directive(directive):
            print(f"✓ Adaptation directive computed for '{next_topic_title}'")
            print(f"   Depth: {directive.get('depth')}, Tone: {directive.get('tone')}")
            return directive
        else:
            print(f"⚠ Invalid directive format, using fallback")
            return _get_fallback_directive()
            
    except Exception as e:
        print(f"ERROR computing adaptation directive: {e}")
        return _get_fallback_directive()


def _validate_directive(directive: Dict[str, Any]) -> bool:
    """
    Validate that directive has required fields with valid values.
    """
    if not isinstance(directive, dict):
        return False
    
    # Check required fields
    required_fields = ["depth", "examples_flavor", "tone"]
    if not all(field in directive for field in required_fields):
        return False
    
    # Validate depth values
    valid_depths = ["shallower", "standard", "deeper"]
    if directive["depth"] not in valid_depths:
        return False
    
    # Validate examples_flavor values
    valid_flavors = ["web", "automation", "data", "ai", "games", "scripting", "general"]
    if directive["examples_flavor"] not in valid_flavors:
        return False
    
    # Validate tone values
    valid_tones = ["more_encouraging", "standard", "more_challenging"]
    if directive["tone"] not in valid_tones:
        return False
    
    return True


def _get_fallback_directive() -> Dict[str, Any]:
    """
    Return a safe fallback directive when generation fails.
    """
    return {
        "depth": "standard",
        "examples_flavor": "general",
        "extra_emphasis": "core concepts",
        "tone": "standard"
    }


def analyze_performance_trend(performance_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze overall performance trend across multiple topics.
    Useful for understanding learner's progress over time.
    
    Args:
        performance_records: List of performance records
    
    Returns:
        Dict with trend analysis:
        {
            "average_quiz_score": float,
            "average_code_score": float,
            "pass_rate": float,
            "trend": "improving" | "stable" | "declining",
            "total_topics": int
        }
    """
    if not performance_records:
        return {
            "average_quiz_score": 0.0,
            "average_code_score": 0.0,
            "pass_rate": 0.0,
            "trend": "stable",
            "total_topics": 0
        }
    
    # Calculate averages
    quiz_scores = []
    code_scores = []
    passes = 0
    
    for record in performance_records:
        # Quiz score as percentage
        quiz_total = record.get("quiz_total", 1)
        quiz_score = (record.get("quiz_score", 0) / quiz_total) * 100
        quiz_scores.append(quiz_score)
        
        # Code score
        code_scores.append(record.get("code_score", 0))
        
        # Pass count
        if record.get("code_passed", False):
            passes += 1
    
    avg_quiz = sum(quiz_scores) / len(quiz_scores)
    avg_code = sum(code_scores) / len(code_scores)
    pass_rate = (passes / len(performance_records)) * 100
    
    # Determine trend (compare first half vs second half)
    trend = "stable"
    if len(performance_records) >= 2:
        mid = len(performance_records) // 2
        first_half_avg = sum(code_scores[:mid]) / len(code_scores[:mid])
        second_half_avg = sum(code_scores[mid:]) / len(code_scores[mid:])
        
        if second_half_avg > first_half_avg + 10:
            trend = "improving"
        elif second_half_avg < first_half_avg - 10:
            trend = "declining"
    
    return {
        "average_quiz_score": round(avg_quiz, 1),
        "average_code_score": round(avg_code, 1),
        "pass_rate": round(pass_rate, 1),
        "trend": trend,
        "total_topics": len(performance_records)
    }


def suggest_depth_adjustment(last_perf: Dict[str, Any]) -> str:
    """
    Simple heuristic to suggest depth adjustment based on performance.
    
    Args:
        last_perf: Last performance record
    
    Returns:
        "shallower" | "standard" | "deeper"
    """
    quiz_score = last_perf.get("quiz_score", 0)
    quiz_total = last_perf.get("quiz_total", 3)
    code_score = last_perf.get("code_score", 0)
    
    quiz_percentage = (quiz_score / quiz_total) * 100
    
    # If both quiz and code are strong, go deeper
    if quiz_percentage >= 100 and code_score >= 90:
        return "deeper"
    
    # If struggling with either, go shallower
    elif quiz_percentage < 67 or code_score < 60:
        return "shallower"
    
    # Otherwise, keep standard
    else:
        return "standard"


def suggest_tone_adjustment(last_perf: Dict[str, Any]) -> str:
    """
    Simple heuristic to suggest tone adjustment based on performance.
    
    Args:
        last_perf: Last performance record
    
    Returns:
        "more_encouraging" | "standard" | "more_challenging"
    """
    code_passed = last_perf.get("code_passed", False)
    code_score = last_perf.get("code_score", 0)
    
    # If failed or low score, be more encouraging
    if not code_passed or code_score < 60:
        return "more_encouraging"
    
    # If excellent performance, can be more challenging
    elif code_score >= 95:
        return "more_challenging"
    
    # Otherwise, standard tone
    else:
        return "standard"


if __name__ == "__main__":
    print("adaptation.py - Adaptive learning engine")
    print("This module analyzes performance and generates adaptation directives")
    
    # Test with sample performance
    sample_perf = {
        "topic_id": 1,
        "quiz_score": 2,
        "quiz_total": 3,
        "code_score": 75,
        "code_passed": True,
        "time_seconds": 300,
        "regenerations_used": 0
    }
    
    print(f"\nSample performance: {sample_perf}")
    print(f"Suggested depth: {suggest_depth_adjustment(sample_perf)}")
    print(f"Suggested tone: {suggest_tone_adjustment(sample_perf)}")

# Made with Bob
