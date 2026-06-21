"""
backend/api.py

FastAPI backend exposing an endpoint to rank candidates.

Add query param `use_groq=true` to enable semantic matching (requires GROQ_API_URL & GROQ_API_KEY).
"""

from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path
import pandas as pd
import os
from dotenv import load_dotenv

# load .env for local development, if present
ROOT = Path(__file__).resolve().parents[1]
env_path = ROOT.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Ensure src is importable
sys.path.append(str(ROOT / "src"))
sys.path.append(str(ROOT / ""))  # ensure top-level imports work

from ranking import rank_candidates  # type: ignore

app = FastAPI(title="AI Recruiter Ranking API", version="0.1")


class RankRequest(BaseModel):
    skills: Optional[List[str]] = None
    limit: Optional[int] = 10
    use_groq: Optional[bool] = False


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/rank")
def get_rank(
    skills: Optional[str] = Query(None, description="Comma-separated skills"),
    limit: int = Query(10, ge=1, le=100),
    use_groq: bool = Query(False, description="Enable Groq semantic matching"),
):
    # load sample data
    data_path = ROOT / "data" / "sample_candidates.csv"
    try:
        df = pd.read_csv(data_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load data: {e}")

    records = df.to_dict(orient="records")
    job_skills = None
    if skills:
        job_skills = [s.strip() for s in skills.split(",") if s.strip()]

    ranked = rank_candidates(records, job_skills=job_skills, use_semantic=use_groq)
    return ranked[:limit]


@app.post("/rank")
def post_rank(req: RankRequest):
    data_path = ROOT / "data" / "sample_candidates.csv"
    try:
        df = pd.read_csv(data_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load data: {e}")

    records = df.to_dict(orient="records")
    ranked = rank_candidates(records, job_skills=req.skills, use_semantic=bool(req.use_groq))
    return ranked[: req.limit]
