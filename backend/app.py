from fastapi import FastAPI, UploadFile, File, Form
from analyzer import analyze_resume
import fitz

app = FastAPI()


def extract_text_from_pdf(pdf_bytes):
    text = ""

    pdf = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    for page in pdf:
        text += page.get_text()

    return text


@app.get("/")
async def root():
    return {"message": "AI Resume Analyzer Backend Running"}


@app.post("/analyze")
async def analyze(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    try:
        pdf_bytes = await resume.read()

        resume_text = extract_text_from_pdf(
            pdf_bytes
        )

        result = analyze_resume(
            resume_text,
            job_description
        )

        return result

    except Exception as e:
        return {
            "error": str(e)
        }