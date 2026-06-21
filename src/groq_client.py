"""
src/groq_client.py

Groq (Responses API) integration with robust parsing and TF-IDF fallback.

Behavior:
- Uses environment variables:
  - GROQ_API_KEY
  - GROQ_API_URL (defaults to https://api.groq.com/openai/v1/responses)
  - GROQ_MODEL (optional)
- Tries Groq Responses endpoint first (asks model to return EXACT JSON {"similarity": number}).
- If Groq call fails or requests/sklearn not available, falls back to TF-IDF or simple token-overlap.
"""

import os
import json
import re
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


def _extract_first_float_from_text(text: str):
    if not text:
        return None
    # try JSON first
    try:
        parsed = json.loads(text.strip())
        if isinstance(parsed, dict):
            for k in ("similarity", "score", "semantic_score"):
                if k in parsed and isinstance(parsed[k], (int, float)):
                    return max(0.0, min(1.0, float(parsed[k])))
    except Exception:
        pass
    # fallback: regex for number
    m = re.search(r"(\d+\.\d+|\d+)", text)
    if m:
        v = float(m.group(1))
        if v > 1.0:  # maybe percent
            v = v / 100.0
        return max(0.0, min(1.0, v))
    return None


def _call_groq_api(candidate_text: str, job_skills: List[str]) -> float:
    """
    Call Groq Responses endpoint and try to extract a numeric similarity in [0,1].
    Sends an instruction that requests EXACT JSON {"similarity": <number>}.
    """
    url = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/responses")
    key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "")  # optional
    if not url or not key or requests is None:
        raise RuntimeError("Groq config missing or 'requests' not installed")

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    instruction = (
        "Compare the candidate to the required skills and return EXACTLY a JSON object "
        'with one key named \"similarity\" whose value is a decimal between 0 and 1, and nothing else.\n\n'
        f"Candidate: {candidate_text}\n"
        f"Required skills: {', '.join(job_skills)}\n\n"
        'Return ONLY: {"similarity": 0.0}'
    )

    payload = {"input": instruction}
    if model:
        payload["model"] = model

    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    # 1) top-level numeric key
    if isinstance(data, dict):
        for k in ("similarity", "score", "semantic_score"):
            if k in data and isinstance(data[k], (int, float)):
                return max(0.0, min(1.0, float(data[k])))

    # 2) common nested shapes (output/outputs/choices)
    def extract_from_output(obj):
        out_candidates = []
        for key in ("output", "outputs", "choices", "data"):
            val = obj.get(key)
            if val:
                out_candidates.append(val)
        for out in out_candidates:
            # list or dict
            if isinstance(out, list):
                for item in out:
                    # look for content fields or text fields
                    if isinstance(item, dict):
                        # content -> list of content dicts
                        content = item.get("content")
                        if isinstance(content, list):
                            for c in content:
                                if isinstance(c, dict):
                                    for txt_key in ("text", "payload", "body"):
                                        if txt_key in c and isinstance(c[txt_key], str):
                                            v = _extract_first_float_from_text(c[txt_key])
                                            if v is not None:
                                                return v
                        # message or text keys
                        if "message" in item and isinstance(item["message"], dict):
                            msg = item["message"]
                            # message content could be list or str
                            if isinstance(msg.get("content"), list):
                                for c in msg["content"]:
                                    if isinstance(c, dict) and isinstance(c.get("text"), str):
                                        v = _extract_first_float_from_text(c["text"])
                                        if v is not None:
                                            return v
                            elif isinstance(msg.get("content"), str):
                                v = _extract_first_float_from_text(msg["content"])
                                if v is not None:
                                    return v
                        if "text" in item and isinstance(item["text"], str):
                            v = _extract_first_float_from_text(item["text"])
                            if v is not None:
                                return v
                    else:
                        # item might be plain text
                        if isinstance(item, str):
                            v = _extract_first_float_from_text(item)
                            if v is not None:
                                return v
            elif isinstance(out, dict):
                # recursively try dict
                for k, v in out.items():
                    if isinstance(v, str):
                        val = _extract_first_float_from_text(v)
                        if val is not None:
                            return val
                    if isinstance(v, (int, float)) and k in ("similarity", "score", "semantic_score"):
                        return max(0.0, min(1.0, float(v)))
        return None

    val = extract_from_output(data)
    if val is not None:
        return val

    # 3) try any float in the full JSON string
    full = json.dumps(data)
    fallback = _extract_first_float_from_text(full)
    if fallback is not None:
        return fallback

    raise RuntimeError("Unable to extract numeric similarity from Groq response")


def _tfidf_similarity(candidate_text: str, job_skills: List[str]) -> float:
    """
    Fallback TF-IDF similarity between candidate_text and the job_skills joined text.
    Returns a value between 0.0 and 1.0.
    """
    if TfidfVectorizer is None or cosine_similarity is None:
        cand_tokens = set((candidate_text or "").lower().split())
        skill_tokens = set(" ".join(job_skills or []).lower().split())
        if not skill_tokens:
            return 0.0
        overlap = cand_tokens.intersection(skill_tokens)
        return float(len(overlap)) / float(len(skill_tokens)) if skill_tokens else 0.0

    docs = [candidate_text or "", " ".join(job_skills or [])]
    vec = TfidfVectorizer(stop_words="english").fit_transform(docs)
    sim = cosine_similarity(vec[0:1], vec[1:2])[0][0]
    return float(max(0.0, min(1.0, sim)))


def semantic_skill_score(candidate_text: str, job_skills: List[str]) -> float:
    """
    Public: compute semantic similarity in 0..1
    """
    candidate_text = candidate_text or ""
    job_skills = job_skills or []
    try:
        return _call_groq_api(candidate_text, job_skills)
    except Exception:
        try:
            return _tfidf_similarity(candidate_text, job_skills)
        except Exception:
            return 0.0
