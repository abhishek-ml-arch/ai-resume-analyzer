# 🚀 AI Resume Analyzer

Analyze your resume against any job description using semantic AI matching and NLP skill extraction.

## What It Does
- Computes an ATS match score using sentence embeddings (cosine similarity)
- Extracts 50+ skills from both resume and job description
- Shows matched vs missing skills
- Gives dynamic recommendations based on actual results

## Tech Stack
- **Backend:** FastAPI + sentence-transformers + PyMuPDF
- **Frontend:** Streamlit + Plotly
- **AI Model:** all-MiniLM-L6-v2

## Quick Start

```bash
# One command to rule them all
python start.py

# That's it. The launcher handles:
#   • Creating a Python virtual environment (if needed)
#   • Installing all dependencies
#   • Starting the backend (FastAPI on port 8000)
#   • Starting the frontend (Streamlit on port 8501)
#   • Streaming logs in real time
```

## Usage
1. Open http://localhost:8501 in your browser
2. Upload your resume as a PDF
3. Paste the job description
4. Click **Analyze Resume**

## Notes
- Resume must be a text-based PDF (not a scanned image)
- Maximum file size: 5MB
- Backend runs on port 8000, frontend on port 8501
- Press **Ctrl+C** to stop all services
- Fully compatible with Arch Linux / CachyOS