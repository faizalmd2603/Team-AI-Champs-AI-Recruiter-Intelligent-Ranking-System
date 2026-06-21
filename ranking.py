"""
ranking.py
Contains the logic to rank candidates given parsed candidate records and job requirements.
"""

from typing import List, Dict, Any, Optional
from models.model import ScoringModel
from parser import parse_candidate_row


def compute_skill_match(candidate_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
    """
    Compute how many required skills a candidate matches.

    Returns a dict:
    {
        "matched": int,
        "total_required": int,
        "matched_ratio": float (0..1),
        "matched_skills": List[str]
    }
    """
    req = [s.strip().lower() for s in required_skills if s]
    cand = [s.strip().lower() for s in candidate_skills if s]
    matched = [s for s in req if s in cand]
    total_required = max(len(req), 1)  # avoid division by zero
    matched_ratio = len(matched) / total_required
    return {
        "matched": len(matched),
        "total_required": total_required,
        "matched_ratio": matched_ratio,
        "matched_skills": matched,
    }


def rank_candidates(
    raw_candidates: List[Dict[str, Any]],
    job_skills: Optional[List[str]] = None,
    max_experience_cap: float = 10.0,
) -> List[Dict[str, Any]]:
    """
    Rank a list of raw candidate rows (dicts). Each row is parsed and scored.
    - raw_candidates: list of dict-like records (as loaded from CSV)
    - job_skills: list of skills to match against (if None, use union of candidate skills)
    - max_experience_cap: cap (in years) for normalization

    Returns:
        List of candidate dicts sorted by descending score. Each candidate dict contains:
        - name, experience, skills, score, details ...
    """
    parsed = []
    # parse rows
    for row in raw_candidates:
        p = parse_candidate_row(row)
        parsed.append(p)

    # determine required skills
    if job_skills:
        required = [s.strip() for s in job_skills if s]
    else:
        skills_pool = []
        for p in parsed:
            skills_pool.extend(p["skills"])
        required = list(dict.fromkeys(skills_pool))[:6]

    scored = []
    for p in parsed:
        skill_info = compute_skill_match(p["skills"], required)
        score = ScoringModel.score(
            experience_years=p["experience"],
            matched_skill_ratio=skill_info["matched_ratio"],
            experience_cap=max_experience_cap,
        )
        candidate_out = {
            "name": p["name"],
            "experience": p["experience"],
            "skills": p["skills"],
            "education": p.get("education", ""),
            "matched_skills": skill_info["matched_skills"],
            "matched_count": skill_info["matched"],
            "required_count": skill_info["total_required"],
            "skill_match_ratio": skill_info["matched_ratio"],
            "score": round(score, 2),
        }
        scored.append(candidate_out)

    # sort descending by score
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


if __name__ == "__main__":
    demo = [
        {"name": "A", "experience": 5, "skills": "Python, TensorFlow, AWS"},
        {"name": "B", "experience": 8, "skills": "Java, Spring, AWS"},
    ]
    print(rank_candidates(demo, job_skills=["Python", "TensorFlow"]))
