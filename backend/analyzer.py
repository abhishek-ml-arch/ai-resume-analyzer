import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from config import SKILLS, STRENGTH_THRESHOLDS

# Loaded once at startup
model = SentenceTransformer("all-MiniLM-L6-v2")


def extract_skills(text: str) -> list:
    """Extract known skills from text using word-boundary regex matching."""
    # Normalize text: lowercase, collapse whitespace, remove special chars
    text = text.lower()
    text = re.sub(r'[^\w\s/#+]', ' ', text)  # keep / # + for c#, c++, ci/cd
    text = re.sub(r'\s+', ' ', text)

    found = []
    for skill in SKILLS:
        escaped = re.escape(skill)
        # Word boundary before first word, word boundary after last word
        pattern = rf'(?<!\w){escaped}(?!\w)'
        if re.search(pattern, text):
            found.append(skill)
    return found


def generate_recommendations(missing_skills: list) -> list:
    """Generate one actionable recommendation per missing skill."""
    return [
        f"Consider adding projects or experience related to {skill.title()}."
        for skill in missing_skills
    ]


def calculate_resume_strength(score: float) -> str:
    """Return a strength label based on configurable thresholds."""
    if score >= STRENGTH_THRESHOLDS["Excellent"]:
        return "Excellent"
    elif score >= STRENGTH_THRESHOLDS["Strong"]:
        return "Strong"
    elif score >= STRENGTH_THRESHOLDS["Average"]:
        return "Average"
    return "Weak"


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """Core analysis: semantic similarity + skill gap detection."""

    if not resume_text.strip():
        return {"error": "No text found in resume PDF. Make sure it is not a scanned image."}

    if not job_description.strip():
        return {"error": "Job description is empty."}

    # Semantic similarity via sentence embeddings
    embeddings = model.encode([resume_text, job_description])
    resume_embedding = np.array(embeddings[0]).reshape(1, -1)
    jd_embedding = np.array(embeddings[1]).reshape(1, -1)
    similarity = cosine_similarity(resume_embedding, jd_embedding)[0][0]
    ats_score = round(float(similarity) * 100, 2)

    # Skill extraction
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)
    missing_skills = list(set(jd_skills) - set(resume_skills))

    return {
        "ATS Score": ats_score,
        "Match Score": f"{ats_score}%",
        "Resume Strength": calculate_resume_strength(ats_score),
        "Resume Skills": resume_skills,
        "Job Description Skills": jd_skills,
        "Missing Skills": missing_skills,
        "Recommendations": generate_recommendations(missing_skills),
    }
