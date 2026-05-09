SKILLS = [
    # Languages
    "python", "java", "javascript", "typescript", "r", "c++", "c#", "go", "rust", "scala",

    # ML / AI
    "machine learning", "deep learning", "nlp", "computer vision", "reinforcement learning",
    "mlops", "langchain", "huggingface", "llm", "transformers", "xgboost", "random forest",

    # Frameworks / Libraries
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "opencv",
    "fastapi", "flask", "django", "react", "streamlit",

    # Data & Databases
    "sql", "postgresql", "mongodb", "redis", "mysql", "sqlite", "hadoop", "spark",
    "data analysis", "data visualization", "tableau", "power bi", "excel",

    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "linux", "git",
    "airflow", "celery",
]

# ATS Score thresholds
STRENGTH_THRESHOLDS = {
    "Excellent": 85,
    "Strong": 70,
    "Average": 50,
}

# File validation
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_CONTENT_TYPE = "application/pdf"
