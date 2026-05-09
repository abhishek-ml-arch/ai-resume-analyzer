#!/usr/bin/env fish

cd ~/Documents/"AI Resume Analyzer"

source venv/bin/activate.fish

# Backend
cd backend
uvicorn app:app --reload &

sleep 5

# Frontend
cd ../frontend
streamlit run streamlit_app.py