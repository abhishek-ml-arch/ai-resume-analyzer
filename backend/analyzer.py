from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

SKILLS = [
    "python",
    "machine learning",
    "deep learning",
    "sql",
    "tensorflow",
    "pytorch",
    "data analysis",
    "nlp",
    "fastapi",
    "docker",
    "aws",
    "react",
    "git",
    "linux",
    "flask",
    "pandas",
    "numpy"
]


def extract_skills(text):
    text = text.lower()

    found = []

    for skill in SKILLS:
        if skill in text:
            found.append(skill)

    return found


def generate_recommendations(missing_skills):

    recommendations = []

    for skill in missing_skills:

        recommendations.append(
            f"Consider adding projects or experience related to {skill.title()}."
        )

    return recommendations


def calculate_resume_strength(score):

    if score >= 85:
        return "Excellent"

    elif score >= 70:
        return "Strong"

    elif score >= 50:
        return "Average"

    return "Weak"


def analyze_resume(
    resume_text,
    job_description
):

    if not resume_text.strip():
        return {
            "error": "No text found in resume PDF."
        }

    embeddings = model.encode([
        resume_text,
        job_description
    ])

    resume_embedding = np.array(
        embeddings[0]
    ).reshape(1, -1)

    jd_embedding = np.array(
        embeddings[1]
    ).reshape(1, -1)

    similarity = cosine_similarity(
        resume_embedding,
        jd_embedding
    )[0][0]

    ats_score = round(
        float(similarity) * 100,
        2
    )

    resume_skills = extract_skills(
        resume_text
    )

    jd_skills = extract_skills(
        job_description
    )

    missing_skills = list(
        set(jd_skills) - set(resume_skills)
    )

    recommendations = generate_recommendations(
        missing_skills
    )

    resume_strength = calculate_resume_strength(
        ats_score
    )

    return {
        "ATS Score": ats_score,
        "Match Score": f"{ats_score}%",
        "Resume Strength": resume_strength,
        "Resume Skills": resume_skills,
        "Job Description Skills": jd_skills,
        "Missing Skills": missing_skills,
        "Recommendations": recommendations
    }