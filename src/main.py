"""
main.py
Example CLI entrypoint which loads sample data, runs the ranking pipeline,
and prints results to stdout.
"""

import sys
from pathlib import Path
import pandas as pd

# ensure src imports work when running this file directly
sys.path.append(str(Path(__file__).parent.resolve()))

from ranking import rank_candidates

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_candidates.csv"


def load_sample_candidates(path: Path):
    """
    Load sample candidates from CSV into a list of dicts.
    """
    df = pd.read_csv(path)
    # normalize columns to expected names
    df = df.rename(columns=lambda c: c.strip())
    return df.to_dict(orient="records")


def print_ranked(ranked):
    """
    Nicely print top candidates.
    """
    print("\nTop Ranked Candidates:")
    for i, c in enumerate(ranked, start=1):
        print(
            f"{i}. {c['name']} — Score: {c['score']}% — Experience: {c['experience']} — "
            f"Matched Skills: {c['matched_count']}/{c['required_count']} — "
            f"Matched: {', '.join(c['matched_skills']) if c['matched_skills'] else 'None'}"
        )


def main():
    candidates = load_sample_candidates(DATA_PATH)
    # Example job skill set (could be taken from user input)
    job_skills = ["python", "tensorflow", "pytorch", "machine learning", "nlp"]
    ranked = rank_candidates(candidates, job_skills=job_skills)
    print_ranked(ranked[:10])  # print top 10


if __name__ == "__main__":
    main()
