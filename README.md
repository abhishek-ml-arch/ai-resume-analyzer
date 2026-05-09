# 🚀 AI Resume Analyzer

An AI-powered full-stack resume analysis platform that compares resumes against job descriptions using NLP embeddings, semantic similarity, and intelligent skill extraction.

This project combines:
- Natural Language Processing (NLP)
- Semantic AI Matching
- Resume Parsing
- FastAPI Backend APIs
- Streamlit Dashboard UI
- Interactive Visual Analytics

The system analyzes uploaded resumes against job descriptions and generates:
- ATS-style scores
- Skill matching analysis
- Missing skill detection
- AI recruiter insights
- Resume improvement recommendations

---

# 🌟 Project Preview

## Core Features

✅ AI Resume Matching  
✅ ATS Score Analysis  
✅ Semantic Similarity Matching  
✅ Dynamic Skill Extraction  
✅ Missing Skill Detection  
✅ AI Recruiter Insight Generation  
✅ Interactive Analytics Dashboard  
✅ Glassmorphism Dark UI  
✅ FastAPI Backend  
✅ Streamlit Frontend  
✅ PDF Resume Upload  
✅ Error Handling & Validation  

---

# 🧠 AI & NLP Technologies Used

## 1. Sentence Transformers

The project uses transformer-based sentence embeddings:

```python
sentence-transformers/all-MiniLM-L6-v2

2. Cosine Similarity

The similarity between:

Resume text
Job description

is calculated using:

sklearn.metrics.pairwise.cosine_similarity

This generates an ATS-style semantic match score.

3. NLP Skill Extraction

Skills are extracted dynamically using:

Regex matching
Configurable skill database
NLP preprocessing

The analyzer can identify:

Programming languages
AI/ML technologies
Backend frameworks
DevOps tools
Cloud platforms
Data tools
🎯 Example Workflow
Step 1 — Upload Resume

User uploads a resume PDF.

Step 2 — Paste Job Description

Example:

Looking for a Python developer with experience in FastAPI,
machine learning, Docker, SQL, NLP, and deep learning.
Step 3 — AI Analysis

The backend:

extracts PDF text
processes NLP embeddings
extracts skills
computes semantic similarity
generates recruiter insight
Step 4 — Dashboard Results

The frontend displays:

ATS Score
Resume Strength
Skill Match Analysis
Missing Skills
AI Recommendations
Recruiter Feedback
Visual Charts
🏗️ Project Architecture
AI Resume Analyzer/
│
├── backend/
│   ├── app.py
│   ├── analyzer.py
│   ├── config.py
│   ├── utils.py
│   └── requirements.txt
│
├── frontend/
│   └── streamlit_app.py
│
├── screenshots/
├── data/
│
├── requirements.txt
├── docker-compose.yml
├── run.fish
├── start.sh
└── README.md
⚙️ Backend Architecture
FastAPI Backend

The backend handles:

API routing
PDF uploads
validation
NLP analysis
semantic scoring
recruiter insight generation
JSON responses
Main API Endpoint
POST /analyze
Backend Components
app.py

Main FastAPI application.

Handles:

API routes
request validation
response formatting
error handling
analyzer.py

Core AI engine.

Handles:

semantic similarity
skill extraction
ATS scoring
recruiter insight generation
config.py

Centralized skill database.

Contains:

programming skills
AI/ML tools
cloud technologies
backend frameworks
DevOps tools
utils.py

Utility helper functions.

Handles:

PDF text extraction
reusable helper logic
🎨 Frontend Architecture
Streamlit Dashboard

The frontend provides:

modern dashboard UI
visual analytics
AI feedback panels
resume upload workflow
skill match visualizations
✨ UI Features
Glassmorphism Dashboard

Modern futuristic interface with:

dark gradients
translucent cards
glow effects
smooth layouts
AI-themed visuals
Dashboard Metrics

Displays:

ATS score
resume strength
matched skills
missing skills
Visual Analytics
ATS Gauge Chart

Visual representation of semantic alignment score.

Pie Chart

Displays:

matched skills
missing skills
Skill Match Progress Bars

Dynamic progress visualization for:

matched skills
missing skills
🔍 Skill Extraction System

The analyzer can identify skills such as:

Programming
Python
Java
JavaScript
SQL
TypeScript
AI / Machine Learning
Machine Learning
Deep Learning
NLP
TensorFlow
PyTorch
LangChain
Backend Development
FastAPI
Flask
Django
DevOps & Cloud
Docker
Kubernetes
AWS
Azure
GCP
Data & Analytics
Pandas
NumPy
Scikit-learn
Power BI
Tableau
📊 Example Output
ATS Score
ATS Score: 82.5%
Missing Skills
Missing Skills:
- Docker
- FastAPI
Recruiter Insight
The resume demonstrates strong alignment in Python,
machine learning, and NLP.

However, deployment-oriented backend skills such as
Docker and FastAPI remain underrepresented.
🚀 Installation Guide
1. Clone Repository
git clone https://github.com/abhishek-ml-arch/ai-resume-analyzer.git
2. Navigate Into Project
cd ai-resume-analyzer
3. Create Virtual Environment
Fish Shell
python -m venv venv
source venv/bin/activate.fish
Bash
python -m venv venv
source venv/bin/activate
4. Install Dependencies
pip install -r requirements.txt
▶️ Running The Project
Fish Shell
./run.fish
Bash
./start.sh
🧪 API Validation Features

The backend includes:

✅ PDF validation
✅ File size validation
✅ Backend error handling
✅ JSON-safe responses
✅ Frontend API failure handling

📈 Engineering Concepts Demonstrated

This project demonstrates:

Full-stack AI engineering
NLP embedding systems
Semantic similarity pipelines
FastAPI REST APIs
Streamlit dashboard engineering
Backend/frontend integration
Modular architecture
Error-safe APIs
Visualization systems
Recruiter-style AI analysis
Resume intelligence systems
🔥 Future Improvements

Planned upgrades include:

AI Improvements
Ollama integration
Local LLM recruiter feedback
OpenAI integration
LangChain pipelines
Vector databases
Backend Improvements
PostgreSQL database
Authentication system
Resume history tracking
Multi-user support
Docker deployment
Frontend Improvements
Real-time analytics
Animated dashboards
Resume heatmaps
Resume formatting analysis
NLP Improvements
OCR for scanned resumes
Advanced entity recognition
Dynamic skill extraction
Industry-specific scoring
📸 Screenshots

Place screenshots inside:

screenshots/

Example:

![Dashboard](screenshots/dashboard.png)
👨‍💻 Author
Abhishek

AI/ML enthusiast focused on:

AI engineering
NLP systems
autonomous AI tools
full-stack AI products
advanced software systems

GitHub:

https://github.com/abhishek-ml-arch
📜 License

MIT License

⭐ Final Notes

This project was built to explore:

AI-powered resume intelligence
semantic NLP systems
modern AI dashboards
full-stack AI application engineering

The system is designed to evolve into a production-grade AI recruiting assistant platform.