"""
Cortex VC Diligence — AI Startup Investment Analysis
Multi-agent pipeline for startup due diligence
"""
import streamlit as st
import google.generativeai as genai
import json
import re
from datetime import datetime

st.set_page_config(page_title="Cortex VC Diligence | Startup Analysis", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
.stApp { font-family: 'Inter', sans-serif; }
.main-header { text-align: center; padding: 2rem 0; }
.main-header h1 { font-size: 2.5rem; font-weight: 700; background: linear-gradient(135deg, #10b981 0%, #059669 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.score-card { background: #f0fdf4; border: 2px solid #10b981; border-radius: 16px; padding: 2rem; text-align: center; }
.score-card h2 { font-size: 3rem; color: #059669; margin: 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>📊 Cortex VC Diligence</h1><p>AI-powered startup investment analysis in minutes, not weeks</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Settings")
    gemini_key = st.text_input("Google Gemini API Key", type="password")
    st.divider()
    st.markdown("### 💎 Fund Pro")
    st.markdown("- Portfolio tracking\n- Market comparables\n- LP-ready reports\n- Deal flow scoring")
    st.link_button("Start Fund Pro — $199/mo", "https://buy.stripe.com/test_placeholder", use_container_width=True)

company = st.text_input("🏢 Company Name", placeholder="e.g., Stripe, Notion, Linear")
website = st.text_input("🌐 Website (optional)", placeholder="https://example.com")
context = st.text_area("📝 Additional Context (optional)", placeholder="Stage, sector, what you know...", height=80)

analyze = st.button("🔍 Run Due Diligence", type="primary", use_container_width=True,
                     disabled=not (company and gemini_key))

if analyze:
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    with st.status("🔍 Running due diligence pipeline...", expanded=True) as status:
        st.write(f"Stage 1/4: Researching {company}...")
        
        prompt = f"""You are a senior VC analyst conducting due diligence on a startup.

COMPANY: {company}
WEBSITE: {website or 'Not provided'}
CONTEXT: {context or 'None'}

Conduct thorough analysis and return JSON:
{{
    "company": {{
        "name": "{company}",
        "description": "<what they do in 1-2 sentences>",
        "founded": "<year>",
        "hq": "<location>",
        "stage": "<Pre-seed/Seed/Series A/B/C/etc>",
        "sector": "<primary sector>",
        "business_model": "<how they make money>",
        "website": "{website or 'Unknown'}"
    }},
    "team": {{
        "founders": ["<name - background>"],
        "team_size": "<estimate>",
        "team_score": <1-10>,
        "team_notes": "<assessment>"
    }},
    "market": {{
        "tam": "<Total Addressable Market size>",
        "sam": "<Serviceable Available Market>",
        "som": "<Serviceable Obtainable Market>",
        "market_growth": "<annual growth rate>",
        "market_score": <1-10>,
        "market_notes": "<assessment>"
    }},
    "product": {{
        "description": "<what the product does>",
        "differentiation": "<key differentiators>",
        "moat": "<competitive moat>",
        "product_score": <1-10>,
        "product_notes": "<assessment>"
    }},
    "traction": {{
        "revenue": "<if known>",
        "users": "<if known>",
        "growth_rate": "<if known>",
        "key_metrics": "<notable metrics>",
        "traction_score": <1-10>,
        "traction_notes": "<assessment>"
    }},
    "competition": {{
        "direct_competitors": ["<competitor 1>", "<competitor 2>", "<competitor 3>"],
        "competitive_advantage": "<main advantage>",
        "competition_score": <1-10>,
        "competition_notes": "<assessment>"
    }},
    "financials": {{
        "last_funding": "<amount and date if known>",
        "total_raised": "<if known>",
        "valuation": "<if known>",
        "burn_rate": "<estimate if possible>",
        "runway": "<estimate>",
        "financial_score": <1-10>
    }},
    "risks": [
        {{"risk": "<risk description>", "severity": "<high/medium/low>", "mitigation": "<possible mitigation>"}},
        ... (5-7 risks)
    ],
    "opportunities": ["<opportunity 1>", "<opportunity 2>", "<opportunity 3>"],
    "overall_score": <1-100>,
    "investment_thesis": "<2-3 sentence thesis for/against investing>",
    "recommendation": "<STRONG BUY / BUY / HOLD / PASS / STRONG PASS>",
    "key_questions": ["<question for founders>", ... (5 questions)]
}}

Be analytical and honest. Use real data where possible. Score objectively.
Return ONLY valid JSON."""
        
        st.write("Stage 2/4: Analyzing market & competition...")
        st.write("Stage 3/4: Evaluating team & product...")
        st.write("Stage 4/4: Generating investment thesis...")
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = re.sub(r'^```json?\n?', '', text)
            text = re.sub(r'\n?```$', '', text)
        
        try:
            data = json.loads(text)
        except:
            response = model.generate_content(prompt + "\nReturn ONLY valid JSON.")
            text = response.text.strip()
            if text.startswith("```"):
                text = re.sub(r'^```json?\n?', '', text)
                text = re.sub(r'\n?```$', '', text)
            data = json.loads(text)
        
        status.update(label="✅ Due diligence complete!", state="complete")
    
    # Score
    score = data.get("overall_score", 50)
    rec = data.get("recommendation", "HOLD")
    rec_color = "#22c55e" if "BUY" in rec else "#ef4444" if "PASS" in rec else "#f59e0b"
    
    s1, s2, s3 = st.columns([1,2,1])
    with s2:
        st.markdown(f"""
        <div class="score-card">
            <p style="color:#6b7280;margin:0;">Investment Score</p>
            <h2>{score}/100</h2>
            <p style="font-size:1.5rem;font-weight:700;color:{rec_color};margin:0;">{rec}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"### 💡 Investment Thesis")
    st.info(data.get("investment_thesis", ""))
    
    # Component Scores
    st.markdown("### 📊 Component Scores")
    scores = {
        "👥 Team": data.get("team", {}).get("team_score", 5),
        "📈 Market": data.get("market", {}).get("market_score", 5),
        "🛠️ Product": data.get("product", {}).get("product_score", 5),
        "🚀 Traction": data.get("traction", {}).get("traction_score", 5),
        "⚔️ Competition": data.get("competition", {}).get("competition_score", 5),
        "💰 Financials": data.get("financials", {}).get("financial_score", 5),
    }
    cols = st.columns(6)
    for i, (label, score_val) in enumerate(scores.items()):
        color = "#22c55e" if score_val >= 7 else "#f59e0b" if score_val >= 5 else "#ef4444"
        cols[i].markdown(f"<div style='text-align:center;'><p style='margin:0;font-size:0.85rem;'>{label}</p><p style='font-size:2rem;font-weight:700;color:{color};margin:0;'>{score_val}</p></div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏢 Company", "📊 Analysis", "⚠️ Risks", "❓ Questions", "📄 Full Report"])
    
    with tab1:
        comp = data.get("company", {})
        st.markdown(f"**{comp.get('name', company)}** — {comp.get('description', '')}")
        st.markdown(f"- **Stage:** {comp.get('stage', 'N/A')}")
        st.markdown(f"- **Sector:** {comp.get('sector', 'N/A')}")
        st.markdown(f"- **Business Model:** {comp.get('business_model', 'N/A')}")
        
        fin = data.get("financials", {})
        st.markdown("### 💰 Financials")
        st.markdown(f"- **Last Funding:** {fin.get('last_funding', 'N/A')}")
        st.markdown(f"- **Total Raised:** {fin.get('total_raised', 'N/A')}")
        st.markdown(f"- **Valuation:** {fin.get('valuation', 'N/A')}")
    
    with tab2:
        for section, key in [("Team", "team"), ("Market", "market"), ("Product", "product"), ("Traction", "traction"), ("Competition", "competition")]:
            d = data.get(key, {})
            notes_key = f"{key}_notes"
            st.markdown(f"### {section}")
            st.markdown(d.get(notes_key, "No data available"))
    
    with tab3:
        for risk in data.get("risks", []):
            sev = risk.get("severity", "medium")
            emoji = "🔴" if sev == "high" else "🟡" if sev == "medium" else "🟢"
            with st.expander(f"{emoji} {risk.get('risk', '')}"):
                st.markdown(f"**Severity:** {sev.upper()}")
                st.markdown(f"**Mitigation:** {risk.get('mitigation', '')}")
        
        st.markdown("### 🌟 Opportunities")
        for opp in data.get("opportunities", []):
            st.markdown(f"- ✨ {opp}")
    
    with tab4:
        st.markdown("### Questions for Founders")
        for q in data.get("key_questions", []):
            st.markdown(f"- ❓ {q}")
    
    with tab5:
        st.json(data)
    
    st.download_button("📥 Download Report (JSON)", json.dumps(data, indent=2),
                      file_name=f"dd-{company.lower().replace(' ','-')}-{datetime.now().strftime('%Y%m%d')}.json")

st.markdown("---")
st.markdown('<div style="text-align:center;color:#9ca3af;"><p>Cortex VC Diligence — Part of <a href="/">Cortex AI Suite</a></p></div>', unsafe_allow_html=True)
