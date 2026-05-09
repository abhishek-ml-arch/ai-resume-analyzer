#!/usr/bin/env fish

cd (dirname (status filename))

source venv/bin/activate.fish

# Start backend
cd backend
uvicorn app:app --reload &

sleep 5

# Start frontend
cd ../frontend
streamlit run streamlit_app.py
