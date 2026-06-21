# AI Champs - AI Recruiter Intelligent Ranking System

**Challenge:** AI & Data Challenge — AI Recruiter Intelligent Ranking System  
**Team:** AI Champs  
**Team Leader:** Vaibhav Kumar Tyagi

---

## Overview

AI Recruiter Intelligent Ranking System is an extensible, production-ready starter repository that demonstrates an AI-powered recruitment pipeline. The system parses resumes (sample CSV included), extracts structured attributes (skills & experience), computes an explainable score, and returns ranked candidates via CLI and an API.

This repo is ideal for hackathons, portfolio demos, and as a foundation for production extensions.

---

## Features

- Resume parsing (lightweight NLP / heuristics)
- Skill matching against job requirements
- Candidate scoring and ranking (explainable formula)
- CLI demo (`src/main.py`)
- FastAPI backend (`/rank` endpoint)
- Encapsulated scoring model for easy extension
- Unit tests for ranking logic
- Sample candidate dataset
- Documentation and CI workflow

---

## Architecture (high level)

- `src/parser.py` — parse raw candidate records into structured fields
- `models/model.py` — scoring & normalization logic
- `src/ranking.py` — orchestrates parse, match, and scoring
- `src/main.py` — CLI demo to print ranked candidates
- `backend/api.py` — FastAPI app exposing `/rank`
- `data/sample_candidates.csv` — sample data
- `tests/test_ranking.py` — unit tests
- `docs/architecture.md` — design + scalability notes

---

## Tech Stack

- Python 3.8+
- FastAPI, Uvicorn
- pandas
- scikit-learn (helpers)
- nltk (tokenization)
- pytest (testing)

---

## Quick Installation

1. Clone the repo:
   git clone https://github.com/<your-username>/ai-recruiter-ai-champs.git
   cd ai-recruiter-ai-champs

2. Create and activate a virtual environment:
   python -m venv venv
   source venv/bin/activate   # macOS / Linux
   venv\Scripts\activate      # Windows

3. Install dependencies:
   pip install -r requirements.txt

4. (Optional) Download NLTK data:
   python -c "import nltk; nltk.download('punkt')"

---

## Usage

CLI:
- Run: `python src/main.py`  
  Prints top-ranked candidates from the sample CSV.

API:
- Start server:
  `uvicorn backend.api:app --reload --port 8000`
- GET ranked candidates:
  `http://127.0.0.1:8000/rank`
- With skills:
  `http://127.0.0.1:8000/rank?skills=Python,TensorFlow,PyTorch`

POST JSON example:
```json
{
  "skills": ["Python", "Django"],
  "limit": 5
}
