AI Champs - AI Recruiter Intelligent Ranking System

Challenge: AI & Data Challenge — AI Recruiter Intelligent Ranking System
Team: AI Champs
Team Leader: Vaibhav Kumar Tyagi

Overview

AI Recruiter Intelligent Ranking System is an extensible, production-ready starter repository that demonstrates an AI-powered recruitment pipeline. The system accepts candidate resumes (sample CSV provided), extracts structured attributes (skills and experience), scores candidates using a transparent scoring formula, and returns ranked candidates both via a CLI script and an API.

This repository is intended for hackathons, portfolio demos, and as a foundation for production extensions.

Features

Resume parsing (mock NLP with clear structure)
Skill matching against job requirements
Candidate scoring and ranking
Command-line example (src/main.py)
FastAPI backend with /rank endpoint
Encapsulated scoring model for easy extension
Unit tests for ranking logic
Realistic sample candidate CSV dataset
Documentation describing architecture and extensibility
Architecture (high level)

src/parser.py: Parses candidate records and extracts normalized fields.
models/model.py: Encapsulates the scoring formula and normalization logic.
src/ranking.py: Coordinates parsing and scoring, returns sorted candidates.
src/main.py: Example CLI that loads sample data, computes rankings, and prints results.
backend/api.py: FastAPI app exposing /rank endpoint to compute rankings on demand.
data/sample_candidates.csv: Sample dataset for experimentation.
tests/test_ranking.py: Basic unit test ensuring ranking correctness.
docs/architecture.md: Design and data flow details.
Tech Stack

Python 3.8+
FastAPI (API)
Uvicorn (ASGI server)
pandas (data handling)
scikit-learn (optional helpers)
nltk (tokenization / mock NLP)
pytest (testing)
Installation

Clone the repo git clone https://github.com/your-org/ai-recruiter-ai-champs.git cd ai-recruiter-ai-champs

Create a virtual environment (recommended) python -m venv venv source venv/bin/activate # mac/linux venv\Scripts\activate # windows

Install dependencies pip install -r requirements.txt

Note: nltk is included. If you plan to use advanced nltk tokenizers you may need to download data packages: python -c "import nltk; nltk.download('punkt')"

Usage

CLI Example

Run the main script to see sample ranking: python src/main.py

Output will print ranked candidates with computed score percentages.

API Example

Run the FastAPI server: uvicorn backend.api:app --reload --host 127.0.0.1 --port 8000

Open the API in your browser or use curl:

GET ranked candidates with default scoring (uses sample dataset): http://127.0.0.1:8000/rank

Provide job skills via query parameter (comma separated): http://127.0.0.1:8000/rank?skills=Python,TensorFlow,PyTorch

POST example (JSON): POST /rank with body: { "skills": ["Python","Django"], "max_experience_years": 15 }

Response: JSON list of candidates sorted by score.

Example output (CLI)

Top 5 Ranked Candidates:

Ananya Iyer — Score: 93.6% — Experience: 9.0 — Matched Skills: 6/7 — Skills Matched: 85.7%
Meera Krishnan — Score: 89.3% — Experience: 8.0 — Matched Skills: 5/6 — Skills Matched: 83.3%
Vikram Singh — Score: 83.2% — Experience: 6.0 — Matched Skills: 5/6 — Skills Matched: 83.3% ...etc
(Actual numeric values may vary slightly depending on normalization caps.)

Scoring Details

The current scoring formula (simple, explainable) is:

experience_score = normalize(experience_years, cap=10) -> 0..100
skills_score = (matched_skills / total_required_skills) * 100
Final score: score = (experience_score * 0.6) + (skills_score * 0.4)

This yields a final percentage (0..100). The design is intentionally modular so you can replace the model with ML-based ranking later.

Tests

Run tests with: pytest -q

Future Enhancements

Add semantic skill matching (embeddings / BERT) instead of keyword matching.
Add PDF / DOCX resume parsing and OCR.
Add candidate behavioral features (activity, intent, response rate).
Replace rule-based scoring with a trainable ranking model (LTR / pairwise learning).
Add authentication, role-based access, and multi-tenant support.
Add persistence layer (Postgres) and background workers for large-scale parsing.
License

MIT License © 2026 AI Champs

See LICENSE file for details.

Contact

Team AI Champs — Team Lead: Vaibhav Kumar Tyagi
