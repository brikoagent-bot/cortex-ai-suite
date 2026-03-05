"""
Cortex Sales Intel — AI Battle Card Generator
Generates competitive sales battle cards using Gemini
"""
import streamlit as st
import google.generativeai as genai
import json
import re
from datetime import datetime

st.set_page_config(page_title="Cortex Sales Intel | Battle Cards", page_icon="⚔️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
.stApp { font-family: 'Inter', sans-serif; }
.main-header { text-align: center; padding: 2rem 0; }
.main-header h1 { font-size: 2.5rem; font-weight: 700; background: linear-gradient(135deg, #f97316 0%, #ef4444 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>⚔️ Cortex Sales Intel</h1><p>AI-powered competitive battle cards for your sales team</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Settings")
    gemini_key = st.text_input("Google Gemini API Key", type="password", help="Free at aistudio.google.com/apikey")
    st.divider()
    st.markdown("### 💎 Pro Features")
    st.markdown("- Auto-refresh battle cards weekly\n- CRM integration\n- Team sharing")
    st.link_button("Upgrade — $99/mo", "https://buy.stripe.com/test_placeholder", use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    competitor = st.text_input("🏢 Competitor", placeholder="e.g., Salesforce, Slack, Zendesk")
with col2:
    your_product = st.text_input("🚀 Your Product", placeholder="e.g., HubSpot, Teams, Freshdesk")

generate = st.button("⚔️ Generate Battle Card", type="primary", use_container_width=True,
                      disabled=not (competitor and your_product and gemini_key))

if generate:
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    with st.status("🔍 Researching competitor...", expanded=True) as status:
        st.write(f"Analyzing {competitor} vs {your_product}...")
        
        prompt = f"""You are a competitive intelligence analyst. Create a comprehensive sales battle card.

COMPETITOR: {competitor}
YOUR PRODUCT: {your_product}

Return a JSON object with:
{{
    "competitor_overview": {{
        "name": "{competitor}",
        "description": "<1-2 sentence overview>",
        "founded": "<year or 'Unknown'>",
        "hq": "<location>",
        "employees": "<estimate>",
        "target_market": "<who they sell to>",
        "pricing_model": "<pricing approach>"
    }},
    "feature_comparison": [
        {{"feature": "<feature name>", "them": <1-10>, "us": <1-10>, "notes": "<brief note>"}},
        ... (8-10 features)
    ],
    "their_strengths": ["<strength 1>", "<strength 2>", "<strength 3>", "<strength 4>", "<strength 5>"],
    "their_weaknesses": ["<weakness 1>", "<weakness 2>", "<weakness 3>", "<weakness 4>", "<weakness 5>"],
    "our_advantages": ["<advantage 1>", "<advantage 2>", "<advantage 3>"],
    "objection_handlers": [
        {{"objection": "<what prospect says>", "response": "<your scripted response>", "proof": "<evidence>"}},
        ... (5-8 objections)
    ],
    "killer_questions": ["<question that exposes their weakness>", ... (5 questions)],
    "landmines": ["<early statement that positions you well>", ... (3-5 landmines)],
    "quick_verdict": "<1 sentence summary of competitive position>",
    "win_rate_estimate": "<percentage estimate of winning against them>"
}}

Be strategic, honest, and specific. Real data preferred over generic statements.
Return ONLY valid JSON."""
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = re.sub(r'^```json?\n?', '', text)
            text = re.sub(r'\n?```$', '', text)
        
        try:
            data = json.loads(text)
        except:
            st.error("Failed to parse. Retrying...")
            response = model.generate_content(prompt + "\nReturn ONLY valid JSON, no markdown fences.")
            text = response.text.strip()
            if text.startswith("```"):
                text = re.sub(r'^```json?\n?', '', text)
                text = re.sub(r'\n?```$', '', text)
            data = json.loads(text)
        
        status.update(label="✅ Battle card generated!", state="complete")
    
    # Display
    overview = data.get("competitor_overview", {})
    st.markdown(f"### 🏢 {overview.get('name', competitor)}")
    st.markdown(f"> {overview.get('description', '')}")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Founded", overview.get("founded", "N/A"))
    c2.metric("HQ", overview.get("hq", "N/A"))
    c3.metric("Employees", overview.get("employees", "N/A"))
    c4.metric("Win Rate Est.", data.get("win_rate_estimate", "N/A"))
    
    st.info(f"**Quick Verdict:** {data.get('quick_verdict', '')}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Feature Comparison", "💪 SWOT", "🗣️ Objection Handlers", "🎯 Tactics"])
    
    with tab1:
        features = data.get("feature_comparison", [])
        if features:
            st.markdown("| Feature | Them | Us | Winner | Notes |")
            st.markdown("|---------|------|-----|--------|-------|")
            for f in features:
                them = f.get("them", 5)
                us = f.get("us", 5)
                winner = "✅ Us" if us > them else ("❌ Them" if them > us else "🤝 Tie")
                st.markdown(f"| {f.get('feature', '')} | {them}/10 | {us}/10 | {winner} | {f.get('notes', '')} |")
    
    with tab2:
        col_s, col_w = st.columns(2)
        with col_s:
            st.markdown("### ❌ Their Strengths")
            for s in data.get("their_strengths", []):
                st.markdown(f"- {s}")
            st.markdown("### ✅ Our Advantages")
            for a in data.get("our_advantages", []):
                st.markdown(f"- 🏆 {a}")
        with col_w:
            st.markdown("### ✅ Their Weaknesses")
            for w in data.get("their_weaknesses", []):
                st.markdown(f"- {w}")
    
    with tab3:
        for obj in data.get("objection_handlers", []):
            with st.expander(f"🗣️ \"{obj.get('objection', '')}\""):
                st.markdown(f"**Response:** {obj.get('response', '')}")
                st.markdown(f"**Proof:** {obj.get('proof', '')}")
    
    with tab4:
        st.markdown("### 🎯 Killer Questions")
        for q in data.get("killer_questions", []):
            st.markdown(f"- ❓ {q}")
        st.markdown("### 💣 Landmines (Say Early)")
        for l in data.get("landmines", []):
            st.markdown(f"- 💣 {l}")
    
    # Download
    st.download_button("📥 Download Battle Card (JSON)", json.dumps(data, indent=2),
                      file_name=f"battle-card-{competitor.lower().replace(' ','-')}.json", mime="application/json")
    
    st.markdown("""
    <div style="background:linear-gradient(135deg,#f97316,#ef4444);border-radius:12px;padding:2rem;color:white;text-align:center;margin:2rem 0;">
        <h2>📊 Want live battle cards?</h2>
        <p>Pro auto-refreshes weekly and integrates with your CRM.</p>
        <a href="https://buy.stripe.com/test_placeholder" style="background:white;color:#ef4444;padding:12px 32px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:1rem;">Start Pro — $99/mo</a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div style="text-align:center;color:#9ca3af;"><p>Cortex Sales Intel — Part of <a href="/">Cortex AI Suite</a></p></div>', unsafe_allow_html=True)
