#!/usr/bin/env python3
"""
scripts/groq_test.py

Simple test script run by GitHub Actions to validate Groq Responses integration.
It imports src/groq_client.semantic_skill_score and calls it with a sample candidate
and job skills. The script prints the returned score and exits non-zero on failure.
"""
import sys
from pathlib import Path

# ensure src imports work
repo_root = Path(__file__).resolve().parents[1]
sys.path.append(str(repo_root / "src"))
sys.path.append(str(repo_root))

try:
    from groq_client import semantic_skill_score
except Exception as e:
    print("ERROR: failed to import groq_client:", e)
    sys.exit(2)

candidate = (
    "Experienced ML engineer with Python, TensorFlow, PyTorch, NLP and cloud deployment experience."
)
skills = ["python", "tensorflow", "pytorch", "machine learning", "nlp"]

try:
    score = semantic_skill_score(candidate, skills)
    print(f"Groq semantic score: {score}")
    if not isinstance(score, (int, float)):
        print("ERROR: score is not numeric")
        sys.exit(3)
    if score < 0 or score > 1:
        print("ERROR: score out of range 0..1")
        sys.exit(4)
    print("SUCCESS: Groq test passed")
    sys.exit(0)
except Exception as e:
    print("ERROR: exception calling semantic_skill_score:", e)
    sys.exit(5)
