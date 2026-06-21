"""
parser.py
Responsible for parsing candidate rows (from CSV or other sources) to extract structured
fields used by the ranking pipeline. This implementation uses lightweight/mocked NLP logic.
"""

import re
from typing import Dict, List, Any

# try to use nltk tokenizer if available but provide fallback
try:
    from nltk.tokenize import word_tokenize
except Exception:
    def word_tokenize(text: str):
        return re.findall(r"\w+", text)


def normalize_skill(skill: str) -> str:
    """
    Normalize skill string to a canonical lowercased token without extra spaces.
    """
    return re.sub(r"\s+", " ", skill.strip().lower())


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract skills from a free-text skills field or resume text.
    The function expects skills to be comma-separated or space-separated tokens.
    This is a simple heuristic and can be replaced by a semantic skill extractor later.
    """
    if not isinstance(text, str) or not text:
        return []

    # Split by commas first
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if len(parts) <= 1:
        # fallback: split on slashes or words
        parts = re.split(r"[/\|;]", text)
        parts = [p.strip() for p in parts if p.strip()]

    skills = []
    for p in parts:
        # break long phrases into tokens if comma not provided
        tokens = re.split(r"\s*[\s/]+\s*", p)
        for token in tokens:
            tok = normalize_skill(token)
            if tok:
                skills.append(tok)
    # deduplicate while preserving order
    seen = set()
    out = []
    for s in skills:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def parse_candidate_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse a candidate record (e.g. a pandas Series converted to dict) and return structured data.

    Expected input keys: 'name', 'experience', 'skills', 'education' (optional)

    Returns:
        {
            "name": str,
            "experience": float,
            "skills": List[str],
            "education": str (optional),
            "raw": dict (original row)
        }
    """
    name = row.get("name") or row.get("full_name") or "Unknown"
    # experience may be stored as number or text like "7 years"
    exp_raw = row.get("experience", 0)
    experience = 0.0
    try:
        if isinstance(exp_raw, str):
            m = re.search(r"(\d+(\.\d+)?)", exp_raw)
            experience = float(m.group(1)) if m else 0.0
        else:
            experience = float(exp_raw)
    except Exception:
        experience = 0.0

    skills_field = row.get("skills", "") or ""
    skills = extract_skills_from_text(skills_field)

    education = row.get("education", "") or ""

    return {
        "name": str(name),
        "experience": experience,
        "skills": skills,
        "education": education,
        "raw": row,
    }


if __name__ == "__main__":
    # quick local demo
    sample = {"name": "Jane Doe", "experience": "4 years", "skills": "Python, Django, REST API"}
    print(parse_candidate_row(sample))
