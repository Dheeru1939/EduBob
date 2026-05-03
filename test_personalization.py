"""
Personalization regression test for EduBob v2.

Runs the live curriculum prompt against watsonx.ai with 3 distinct personas
and prints the results side-by-side. Verifies that the personalization layer
produces visibly different curricula.

Usage:
    python test_personalization.py

Cost: ~3 LLM calls, ~5-8K tokens total.
"""

import json
from core.watsonx_client import generate_json
from core.prompts import build_curriculum_prompt


PERSONAS = [
    {
        "name": "Marketing pro pivoting to data (32yo)",
        "profile": {
            "age_band": "25_34",
            "life_context": "mid_career_switcher",
            "current_field": "marketing manager at a B2B SaaS company",
            "interests": ["data"],
            "motivation": "pivot from marketing into a data role",
            "skill_level": "absolute_beginner",
            "preferred_style": "project-based",
        },
    },
    {
        "name": "Curious teen exploring web (16yo)",
        "profile": {
            "age_band": "under_18",
            "life_context": "student",
            "current_field": "high school sophomore who loves video games",
            "interests": ["web"],
            "motivation": "build a website for my gaming clan",
            "skill_level": "absolute_beginner",
            "preferred_style": "hands-on",
        },
    },
    {
        "name": "Retired teacher learning for fun (62yo)",
        "profile": {
            "age_band": "50_plus",
            "life_context": "retired_explorer",
            "current_field": "retired primary school teacher who loves gardening and cooking",
            "interests": ["automation"],
            "motivation": "stay sharp and organize my recipes and garden notes",
            "skill_level": "absolute_beginner",
            "preferred_style": "structured",
        },
    },
]


def test_persona(persona):
    print(f"\n{'='*70}")
    print(f"PERSONA: {persona['name']}")
    print(f"{'='*70}")
    print(f"Profile: {json.dumps(persona['profile'], indent=2)}")
    print("\nGenerating curriculum...")

    prompt = build_curriculum_prompt(persona["profile"])
    curriculum = generate_json(
        prompt=prompt,
        system="You are an expert curriculum designer creating PERSONALIZED Python learning paths.",
        max_tokens=800,
        temperature=0.7,
        validator=lambda r: isinstance(r, dict) and "topics" in r and len(r.get("topics", [])) == 5,
    )

    if not curriculum:
        print("✗ FAILED: watsonx did not return valid 5-topic curriculum")
        return None

    print(f"\n>>> TRACK TITLE: {curriculum.get('track_title', '?')}")
    print(f"\nTopics:")
    for t in curriculum.get("topics", []):
        print(f"  {t.get('id')}. {t.get('title')}")
        print(f"      {t.get('summary')}")
    return curriculum


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("EduBob Personalization Regression Test")
    print("=" * 70)

    results = []
    for persona in PERSONAS:
        result = test_persona(persona)
        results.append((persona["name"], result))

    # Summary comparison
    print("\n\n" + "=" * 70)
    print("SIDE-BY-SIDE COMPARISON")
    print("=" * 70)
    for name, curr in results:
        if curr:
            title = curr.get("track_title", "?")
            topic1 = curr.get("topics", [{}])[0].get("title", "?")
            print(f"\n* {name}")
            print(f"    Track : {title}")
            print(f"    Topic1: {topic1}")
        else:
            print(f"\n* {name}")
            print(f"    FAILED -- watsonx did not return a valid curriculum")

    # Differentiation check
    titles = [c.get("track_title", "") for _, c in results if c]
    if titles and len(set(titles)) == len(titles):
        print(f"\nPASS: All {len(titles)} track titles are UNIQUE -- personalization is working")
    elif titles:
        print(f"\nWARN: Some track titles are duplicated -- personalization may need stronger prompts")
    else:
        print(f"\nFAIL: No curricula generated -- check watsonx connection")
