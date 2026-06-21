#!/usr/bin/env python3
"""
scripts/groq_test.py

Simple test to validate Groq semantic_skill_score integration.
Called by GitHub Actions workflow.
"""
import sys
from pathlib import Path

# Setup imports
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "src"))
sys.path.insert(0, str(repo_root))

try:
    from groq_client import semantic_skill_score
except Exception as e:
    print(f"FAIL: Could not import groq_client: {e}")
    sys.exit(1)

# Test data
candidate = "Experienced ML engineer with Python, TensorFlow, PyTorch, NLP and cloud deployment."
skills = ["python", "tensorflow", "pytorch", "machine learning", "nlp"]

try:
    score = semantic_skill_score(candidate, skills)
    assert isinstance(score, (int, float)), f"Score is not numeric: {type(score)}"
    assert 0.0 <= score <= 1.0, f"Score out of range: {score}"
    print(f"PASS: semantic_skill_score = {score}")
    sys.exit(0)
except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)
