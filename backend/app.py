from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi import Form

from fastapi.responses import JSONResponse

from analyzer import (
    extract_skills,
    calculate_similarity,
    generate_recruiter_insight
)

from utils import extract_text_from_pdf

app = FastAPI()


@app.get("/")
def home():

    return {
        "message": "AI Resume Analyzer Backend Running"
    }


@app.post("/analyze")
async def analyze_resume(

    resume: UploadFile = File(...),

    job_description: str = Form(...)

):

    try:

        # -------------------------------------------------
        # FILE VALIDATION
        # -------------------------------------------------

        if resume.content_type != "application/pdf":

            return JSONResponse(
                status_code=400,
                content={
                    "error": "Only PDF resumes are allowed."
                }
            )

        pdf_bytes = await resume.read()

        if len(pdf_bytes) > 5 * 1024 * 1024:

            return JSONResponse(
                status_code=400,
                content={
                    "error": "PDF size exceeds 5MB limit."
                }
            )

        # -------------------------------------------------
        # EXTRACT TEXT
        # -------------------------------------------------

        resume_text = extract_text_from_pdf(
            pdf_bytes
        )

        if not resume_text:

            return JSONResponse(
                status_code=400,
                content={
                    "error": "No text found inside PDF."
                }
            )

        # -------------------------------------------------
        # SKILL EXTRACTION
        # -------------------------------------------------

        resume_skills = extract_skills(
            resume_text
        )

        jd_skills = extract_skills(
            job_description
        )

        matched_skills = list(
            set(resume_skills).intersection(
                set(jd_skills)
            )
        )

        missing_skills = list(
            set(jd_skills) - set(resume_skills)
        )

        # -------------------------------------------------
        # ATS SCORE
        # -------------------------------------------------

        ats_score = calculate_similarity(
            resume_text,
            job_description
        )

        # -------------------------------------------------
        # RESUME STRENGTH
        # -------------------------------------------------

        if ats_score >= 80:

            resume_strength = "Strong"

        elif ats_score >= 60:

            resume_strength = "Average"

        else:

            resume_strength = "Weak"

        # -------------------------------------------------
        # RECOMMENDATIONS
        # -------------------------------------------------

        recommendations = []

        for skill in missing_skills:

            recommendations.append(
                f"Consider adding projects or experience related to {skill.title()}."
            )

        if not recommendations:

            recommendations.append(
                "Excellent alignment detected for this role."
            )

        # -------------------------------------------------
        # RECRUITER INSIGHT
        # -------------------------------------------------

        recruiter_insight = generate_recruiter_insight(
            matched_skills,
            missing_skills,
            ats_score
        )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return {

            "ATS Score": ats_score,

            "Resume Strength": resume_strength,

            "Resume Skills": resume_skills,

            "Job Description Skills": jd_skills,

            "Matched Skills": matched_skills,

            "Missing Skills": missing_skills,

            "Recommendations": recommendations,

            "Recruiter Insight": recruiter_insight
        }

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )