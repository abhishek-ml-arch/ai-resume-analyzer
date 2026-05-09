import re

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config import SKILLS

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def extract_skills(text):

    text = text.lower()

    found_skills = []

    for skill in SKILLS:

        pattern = rf'\\b{re.escape(skill)}\\b'

        if re.search(pattern, text):
            found_skills.append(skill)

    return list(set(found_skills))


def calculate_similarity(resume_text, jd_text):

    embeddings = model.encode(
        [resume_text, jd_text]
    )

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    return float(round(similarity * 100, 2))


def generate_recruiter_insight(
    matched_skills,
    missing_skills,
    ats_score
):

    insight = (
        f"The resume demonstrates strength in "
        f"{', '.join(matched_skills[:5])}. "
    )

    if missing_skills:

        insight += (
            f"However, important missing skills include "
            f"{', '.join(missing_skills[:5])}. "
        )

    if ats_score >= 80:

        insight += (
            "Overall alignment with the target role is strong."
        )

    elif ats_score >= 60:

        insight += (
            "The profile shows moderate alignment but could "
            "benefit from stronger backend and deployment experience."
        )

    else:

        insight += (
            "The resume currently lacks strong alignment "
            "with the target role."
        )

    return insight