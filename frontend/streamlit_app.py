import streamlit as st
import requests

st.set_page_config(
    page_title="AI Resume Analyzer",
    layout="wide"
)

st.title("AI Resume Analyzer")

st.markdown(
    "Analyze your resume against job descriptions using AI-powered semantic matching."
)

uploaded_file = st.file_uploader(
    "Upload Resume PDF",
    type=["pdf"]
)

job_description = st.text_area(
    "Paste Job Description",
    height=200
)

if st.button("Analyze Resume"):

    if uploaded_file is None:
        st.error("Please upload a resume PDF.")

    elif not job_description.strip():
        st.error("Please enter a job description.")

    else:

        with st.spinner("Analyzing Resume..."):

            try:

                response = requests.post(
                    "http://127.0.0.1:8000/analyze",
                    files={
                        "resume": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    },
                    data={
                        "job_description": job_description
                    }
                )

                result = response.json()

                if "error" in result:
                    st.error(result["error"])

                else:

                    st.success("Analysis Complete")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "ATS Score",
                            f"{result['ATS Score']}%"
                        )

                    with col2:
                        st.metric(
                            "Match Score",
                            result["Match Score"]
                        )

                    with col3:
                        st.metric(
                            "Resume Strength",
                            result["Resume Strength"]
                        )

                    st.progress(
                        int(result["ATS Score"])
                    )

                    st.subheader("Resume Skills")
                    st.write(result["Resume Skills"])

                    st.subheader("Job Description Skills")
                    st.write(result["Job Description Skills"])

                    st.subheader("Missing Skills")
                    st.write(result["Missing Skills"])

                    st.subheader("AI Recommendations")

                    for recommendation in result[
                        "Recommendations"
                    ]:
                        st.info(recommendation)

            except Exception as e:
                st.error(
                    f"Frontend Error: {str(e)}"
                )