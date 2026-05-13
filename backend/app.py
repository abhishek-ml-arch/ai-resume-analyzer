from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from analyzer import analyze_resume
from utils import extract_text_from_pdf
from config import MAX_FILE_SIZE_BYTES, ALLOWED_CONTENT_TYPE

app = FastAPI(title="AI Resume Analyzer API")


@app.get("/")
async def root():
    return {"message": "AI Resume Analyzer Backend Running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    try:
        # --- Validation ---
        if resume.content_type != ALLOWED_CONTENT_TYPE:
            return JSONResponse(
                status_code=400,
                content={"error": "Only PDF files are accepted."}
            )

        pdf_bytes = await resume.read()

        if len(pdf_bytes) > MAX_FILE_SIZE_BYTES:
            return JSONResponse(
                status_code=400,
                content={"error": "File too large. Maximum size is 5MB."}
            )

        if not job_description.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Job description cannot be empty."}
            )

        # --- Processing ---
        resume_text = extract_text_from_pdf(pdf_bytes)
        result = analyze_resume(resume_text, job_description)

        # Propagate analysis-level errors
        if "error" in result:
            return JSONResponse(status_code=422, content=result)

        return result

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )