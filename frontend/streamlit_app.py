"""
AI Resume Analyzer — Frontend
Enterprise-style UI; analysis calls FastAPI on port 8000 (unchanged contract).
"""
from __future__ import annotations

import html
import time
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
# STATIC CONSTANTS (never recomputed across reruns)
# ═══════════════════════════════════════════════════════════════
_CSS_CACHE_KEY = "_css_injected"

HERO_HTML: str = """
<div class="saas-hero">
<div class="saas-hero-badge"><span class="saas-hero-badge-dot"></span>Semantic resume review</div>
<h1 class="saas-hero-title">AI Resume <em>Analyzer</em></h1>
<p class="saas-hero-sub">Upload a PDF resume and paste the target job description.
You get ATS-style scoring, skill coverage, and concise recommendations — without leaving this workspace.</p>
<div class="saas-hero-meta"><span>ATS-style score</span><span>Skill gaps</span><span>Actionable tips</span></div>
</div>
"""

API_URL = "http://127.0.0.1:8000/analyze"
API_TIMEOUT = 120
API_RETRY_DELAY = 1.5
API_MAX_RETRIES = 1

_RESULT_KEYS = frozenset(
    ("ATS Score", "Resume Skills", "Missing Skills", "Resume Strength", "Recommendations")
)

NAV_ITEMS = [
    ("dashboard", "Dashboard"),
    ("score", "ATS & metrics"),
    ("skills", "Skill match"),
    ("insights", "Charts"),
    ("feedback", "AI guidance"),
]

PAGE_COPY = {
    "dashboard": ("Workspace", "Upload a resume, add a job description, and run analysis."),
    "score": ("ATS & metrics", "Score, KPIs, and headline match quality."),
    "skills": ("Skill match", "Matched vs missing skills and per-skill signal."),
    "insights": ("Charts", "Gauge and distribution for quick scanning."),
    "feedback": ("AI guidance", "Narrative summary and actionable recommendations."),
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def _h(text: object) -> str:
    """Escape text embedded in unsafe_allow_html markdown."""
    return html.escape(str(text), quote=True)


def _inject_css_once() -> None:
    """Read & inject styles.css exactly once per session, caching contents."""
    if _CSS_CACHE_KEY not in st.session_state:
        css_path = Path(__file__).resolve().parent / "styles.css"
        if css_path.is_file():
            st.session_state[_CSS_CACHE_KEY] = css_path.read_text(encoding="utf-8")
        else:
            st.session_state[_CSS_CACHE_KEY] = ""
            st.error("Missing styles.css next to streamlit_app.py.")
            return
    css = st.session_state[_CSS_CACHE_KEY]
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def _validate_analysis_payload(data: object) -> str | None:
    """Return error message if payload is unusable; else None."""
    if not isinstance(data, dict):
        return "Invalid response: expected a JSON object."
    missing = _RESULT_KEYS - data.keys()
    if missing:
        return f"Invalid response: missing {', '.join(sorted(missing))}."
    if not isinstance(data.get("Resume Skills"), (list, tuple)):
        return "Invalid response: Resume Skills must be a list."
    if not isinstance(data.get("Missing Skills"), (list, tuple)):
        return "Invalid response: Missing Skills must be a list."
    if not isinstance(data.get("Recommendations"), (list, tuple)):
        return "Invalid response: Recommendations must be a list."
    try:
        float(data["ATS Score"])
    except (TypeError, ValueError):
        return "Invalid response: ATS Score must be numeric."
    return None


def _render_section_header(title: str) -> None:
    """Render a consistent section header with decorative line."""
    st.markdown(
        f'<div class="saas-sec"><span class="saas-sec-title">{_h(title)}</span>'
        '<span class="saas-sec-line"></span></div>',
        unsafe_allow_html=True,
    )


def _spacer() -> None:
    st.markdown('<div class="saas-sp-3"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# CHART THEME (centralized layout for all Plotly figures)
# ═══════════════════════════════════════════════════════════════
CHART_LAYOUT_DEFAULTS: dict[str, Any] = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font={"color": "rgba(250,250,250,0.55)", "size": 11, "family": "Inter"},
    margin={"l": 10, "r": 10, "t": 36, "b": 12},
    height=200,
    autosize=False,
)

CHART_CONFIG = {"displayModeBar": False}


def _apply_chart_layout(fig: go.Figure) -> go.Figure:
    """Apply the shared dark-theme layout to any Plotly figure."""
    fig.update_layout(**CHART_LAYOUT_DEFAULTS)
    return fig


# ═══════════════════════════════════════════════════════════════
# API CLIENT (extracted from inline rendering)
# ═══════════════════════════════════════════════════════════════
def _call_analyze_api(resume_file, job_description: str) -> dict:
    """POST the resume + job description to the FastAPI backend.
    Returns parsed JSON dict.  Raises on network / timeout / parse errors.
    """
    last_exc: Exception | None = None
    for attempt in range(API_MAX_RETRIES + 1):
        try:
            response = requests.post(
                API_URL,
                files={"resume": (resume_file.name, resume_file.getvalue(), "application/pdf")},
                data={"job_description": job_description},
                timeout=API_TIMEOUT,
            )
            if response.status_code == 200:
                try:
                    return response.json()  # type: ignore[no-any-return]
                except ValueError:
                    raise RuntimeError("Server returned a non-JSON response. Check API logs.")
            # Non-200: try to extract error detail
            try:
                err = response.json().get("error", "Unknown")
            except ValueError:
                err = (response.text or "Unknown").strip()[:500] or "Unknown"
            raise RuntimeError(f"Backend error ({response.status_code}): {err}")
        except requests.exceptions.Timeout as e:
            last_exc = e
            if attempt < API_MAX_RETRIES:
                time.sleep(API_RETRY_DELAY)
                continue
            raise RuntimeError(
                "Request timed out. The model or PDF may be large — try again or increase server resources."
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(
                "Cannot reach the API. Start the stack (e.g. <code>python start.py</code>) "
                "so FastAPI is listening on port 8000."
            ) from e
        except requests.exceptions.RequestException as e:
            last_exc = e
            if attempt < API_MAX_RETRIES:
                time.sleep(API_RETRY_DELAY)
                continue
            raise RuntimeError(f"Network error: {e}") from e
        except RuntimeError:
            raise  # re-raise our own
    raise RuntimeError(f"Unexpected: {last_exc}")


# ═══════════════════════════════════════════════════════════════
# RESULT SECTIONS (backend JSON shape unchanged)
# ═══════════════════════════════════════════════════════════════
def _ats_block(result: dict) -> None:
    ats = round(float(result["ATS Score"]), 1)
    verdict_class = "excellent" if ats >= 80 else "good" if ats >= 60 else "poor"
    verdict_text = "Strong match" if ats >= 80 else "Moderate match" if ats >= 60 else "Needs improvement"
    st.markdown(
        f"""
        <div class="saas-ats">
            <div class="saas-ats-score">{ats:.1f}%</div>
            <div class="saas-ats-label">ATS score</div>
            <div class="saas-ats-verdict {verdict_class}">{verdict_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _metrics_row(result: dict) -> None:
    matched = result["Resume Skills"]
    missing = result["Missing Skills"]
    strength = _h(result["Resume Strength"])
    m1, m2, m3, m4 = st.columns(4, gap="medium")
    blocks = [
        ("Strength", strength, "Overall signal"),
        ("Matched", str(len(matched)), "Aligned skills"),
        ("Missing", str(len(missing)), "Gaps vs JD"),
        ("Total", str(len(matched) + len(missing)), "Skills compared"),
    ]
    for col, (lab, val, sub) in zip((m1, m2, m3, m4), blocks):
        with col:
            st.markdown(
                f"""<div class="saas-mcard"><div class="saas-mcard-label">{lab}</div>
                <div class="saas-mcard-value">{val}</div><div class="saas-mcard-sub">{sub}</div></div>""",
                unsafe_allow_html=True,
            )


def _ai_insights(result: dict) -> None:
    matched = result["Resume Skills"]
    missing = result["Missing Skills"]
    if matched and missing:
        matched_str = ", ".join(_h(s.title()) for s in matched[:4])
        missing_str = ", ".join(_h(s.title()) for s in missing[:4])
        body = (
            f'<div class="saas-ai-block"><div class="saas-ai-block-title">Summary</div>'
            f"Your resume aligns on <strong>{matched_str}</strong>. Skills from the posting not surfaced on the resume include "
            f"<strong>{missing_str}</strong>. Tighten wording and evidence where you have adjacent experience.</div>"
        )
    elif matched and not missing:
        body = """<div class="saas-ai-block"><div class="saas-ai-block-title">Summary</div>
            <strong>Strong coverage</strong> — listed skills map cleanly to the job description.</div>"""
    else:
        body = """<div class="saas-ai-block"><div class="saas-ai-block-title">Summary</div>
            Few recognizable skills were extracted. Add explicit tools, methods, and keywords from the posting.</div>"""
    st.markdown(
        f"""
        <div class="saas-ai-panel"><div class="saas-ai-panel-hdr">
            <div class="saas-ai-icon">◇</div><div><div class="saas-ai-title">Analysis</div>
            <div class="saas-ai-sub">Semantic match vs job description</div></div></div>
            <div class="saas-ai-body">{body}</div></div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _build_gauge_chart(ats: float) -> go.Figure:
    """Build the ATS gauge figure (cached so it survives reruns unchanged)."""
    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=ats,
            title={
                "text": "ATS score",
            },
            number={"suffix": "%"},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "rgba(255,255,255,0.06)", "ticks": ""},
                "bar": {"color": "#a1a1aa", "thickness": 0.55},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": "rgba(248,113,113,0.22)"},
                    {"range": [50, 75], "color": "rgba(250,204,21,0.15)"},
                    {"range": [75, 100], "color": "rgba(74,222,128,0.18)"},
                ],
            },
        )
    )
    return gauge


@st.cache_data(show_spinner=False)
def _build_donut_chart(matched: tuple, missing: tuple) -> go.Figure:
    """Build the skill donut chart (cached by skill-set identity)."""
    total = len(matched) + len(missing)
    pie_df = pd.DataFrame(
        {"Status": ["Matched", "Missing"], "Count": [len(matched), len(missing)]}
    )
    fig = px.pie(
        pie_df,
        names="Status",
        values="Count",
        hole=0.58,
        color_discrete_sequence=["#4ade80", "#f87171"],
    )
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.05, xanchor="center", x=0.5),
        annotations=[
            {
                "text": f"{total}<br><span style='font-size:11px;color:rgba(250,250,250,0.4)'>skills</span>",
                "x": 0.5,
                "y": 0.5,
                "font": {"size": 13, "color": "#fafafa", "family": "Inter"},
                "showarrow": False,
            }
        ],
    )
    return fig


def _charts(result: dict) -> None:
    ats = round(float(result["ATS Score"]), 1)
    matched = tuple(result["Resume Skills"])
    missing = tuple(result["Missing Skills"])

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        try:
            gauge = _build_gauge_chart(ats)
            gauge = _apply_chart_layout(gauge)
            st.plotly_chart(gauge, use_container_width=True, config=CHART_CONFIG)
        except Exception:
            st.markdown(
                '<div class="saas-chart-empty">Unable to render gauge chart.</div>',
                unsafe_allow_html=True,
            )

    with c2:
        if len(matched) + len(missing) == 0:
            st.markdown(
                '<p class="saas-chart-empty">No skills to chart yet.</p>',
                unsafe_allow_html=True,
            )
        else:
            try:
                fig = _build_donut_chart(matched, missing)
                fig = _apply_chart_layout(fig)
                st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
            except Exception:
                st.markdown(
                    '<div class="saas-chart-empty">Unable to render skill donut.</div>',
                    unsafe_allow_html=True,
                )


def _skills_section(result: dict) -> None:
    matched = result["Resume Skills"]
    missing = result["Missing Skills"]
    s1, s2 = st.columns(2, gap="medium")
    with s1:
        if matched:
            pills = '<div class="saas-pill-row">' + "".join(
                f"<span class='saas-pill saas-pill-ok'>{_h(s)}</span>" for s in matched
            ) + "</div>"
        else:
            pills = '<div class="saas-pill-row"><span class="saas-pill">No matches</span></div>'
        st.markdown(
            f"""<div class="saas-scard"><div class="saas-scard-hdr"><span class="saas-scard-title">Matched</span>
            <span class="saas-scard-badge">{len(matched)}</span></div>{pills}</div>""",
            unsafe_allow_html=True,
        )
    with s2:
        if missing:
            pills = '<div class="saas-pill-row">' + "".join(
                f"<span class='saas-pill saas-pill-bad'>{_h(s)}</span>" for s in missing
            ) + "</div>"
        else:
            pills = '<div class="saas-pill-row"><span class="saas-pill saas-pill-ok">None — full coverage</span></div>'
        st.markdown(
            f"""<div class="saas-scard"><div class="saas-scard-hdr"><span class="saas-scard-title">Missing</span>
            <span class="saas-scard-badge">{len(missing)}</span></div>{pills}</div>""",
            unsafe_allow_html=True,
        )


def _skill_breakdown(result: dict) -> None:
    matched = result["Resume Skills"]
    missing = result["Missing Skills"]
    rows: list[str] = []
    for skill in list(matched) + list(missing):
        score = 90 if skill in matched else 20
        cls = "h" if score >= 50 else "l"
        sn = _h(str(skill).title())
        rows.append(
            f"""<div class="saas-pitem"><div class="saas-phdr"><span class="saas-pname">{sn}</span>
            <span class="saas-pscore saas-pscore-{cls}">{score}%</span></div>
            <div class="saas-ptrack"><div class="saas-pfill saas-pfill-{cls}" style="width:{score}%"></div></div></div>"""
        )
    st.markdown(f'<div class="saas-pcard">{"".join(rows)}</div>', unsafe_allow_html=True)


def _recommendations(result: dict) -> None:
    recs = result["Recommendations"]
    if recs:
        for rec in recs:
            st.markdown(f'<div class="saas-rcard">{_h(rec)}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="saas-toast-ok">No extra recommendations — alignment already looks solid.</div>',
            unsafe_allow_html=True,
        )


def render_results_for_page(page: str, result: dict) -> None:
    """Route sidebar page to sections; dashboard shows the full story."""
    if page == "dashboard":
        _render_section_header("ATS match")
        _ats_block(result)
        _spacer()
        _render_section_header("Overview")
        _metrics_row(result)
        _spacer()
        _render_section_header("Analysis")
        _ai_insights(result)
        _spacer()
        _render_section_header("Charts")
        _charts(result)
        _spacer()
        _render_section_header("Skills")
        _skills_section(result)
        _spacer()
        _render_section_header("Skill breakdown")
        _skill_breakdown(result)
        _spacer()
        _render_section_header("Recommendations")
        _recommendations(result)
        return

    if page == "score":
        _render_section_header("ATS match")
        _ats_block(result)
        _spacer()
        _render_section_header("Overview")
        _metrics_row(result)
        return

    if page == "skills":
        _render_section_header("Skills")
        _skills_section(result)
        _spacer()
        _render_section_header("Skill breakdown")
        _skill_breakdown(result)
        return

    if page == "insights":
        _render_section_header("Charts")
        _charts(result)
        return

    if page == "feedback":
        _render_section_header("Analysis")
        _ai_insights(result)
        _spacer()
        _render_section_header("Recommendations")
        _recommendations(result)


# ═══════════════════════════════════════════════════════════════
# INIT
# ═══════════════════════════════════════════════════════════════
_inject_css_once()

# ═══════════════════════════════════════════════════════════════
# SESSION
# ═══════════════════════════════════════════════════════════════
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        '<div class="sb-brand"><div class="sb-eyebrow">Workspace</div>'
        '<div class="sb-wordmark">Resume <span class="wl">/</span> Analyzer</div></div>',
        unsafe_allow_html=True,
    )
    for pid, label in NAV_ITEMS:
        active = st.session_state.page == pid
        if st.button(
            label,
            key=f"nav_{pid}",
            use_container_width=True,
            type="primary" if active else "secondary",
        ):
            st.session_state.page = pid
    if st.session_state.analysis_result is not None:
        if st.button("Clear last results", key="clear_analysis", use_container_width=True):
            st.session_state.analysis_result = None
            st.rerun()
    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    st.markdown(
        '<div class="sb-footer"><div class="sb-tagline">Semantic scoring via sentence-transformers embeddings. '
        "Runs locally against your FastAPI service.</div></div>",
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
_valid_pages = {p for p, _ in NAV_ITEMS}
if st.session_state.page not in _valid_pages:
    st.session_state.page = "dashboard"

page = st.session_state.page
title, desc = PAGE_COPY.get(page, PAGE_COPY["dashboard"])

if page == "dashboard":
    st.markdown(HERO_HTML, unsafe_allow_html=True)

    left, right = st.columns(2, gap="medium")
    with left:
        st.markdown(
            '<div class="saas-card saas-upload-zone">'
            '<div class="saas-card-hdr"><div class="saas-card-icon">▤</div>'
            '<span class="saas-card-label">Resume (PDF)</span></div>',
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="hidden", key="resume_uploader")
        st.markdown(
            '<div class="saas-card-hint">Text-based PDF · typical limit 5MB (server-dependent)</div></div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            '<div class="saas-card saas-jd-zone">'
            '<div class="saas-card-hdr"><div class="saas-card-icon">≡</div>'
            '<span class="saas-card-label">Job description</span></div>',
            unsafe_allow_html=True,
        )
        job_description = st.text_area(
            "",
            placeholder="Paste the full job description for best keyword and semantic coverage…",
            label_visibility="hidden",
            height=120,
            key="jd_input",
        )
        st.markdown('<div class="saas-card-hint">Include responsibilities, tools, and must-have skills.</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="saas-cta-wrap">', unsafe_allow_html=True)
    analyze = st.button("Analyze resume", use_container_width=True, key="analyze_btn")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="saas-sp-3"></div>', unsafe_allow_html=True)
    if not st.session_state.analysis_result and not analyze:
        st.markdown(
            '<p class="saas-dash-hint">Results appear here after a successful run. Use the sidebar to jump between sections.</p>',
            unsafe_allow_html=True,
        )

else:
    st.markdown(
        f'<div class="saas-page-head"><h2 class="saas-page-title">{title}</h2><p class="saas-page-desc">{desc}</p></div>',
        unsafe_allow_html=True,
    )

# ─── Run analysis (only from dashboard CTA) ───────────────────
if page == "dashboard" and analyze:
    if not uploaded_file:
        st.markdown(
            '<div class="saas-rcard">Upload a PDF resume before running analysis.</div>',
            unsafe_allow_html=True,
        )
    elif not job_description.strip():
        st.markdown(
            '<div class="saas-rcard">Add a job description so the model can compare against the posting.</div>',
            unsafe_allow_html=True,
        )
    else:
        with st.spinner("Analyzing resume…"):
            try:
                result = _call_analyze_api(uploaded_file, job_description)
            except RuntimeError as e:
                st.markdown(f'<div class="saas-rcard">{_h(e)}</div>', unsafe_allow_html=True)
                st.stop()
            except Exception as e:
                st.markdown(f'<div class="saas-rcard">Request error: {_h(e)}</div>', unsafe_allow_html=True)
                st.stop()

            if "error" in result:
                st.markdown(
                    f'<div class="saas-rcard">Analysis failed: {_h(result["error"])}</div>',
                    unsafe_allow_html=True,
                )
                st.stop()

        bad = _validate_analysis_payload(result)
        if bad:
            st.markdown(f'<div class="saas-rcard">{_h(bad)}</div>', unsafe_allow_html=True)
            st.stop()

        st.session_state.analysis_result = result
        st.rerun()

# ─── Persisted results ─────────────────────────────────────────
result = st.session_state.analysis_result
if result is not None:
    # Validate once — if bad, nuke it so we don't re-display garbage.
    bad = _validate_analysis_payload(result)
    if bad:
        st.session_state.analysis_result = None
        result = None
        st.warning(bad)

if result:
    render_results_for_page(page, result)
elif page != "dashboard":
    st.markdown(
        '<div class="saas-empty">Run an analysis from <strong>Dashboard</strong> to populate this section.</div>',
        unsafe_allow_html=True,
    )