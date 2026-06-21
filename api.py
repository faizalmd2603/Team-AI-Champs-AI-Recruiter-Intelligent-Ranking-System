"""
backend/api.py

FastAPI backend exposing an endpoint to rank candidates.

Endpoints:
- GET /rank
    Query params:
        skills: comma-separated list of required job skills (optional)
        limit: number of top results to return (optional)
    Returns:
        JSON list of ranked candidates
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
root = Path(__file__).resolve().parents[1]
env_path = root.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Ensure src and models are importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))
sys.path.append(str(ROOT / ""))  # ensure top-level imports work

from ranking import rank_candidates  # type: ignore

app = FastAPI(title="AI Recruiter Ranking API", version="0.1")


class RankRequest(BaseModel):
    skills: Optional[List[str]] = None
    limit: Optional[int] = 10


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/rank")
def get_rank(skills: Optional[str] = Query(None, description="Comma-separated skills"),
             limit: int = Query(10, ge=1, le=100)):
    """
    Rank candidates using provided skills (comma-separated) or default sample dataset skills.

    Example:
      /rank?skills=Python,TensorFlow&limit=5
    """
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

    ranked = rank_candidates(records, job_skills=job_skills)
    return ranked[:limit]


# allow POST with JSON body
@app.post("/rank")
def post_rank(req: RankRequest):
    data_path = ROOT / "data" / "sample_candidates.csv"
    try:
        df = pd.read_csv(data_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load data: {e}")

    records = df.to_dict(orient="records")
    ranked = rank_candidates(records, job_skills=req.skills)
    return ranked[: req.limit]
