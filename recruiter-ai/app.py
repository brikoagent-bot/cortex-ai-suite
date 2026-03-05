"""
Cortex Recruiter AI — AI-Powered Hiring Pipeline
Resume screening, job description generation, interview questions
"""
import streamlit as st
import google.generativeai as genai
import json, re
from datetime import datetime

st.set_page_config(page_title="Cortex Recruiter AI | Hiring Pipeline", page_icon="💼", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; }
    .main-header { text-align: center; padding: 2rem 0; }
    .main-header h1 { font-size: 2.5rem; font-weight: 700; background: linear-gradient(135deg, #ec4899 0%, #f43f5e 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>💼 Cortex Recruiter AI</h1><p>AI-powered hiring pipeline — screen, evaluate, interview</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Settings")
    gemini_key = st.text_input("Google Gemini API Key", type="password")
    st.divider()
    st.markdown("### 💎 Cortex Pro")
    st.markdown("ATS integration, bulk screening, candidate ranking.")
    st.link_button("Upgrade — $149/mo", "https://buy.stripe.com/test_placeholder", use_container_width=True)

tab1, tab2, tab3 = st.tabs(["📝 Job Description", "📋 Resume Screener", "🎤 Interview Kit"])

with tab1:
    st.markdown("### Generate a Job Description")
    col1, col2 = st.columns(2)
    with col1:
        role_title = st.text_input("Role Title", placeholder="e.g. Senior Backend Engineer")
        company = st.text_input("Company", placeholder="e.g. Cortex AI")
        department = st.text_input("Department", placeholder="e.g. Engineering")
    with col2:
        seniority = st.selectbox("Seniority", ["Junior", "Mid-Level", "Senior", "Staff", "Principal", "Director", "VP"])
        location = st.text_input("Location", placeholder="e.g. Remote, NYC")
        salary_range = st.text_input("Salary Range (optional)", placeholder="e.g. $150K-$200K")

    tech_stack = st.text_input("Tech Stack / Key Skills", placeholder="e.g. Python, AWS, PostgreSQL, distributed systems")
    company_culture = st.text_area("Company Culture / Perks", placeholder="Describe your culture...", height=80)

    if st.button("📝 Generate JD", type="primary", disabled=not (gemini_key and role_title)):
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        with st.spinner("Writing job description..."):
            prompt = f"""Write a compelling job description for:
Role: {role_title} ({seniority}) at {company or 'a startup'}
Department: {department}, Location: {location}
Salary: {salary_range or 'Competitive'}
Tech/Skills: {tech_stack}
Culture: {company_culture or 'Fast-paced startup environment'}

Include: About the role, Responsibilities (5-7), Requirements (5-7), Nice-to-haves (3-4), Benefits, How to apply.
Make it engaging and inclusive. Avoid jargon. Use clear, direct language."""

            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.download_button("📥 Download JD", response.text, file_name=f"JD-{role_title.replace(' ','-')}.md")

with tab2:
    st.markdown("### Screen a Resume Against a Job")
    job_desc = st.text_area("📋 Paste Job Description", height=150, placeholder="Paste the JD here...")
    resume_text = st.text_area("📄 Paste Resume Text", height=200, placeholder="Paste the candidate's resume...")

    if st.button("🔍 Screen Resume", type="primary", disabled=not (gemini_key and job_desc and resume_text)):
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        with st.spinner("Screening..."):
            prompt = f"""You are a senior technical recruiter. Screen this resume against the job description.

JOB DESCRIPTION:
{job_desc[:3000]}

RESUME:
{resume_text[:3000]}

Return JSON:
{{
    "fit_score": <0-100>,
    "verdict": "<STRONG FIT|GOOD FIT|PARTIAL FIT|NOT A FIT>",
    "matching_skills": ["<skills that match>"],
    "missing_skills": ["<required skills not found>"],
    "experience_match": "<assessment of experience level>",
    "strengths": ["<candidate strengths for this role>"],
    "concerns": ["<red flags or concerns>"],
    "interview_recommendation": "<yes/no with reasoning>",
    "suggested_questions": ["<3 targeted interview questions based on gaps>"]
}}
Return ONLY valid JSON."""

            response = model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```"): text = re.sub(r'^```json?\n?', '', re.sub(r'\n?```$', '', text))
            data = json.loads(text)

        score = data.get("fit_score", 0)
        color = "#10b981" if score >= 70 else "#f59e0b" if score >= 50 else "#ef4444"

        st.markdown(f"""
        <div style="text-align:center;padding:1.5rem;background:#f8f9fa;border-radius:12px;">
            <div style="font-size:3rem;font-weight:800;color:{color};">{score}%</div>
            <div style="font-size:1.2rem;color:#374151;">{data.get('verdict','')}</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### ✅ Matching Skills")
            for s in data.get("matching_skills", []): st.markdown(f"- ✅ {s}")
            st.markdown("### 💪 Strengths")
            for s in data.get("strengths", []): st.markdown(f"- {s}")
        with col2:
            st.markdown("### ❌ Missing Skills")
            for s in data.get("missing_skills", []): st.markdown(f"- ❌ {s}")
            st.markdown("### ⚠️ Concerns")
            for c in data.get("concerns", []): st.markdown(f"- ⚠️ {c}")

        st.markdown(f"### 🎤 Interview Recommendation\n{data.get('interview_recommendation', '')}")
        st.markdown("### Suggested Questions")
        for q in data.get("suggested_questions", []): st.markdown(f"- ❓ {q}")

with tab3:
    st.markdown("### Generate Interview Kit")
    interview_role = st.text_input("Role", placeholder="e.g. Senior Frontend Engineer", key="int_role")
    interview_skills = st.text_input("Key Skills to Assess", placeholder="e.g. React, system design, leadership")
    interview_type = st.selectbox("Interview Type", ["Technical", "Behavioral", "System Design", "Culture Fit", "Mixed"])
    num_questions = st.slider("Number of Questions", 3, 15, 8)

    if st.button("🎤 Generate Kit", type="primary", disabled=not (gemini_key and interview_role)):
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        with st.spinner("Creating interview kit..."):
            prompt = f"""Create a {interview_type} interview kit for {interview_role}.
Skills to assess: {interview_skills}
Generate {num_questions} questions.

Return JSON:
{{
    "role": "{interview_role}",
    "type": "{interview_type}",
    "questions": [
        {{
            "question": "<the question>",
            "category": "<technical|behavioral|design|culture>",
            "difficulty": "<easy|medium|hard>",
            "what_to_look_for": "<ideal answer signals>",
            "red_flags": "<what bad answers look like>",
            "follow_ups": ["<follow-up questions>"]
        }}
    ],
    "scorecard": [
        {{"criteria": "<what to evaluate>", "weight": "<1-5>"}}
    ]
}}
Return ONLY valid JSON."""

            response = model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```"): text = re.sub(r'^```json?\n?', '', re.sub(r'\n?```$', '', text))
            data = json.loads(text)

        for i, q in enumerate(data.get("questions", []), 1):
            diff_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(q.get("difficulty", ""), "⚪")
            with st.expander(f"{diff_emoji} Q{i}: {q.get('question', '')}", expanded=(i <= 3)):
                st.markdown(f"**Category:** {q.get('category', '')} | **Difficulty:** {q.get('difficulty', '')}")
                st.markdown(f"**Look for:** {q.get('what_to_look_for', '')}")
                st.markdown(f"**Red flags:** {q.get('red_flags', '')}")
                if q.get("follow_ups"):
                    st.markdown("**Follow-ups:**")
                    for f in q["follow_ups"]: st.markdown(f"  - {f}")

        st.markdown("### 📊 Scorecard")
        for s in data.get("scorecard", []):
            st.markdown(f"- {s.get('criteria', '')} (Weight: {'⭐' * int(s.get('weight', 1))})")

        st.download_button("📥 Download Kit", json.dumps(data, indent=2),
                          file_name=f"interview-kit-{interview_role.replace(' ','-')}.json")

st.markdown("---")
st.markdown("*Cortex Recruiter AI — [Cortex AI Suite](/) • Powered by Gemini*")
