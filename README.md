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

## Setup

```bash
# 1. Clone and enter project
git clone <your-repo-url>
cd ai-resume-analyzer

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run backend (in one terminal)
cd backend
uvicorn app:app --reload

# 5. Run frontend (in another terminal)
cd frontend
streamlit run streamlit_app.py
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
