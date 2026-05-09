import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# GLOBAL CSS
# -------------------------------------------------

st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
        radial-gradient(circle at top left, #172554 0%, #020617 45%);
        color: white;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    section[data-testid="stSidebar"] {
        background: #050816;
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    .hero-title {
        font-size: 72px;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 12px;
    }

    .gradient-text {
        background: linear-gradient(90deg,#8b5cf6,#3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        font-size: 20px;
        color: rgba(255,255,255,0.7);
        margin-bottom: 25px;
    }

    .glass {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 24px;
        backdrop-filter: blur(14px);
        box-shadow: 0 10px 40px rgba(0,0,0,0.35);
    }

    .metric-card {
        background:
        linear-gradient(
            135deg,
            rgba(139,92,246,0.18),
            rgba(59,130,246,0.08)
        );

        border: 1px solid rgba(255,255,255,0.08);

        border-radius: 24px;

        padding: 25px;

        min-height: 170px;

        position: relative;

        overflow: hidden;
    }

    .metric-card::before {
        content: '';

        position: absolute;

        width: 220px;
        height: 220px;

        background:
        radial-gradient(
            circle,
            rgba(139,92,246,0.25),
            transparent 70%
        );

        top: -120px;
        right: -120px;
    }

    .metric-label {
        font-size: 14px;
        letter-spacing: 1px;
        opacity: 0.7;
        margin-bottom: 15px;
    }

    .metric-value {
        font-size: 48px;
        font-weight: 800;
    }

    textarea {
        background: rgba(255,255,255,0.03) !important;
        color: white !important;
        border-radius: 18px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }

    label {
        color: white !important;
        font-weight: 600 !important;
    }

    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.03);
        border: 1px dashed rgba(255,255,255,0.15);
        border-radius: 18px;
        padding: 20px;
    }

    .stButton > button {
        width: 100%;

        height: 58px;

        border-radius: 18px;

        border: none;

        background:
        linear-gradient(
            90deg,
            #8b5cf6,
            #3b82f6
        );

        color: white;

        font-size: 18px;

        font-weight: 700;

        transition: 0.3s;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 25px rgba(139,92,246,0.45);
    }

    .pill {
        display: inline-block;

        padding: 10px 18px;

        margin: 6px;

        border-radius: 999px;

        background:
        linear-gradient(
            90deg,
            rgba(139,92,246,0.18),
            rgba(59,130,246,0.18)
        );

        border: 1px solid rgba(255,255,255,0.08);

        font-size: 14px;
    }

    header {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

st.sidebar.markdown("# 🚀 AI Resume Analyzer")

st.sidebar.markdown("---")

st.sidebar.markdown("### Dashboard")
st.sidebar.markdown("### ATS Score")
st.sidebar.markdown("### Skill Match")
st.sidebar.markdown("### AI Feedback")
st.sidebar.markdown("### Resume Insights")

st.sidebar.markdown("---")

st.sidebar.info(
    "Improve your chances of getting shortlisted with AI-powered resume analysis."
)

# -------------------------------------------------
# HERO SECTION
# -------------------------------------------------

st.markdown(
    """
    <div class='hero-title'>
        AI Resume <span class='gradient-text'>Analyzer</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class='hero-subtitle'>
        Analyze your resume against job descriptions using semantic AI matching and NLP embeddings.
    </div>
    """,
    unsafe_allow_html=True
)
# -------------------------------------------------
# INPUTS
# -------------------------------------------------

left, right = st.columns(2)

with left:

    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Resume PDF",
        type=["pdf"]
    )

    st.markdown("</div>", unsafe_allow_html=True)

with right:

    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    job_description = st.text_area(
        "Paste Job Description",
        height=180
    )

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------
# BUTTON
# -------------------------------------------------

analyze = st.button("Analyze Resume")

# -------------------------------------------------
# ANALYSIS
# -------------------------------------------------

if analyze:

    if uploaded_file is None:

        st.error("Please upload a resume PDF")

    elif not job_description.strip():

        st.error("Please paste a job description")

    else:

        with st.spinner("Running AI Analysis..."):

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

                if response.status_code != 200:

                    st.error(
                        f"Backend Error: {response.status_code}"
                    )

                    try:

                        error_data = response.json()

                        if "error" in error_data:

                            st.error(error_data["error"])

                    except Exception:

                        st.error("Unknown backend error.")

                    st.stop()

                result = response.json()
                ats_score = result["ATS Score"]

                resume_strength = result["Resume Strength"]

                matched_skills = result["Matched Skills"]

                missing_skills = result["Missing Skills"]

                if "error" in result:

                    st.error(result["error"])

                    st.stop()

            except requests.exceptions.ConnectionError:

                st.error(
                    "Backend server is not running on port 8000."
                )

                st.stop()

            except Exception as e:

                st.error(f"Unexpected Error: {str(e)}")

                st.stop()

            # -------------------------------------------------
            # DASHBOARD METRICS
            # -------------------------------------------------

            st.markdown("## Dashboard Metrics")

            m1, m2, m3, m4 = st.columns(4)

            with m1:

                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>ATS SCORE</div>
                    <div class='metric-value'>{ats_score}%</div>
                </div>
                """, unsafe_allow_html=True)

            with m2:

                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>RESUME STRENGTH</div>
                    <div class='metric-value'>{resume_strength}</div>
                </div>
                """, unsafe_allow_html=True)

            with m3:

                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>MATCHED SKILLS</div>
                    <div class='metric-value'>{len(matched_skills)}</div>
                </div>
                """, unsafe_allow_html=True)

            with m4:

                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>MISSING SKILLS</div>
                    <div class='metric-value'>{len(missing_skills)}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # -------------------------------------------------
            # CHARTS
            # -------------------------------------------------

            c1, c2 = st.columns(2)

            with c1:

                gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=ats_score,
                    title={'text': "ATS Score"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': '#8b5cf6'},
                        'steps': [
                            {'range': [0, 50], 'color': '#ef4444'},
                            {'range': [50, 75], 'color': '#f59e0b'},
                            {'range': [75, 100], 'color': '#22c55e'}
                        ]
                    }
                ))

                gauge.update_layout(
                    paper_bgcolor="#020617",
                    font={'color': 'white'}
                )

                st.plotly_chart(
                    gauge,
                    use_container_width=True
                )

            with c2:

                pie_df = pd.DataFrame({
                    "Category": ["Matched", "Missing"],
                    "Count": [
                        len(matched_skills),
                        len(missing_skills)
                    ]
                })

                fig = px.pie(
                    pie_df,
                    names="Category",
                    values="Count",
                    hole=0.55
                )

                fig.update_layout(
                    paper_bgcolor="#020617",
                    font={'color': 'white'}
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            st.markdown("<br>", unsafe_allow_html=True)
            # -------------------------------------------------
            # SKILLS OVERVIEW
            # -------------------------------------------------

            st.markdown("## Skills Overview")

            s1, s2 = st.columns(2)

            with s1:

                st.markdown("### Matched Skills")

                for skill in matched_skills:

                    st.markdown(
                        f"<span class='pill'>{skill}</span>",
                        unsafe_allow_html=True
                    )

            with s2:

                st.markdown("### Missing Skills")

                for skill in missing_skills:

                    st.markdown(
                        f"<span class='pill'>{skill}</span>",
                        unsafe_allow_html=True
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            # -------------------------------------------------
            # SKILL MATCH ANALYSIS
            # -------------------------------------------------

            skill_scores = {}

            for skill in matched_skills:

                skill_scores[skill] = 90

            for skill in missing_skills:

                if skill not in skill_scores:

                    skill_scores[skill] = 35

            st.markdown("## Skill Match Analysis")

            for skill, score in skill_scores.items():

                st.markdown(
                    f"### {skill} — {score}%"
                )

                st.progress(score / 100)

            # -------------------------------------------------
            # RECRUITER INSIGHT
            # -------------------------------------------------

            st.markdown("## AI Recruiter Insight")

            st.info(
                result["Recruiter Insight"]
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # -------------------------------------------------
            # AI RECOMMENDATIONS
            # -------------------------------------------------

            st.markdown("## AI Recommendations")

            for rec in result["Recommendations"]:

                st.info(rec)

            # -------------------------------------------------
            # FINAL AI INSIGHT
            # -------------------------------------------------

            st.markdown("## Final AI Insight")

            if ats_score >= 80:

                st.success(
                    "Excellent alignment detected with the target role."
                )

            elif ats_score >= 60:

                st.warning(
                    "Good alignment detected, but stronger deployment "
                    "and backend engineering skills would improve the profile."
                )

            else:

                st.error(
                    "Significant resume improvements are recommended "
                    "for this role."
                )