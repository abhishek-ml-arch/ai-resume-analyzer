#!/bin/bash

echo "Starting AI Resume Analyzer..."

# Activate virtual environment
source venv/bin/activate

# Start backend
cd backend
uvicorn app:app --reload &

# Wait a little
sleep 5

# Start frontend
cd ../frontend
streamlit run streamlit_app.py