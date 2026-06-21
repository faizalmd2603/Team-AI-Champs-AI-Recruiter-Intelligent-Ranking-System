"""
src/groq_client.py

Optional Groq.ai integration with fallback to local TF-IDF semantic matching.

Behavior:
- If environment variables GROQ_API_URL and GROQ_API_KEY are present, attempt a POST to that URL.
  The exact payload/response parsing is generic so adapt if Groq's API differs.
- If the call fails or secrets are absent, fall back to a local TF-IDF cosine similarity.
"""

import os
import json
from typing import List

# network call
try:
    import requests
except Exception:
    requests = None  # requests may not be installed; fallback will still work

# local fallback
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:
    TfidfVectorizer = None
    cosine_similarity = None


def _call_groq_api(candidate_text: str, job_skills: List[str]) -> float:
    """
    Generic POST to a Groq-style API. Adapt the endpoint/payload per Groq docs.
    Expects a JSON response with a numeric score in keys like 'similarity' or 'score'.
    Returns float in [0.0, 1.0] on success or raises on failure.
    """
    url = os.getenv("GROQ_API_URL")
    key = os.getenv("GROQ_API_KEY")
    if not url or not key or requests is None:
        raise RuntimeError("Groq config missing or 'requests' not installed")

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    payload = {
        "input": candidate_text,
        "skills": job_skills,
        # adapt or extend payload according to your Groq API requirements
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    # try several common response keys
    if isinstance(data, dict):
        for k in ("similarity", "score", "similarity_score", "semantic_score"):
            if k in data and isinstance(data[k], (int, float)):
                val = float(data[k])
                # clamp to 0..1
                return max(0.0, min(1.0, val))
        # sometimes nested under data[0]
        if "data" in data and isinstance(data["data"], list) and data["data"]:
            first = data["data"][0]
            for k in ("similarity", "score"):
                if k in first and isinstance(first[k], (int, float)):
                    val = float(first[k])
                    return max(0.0, min(1.0, val))

    # If we can't find a numeric score, try to parse any floats in json string (best-effort)
    text = json.dumps(data)
    import re
    m = re.search(r"(\d+\.\d+|\d+)", text)
    if m:
        v = float(m.group(1))
        # if v looks like percent >1, normalize
        if v > 1.0:
            v = v / 100.0
        return max(0.0, min(1.0, v))

    raise RuntimeError("Unable to extract semantic score from Groq response")


def _tfidf_similarity(candidate_text: str, job_skills: List[str]) -> float:
    """
    Fallback TF-IDF similarity between candidate_text and the job_skills joined text.
    Returns a value between 0.0 and 1.0.
    """
    if TfidfVectorizer is None or cosine_similarity is None:
        # sklearn not available: best-effort simple token overlap
        cand_tokens = set(candidate_text.lower().split())
        skill_tokens = set(" ".join(job_skills).lower().split())
        if not skill_tokens:
            return 0.0
        overlap = cand_tokens.intersection(skill_tokens)
        return float(len(overlap)) / float(len(skill_tokens)) if skill_tokens else 0.0

    docs = [candidate_text or "", " ".join(job_skills) or ""]
    vec = TfidfVectorizer(stop_words="english").fit_transform(docs)
    sim = cosine_similarity(vec[0:1], vec[1:2])[0][0]
    # clip and return
    return float(max(0.0, min(1.0, sim)))


def semantic_skill_score(candidate_text: str, job_skills: List[str]) -> float:
    """
    Compute a semantic similarity score (0..1) between candidate_text and job_skills.
    Tries Groq API first, then fallback to TF-IDF local similarity.
    """
    # Normalize inputs
    candidate_text = candidate_text or ""
    job_skills = job_skills or []

    # try Groq API if configured
    try:
        score = _call_groq_api(candidate_text, job_skills)
        return score
    except Exception:
        # fallback to local similarity
        try:
            return _tfidf_similarity(candidate_text, job_skills)
        except Exception:
            return 0.0
