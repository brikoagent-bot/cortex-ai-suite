"""
Cortex Email GTM — AI-Powered Cold Email Campaign Generator
Creates personalized outreach sequences for GTM teams
"""
import streamlit as st
import google.generativeai as genai
import json, re, csv, io
from datetime import datetime

st.set_page_config(page_title="Cortex Email GTM | AI Outreach", page_icon="📧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; }
    .main-header { text-align: center; padding: 2rem 0; }
    .main-header h1 { font-size: 2.5rem; font-weight: 700; background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>📧 Cortex Email GTM</h1><p>AI-powered cold email campaigns that convert</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Settings")
    gemini_key = st.text_input("Google Gemini API Key", type="password")
    st.divider()
    st.markdown("### 💎 Cortex Pro")
    st.markdown("Unlimited campaigns, A/B testing, send scheduling.")
    st.link_button("Upgrade — $79/mo", "https://buy.stripe.com/test_placeholder", use_container_width=True)

tab1, tab2 = st.tabs(["🎯 Single Prospect", "📋 Bulk Campaign"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        your_company = st.text_input("🏢 Your Company", placeholder="e.g. Cortex AI")
        your_product = st.text_input("📦 Your Product/Service", placeholder="e.g. AI-powered SEO audits")
        your_value_prop = st.text_area("💡 Value Proposition", placeholder="We help companies increase organic traffic by 3x...", height=80)
    with col2:
        prospect_name = st.text_input("👤 Prospect Name", placeholder="e.g. Sarah Chen")
        prospect_title = st.text_input("💼 Prospect Title", placeholder="e.g. VP of Marketing")
        prospect_company = st.text_input("🎯 Prospect Company", placeholder="e.g. Shopify")

    tone = st.select_slider("Tone", options=["Very Casual", "Casual", "Professional", "Formal", "Very Formal"], value="Professional")
    sequence_length = st.slider("Email Sequence Length", 1, 5, 3)

    generate_single = st.button("📧 Generate Email Sequence", type="primary", use_container_width=True,
                                disabled=not (gemini_key and your_company and prospect_company))

    if generate_single:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        with st.spinner("Crafting personalized emails..."):
            prompt = f"""You are an expert cold email copywriter. Create a {sequence_length}-email outreach sequence.

SENDER: {your_company} — {your_product}
VALUE PROP: {your_value_prop or 'Not specified'}
PROSPECT: {prospect_name or 'Decision maker'}, {prospect_title or 'Executive'} at {prospect_company}
TONE: {tone}

Create a JSON array of {sequence_length} emails:
[
    {{
        "email_number": 1,
        "subject": "<compelling subject line>",
        "body": "<email body with personalization>",
        "send_delay_days": 0,
        "strategy": "<why this email works>"
    }}
]

Rules:
- Subject lines under 50 chars, no spam words
- Body under 150 words
- Include specific personalization for {prospect_company}
- Each follow-up references the previous email
- Include a clear, low-friction CTA
- No generic "I hope this email finds you well"
Return ONLY valid JSON array."""

            response = model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```"): text = re.sub(r'^```json?\n?', '', re.sub(r'\n?```$', '', text))
            emails = json.loads(text)

        for email in emails:
            st.markdown(f"### Email #{email.get('email_number', '?')} — Day {email.get('send_delay_days', '?')}")
            st.text_input(f"Subject", email.get("subject", ""), key=f"subj_{email.get('email_number')}")
            st.text_area(f"Body", email.get("body", ""), height=150, key=f"body_{email.get('email_number')}")
            st.caption(f"💡 Strategy: {email.get('strategy', '')}")
            st.divider()

        all_text = "\n\n---\n\n".join([f"Subject: {e.get('subject','')}\n\n{e.get('body','')}" for e in emails])
        st.download_button("📥 Download Sequence", all_text, file_name=f"outreach-{prospect_company}.txt")

with tab2:
    st.markdown("### Upload a CSV of prospects")
    st.markdown("Columns: `name, title, company, email` (email optional)")

    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    bulk_product = st.text_input("📦 Product/Service (for all)", placeholder="e.g. AI-powered analytics", key="bulk_prod")
    bulk_value = st.text_area("💡 Value Prop (for all)", placeholder="We help...", height=60, key="bulk_val")

    if uploaded and gemini_key and bulk_product:
        df = csv.DictReader(io.StringIO(uploaded.read().decode()))
        prospects = list(df)
        st.write(f"Found {len(prospects)} prospects")

        if st.button("🚀 Generate All Emails", type="primary"):
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            results = []

            progress = st.progress(0)
            for i, p in enumerate(prospects[:20]):  # Limit to 20
                with st.spinner(f"Generating for {p.get('name', 'Unknown')}..."):
                    prompt = f"""Write a cold email for:
Product: {bulk_product} — {bulk_value}
Prospect: {p.get('name','')}, {p.get('title','')} at {p.get('company','')}
Rules: Under 100 words, compelling subject, specific CTA.
Return JSON: {{"subject": "", "body": ""}}"""

                    resp = model.generate_content(prompt)
                    text = resp.text.strip()
                    if text.startswith("```"): text = re.sub(r'^```json?\n?', '', re.sub(r'\n?```$', '', text))
                    try:
                        email_data = json.loads(text)
                        results.append({**p, **email_data})
                    except:
                        results.append({**p, "subject": "Error", "body": "Failed to generate"})

                progress.progress((i + 1) / min(len(prospects), 20))

            st.success(f"Generated {len(results)} emails!")
            for r in results:
                with st.expander(f"📧 {r.get('name', '')} @ {r.get('company', '')}"):
                    st.markdown(f"**Subject:** {r.get('subject', '')}")
                    st.markdown(r.get('body', ''))

            csv_output = io.StringIO()
            writer = csv.DictWriter(csv_output, fieldnames=["name", "title", "company", "email", "subject", "body"])
            writer.writeheader()
            writer.writerows(results)
            st.download_button("📥 Download All Emails (CSV)", csv_output.getvalue(),
                             file_name=f"bulk-outreach-{datetime.now().strftime('%Y%m%d')}.csv")

st.markdown("---")
st.markdown("*Cortex Email GTM — [Cortex AI Suite](/) • Powered by Gemini*")
