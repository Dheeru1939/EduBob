"""
Learning Pattern Detection for EduBob v2.

Heuristic detection of how a learner is learning, based on their
performance across all completed topics. Outputs human-readable
pattern tags + aggregate stats. Fed into the adaptation directive
prompt so the LLM can reason over multi-topic trends, not just the
last completed topic.
"""

from typing import List, Dict, Any


def detect_learning_patterns(performance_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze a learner's full performance history and extract pattern tags.

    Args:
        performance_history: list of performance records, each with:
            {topic_id, quiz_score, quiz_total, code_score,
             code_passed, time_seconds, regenerations_used}

    Returns:
        {
            "patterns": [{"tag": str, "evidence": str, "icon": str}],
            "summary": "1-sentence summary",
            "stats": {avg_quiz_pct, avg_code_score, avg_time_seconds,
                      topics_completed, total_regens, recent_trend}
        }
    """
    if not performance_history:
        return {
            "patterns": [],
            "summary": "Not enough data yet — complete a topic to see your learning patterns.",
            "stats": {
                "avg_quiz_pct": 0,
                "avg_code_score": 0,
                "avg_time_seconds": 0,
                "topics_completed": 0,
                "total_regens": 0,
                "recent_trend": "stable",
            },
        }

    # ---------- Aggregate stats ----------
    quiz_pcts = [
        (p.get("quiz_score", 0) / max(p.get("quiz_total", 1), 1)) * 100
        for p in performance_history
    ]
    code_scores = [p.get("code_score", 0) for p in performance_history]
    times = [p.get("time_seconds", 0) for p in performance_history]
    regens = [p.get("regenerations_used", 0) for p in performance_history]

    avg_quiz = sum(quiz_pcts) / len(quiz_pcts)
    avg_code = sum(code_scores) / len(code_scores)
    avg_time = sum(times) / len(times)
    total_regens = sum(regens)

    # ---------- Trend ----------
    recent_trend = "stable"
    if len(code_scores) >= 3:
        mid = len(code_scores) // 2
        early_avg = sum(code_scores[:mid]) / max(mid, 1)
        recent_avg = sum(code_scores[mid:]) / max(len(code_scores) - mid, 1)
        if recent_avg > early_avg + 10:
            recent_trend = "improving"
        elif recent_avg < early_avg - 10:
            recent_trend = "declining"

    # ---------- Pattern tags ----------
    patterns: List[Dict[str, str]] = []

    # Speed
    if avg_time < 180:
        patterns.append({
            "tag": "Fast Learner",
            "icon": "⚡",
            "evidence": f"averaging {int(avg_time)}s per topic",
        })
    elif avg_time > 600:
        patterns.append({
            "tag": "Methodical",
            "icon": "🐢",
            "evidence": f"taking {int(avg_time)}s per topic — depth over speed",
        })

    # Skill split
    if avg_quiz >= 85 and avg_code >= 85:
        patterns.append({
            "tag": "Top Performer",
            "icon": "🌟",
            "evidence": f"{int(avg_quiz)}% quiz · {int(avg_code)}/100 code",
        })
    elif avg_quiz >= 80 and avg_code < 60:
        patterns.append({
            "tag": "Theory Strong, Practice Building",
            "icon": "📖",
            "evidence": "knows the concepts, refining hands-on coding",
        })
    elif avg_quiz < 60 and avg_code >= 75:
        patterns.append({
            "tag": "Hands-On Learner",
            "icon": "🛠️",
            "evidence": "writes working code even when concepts feel fuzzy",
        })
    elif avg_quiz < 60 and avg_code < 60:
        patterns.append({
            "tag": "Building Foundations",
            "icon": "🌱",
            "evidence": "earlier topics need a bit more reinforcement",
        })

    # Engagement
    if total_regens >= len(performance_history):
        patterns.append({
            "tag": "Perfectionist",
            "icon": "🎯",
            "evidence": "regenerates challenges to try multiple approaches",
        })

    # Trend
    if recent_trend == "improving":
        patterns.append({
            "tag": "Improving Rapidly",
            "icon": "📈",
            "evidence": "code scores trending up across topics",
        })
    elif recent_trend == "declining":
        patterns.append({
            "tag": "Hitting a Plateau",
            "icon": "📊",
            "evidence": "recent topics scoring lower — may benefit from easier scaffolding",
        })

    # First-pass code success
    first_pass = [p for p in performance_history if p.get("code_passed") and p.get("regenerations_used", 0) == 0]
    if len(first_pass) == len(performance_history) and len(performance_history) >= 3:
        patterns.append({
            "tag": "First-Try Coder",
            "icon": "✅",
            "evidence": "passing every challenge on the first attempt",
        })

    # ---------- Summary ----------
    if not patterns:
        summary = f"You've completed {len(performance_history)} topic(s). Keep going to reveal more patterns."
    else:
        top_pattern = patterns[0]
        summary = (
            f"After {len(performance_history)} topic(s), Watsonx sees you as a "
            f"{top_pattern['tag']} — {top_pattern['evidence']}."
        )

    return {
        "patterns": patterns,
        "summary": summary,
        "stats": {
            "avg_quiz_pct": round(avg_quiz, 1),
            "avg_code_score": round(avg_code, 1),
            "avg_time_seconds": int(avg_time),
            "topics_completed": len(performance_history),
            "total_regens": total_regens,
            "recent_trend": recent_trend,
        },
    }


if __name__ == "__main__":
    # Quick smoke test
    import json
    sample = [
        {"topic_id": 1, "quiz_score": 3, "quiz_total": 3, "code_score": 90, "code_passed": True, "time_seconds": 240, "regenerations_used": 0},
        {"topic_id": 2, "quiz_score": 2, "quiz_total": 3, "code_score": 75, "code_passed": True, "time_seconds": 380, "regenerations_used": 1},
        {"topic_id": 3, "quiz_score": 3, "quiz_total": 3, "code_score": 95, "code_passed": True, "time_seconds": 200, "regenerations_used": 0},
    ]
    print(json.dumps(detect_learning_patterns(sample), indent=2))
