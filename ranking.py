"""
ranking.py
Contains the logic to rank candidates given parsed candidate records and job requirements.

This updated version optionally uses semantic matching (Groq) via src/groq_client.py.
If semantic matching is enabled (use_semantic=True), a blended skill match ratio is used.
"""

from typing import List, Dict, Any, Optional
from models.model import ScoringModel
from parser import parse_candidate_row

# optional semantic client
try:
    from groq_client import semantic_skill_score  # type: ignore
except Exception:
    semantic_skill_score = None  # not available; safe fallback


def compute_skill_match(candidate_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
    """
    Compute how many required skills a candidate matches using keyword matching.
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
    use_semantic: bool = False,
) -> List[Dict[str, Any]]:
    """
    Rank a list of raw candidate rows (dicts). Each row is parsed and scored.

    If use_semantic is True and src/groq_client.semantic_skill_score is available,
    the skill match ratio is blended: blended = 0.6 * keyword_ratio + 0.4 * semantic_score.
    """
    parsed = []
    for row in raw_candidates:
        p = parse_candidate_row(row)
        parsed.append(p)

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
        keyword_ratio = skill_info["matched_ratio"]

        final_skill_ratio = keyword_ratio
        if use_semantic and semantic_skill_score is not None:
            # Build candidate text to send to semantic client
            candidate_text = " ".join(
                [p.get("name", ""), p.get("education", "")] + p.get("skills", [])
            )
            try:
                sem_score = semantic_skill_score(candidate_text, required)  # 0..1
                # Blend ratios (weights adjustable)
                final_skill_ratio = 0.6 * keyword_ratio + 0.4 * sem_score
            except Exception:
                final_skill_ratio = keyword_ratio

        score = ScoringModel.score(
            experience_years=p["experience"],
            matched_skill_ratio=final_skill_ratio,
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
            "skill_match_ratio": final_skill_ratio,
            "score": round(score, 2),
        }
        scored.append(candidate_out)

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


if __name__ == "__main__":
    demo = [
        {"name": "A", "experience": 5, "skills": "Python, TensorFlow, AWS"},
        {"name": "B", "experience": 8, "skills": "Java, Spring, AWS"},
    ]
    print(rank_candidates(demo, job_skills=["Python", "TensorFlow"], use_semantic=False))
