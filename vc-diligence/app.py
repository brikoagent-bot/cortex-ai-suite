"""
Cortex VC Diligence — AI-Powered Startup Investment Analysis
Comprehensive due diligence reports for investors
"""
import streamlit as st
import google.generativeai as genai
import json
import re
from datetime import datetime

st.set_page_config(page_title="Cortex VC Diligence | AI Investment Analysis", page_icon="📊", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; }
    .main-header { text-align: center; padding: 2rem 0; }
    .main-header h1 { font-size: 2.5rem; font-weight: 700; background: linear-gradient(135deg, #10b981 0%, #059669 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>📊 Cortex VC Diligence</h1>
    <p>AI-powered startup due diligence for investors & VCs</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Settings")
    gemini_key = st.text_input("Google Gemini API Key", type="password", help="Free at aistudio.google.com/apikey")
    st.divider()
    st.markdown("### 💎 Cortex Pro")
    st.markdown("Unlimited reports, portfolio tracking, deal flow management.")
    st.link_button("Upgrade — $199/mo", "https://buy.stripe.com/test_placeholder", use_container_width=True)

company_name = st.text_input("🏢 Company/Startup Name", placeholder="e.g. Stripe, Notion, Linear")
company_url = st.text_input("🌐 Company Website (optional)", placeholder="https://example.com")
col1, col2 = st.columns(2)
with col1:
    stage = st.selectbox("📈 Funding Stage", ["Pre-Seed", "Seed", "Series A", "Series B", "Series C+", "Growth", "Pre-IPO"])
    sector = st.text_input("🏭 Sector", placeholder="e.g. Fintech, SaaS, AI/ML")
with col2:
    raise_amount = st.text_input("💰 Raising (optional)", placeholder="e.g. $10M Series A")
    additional_context = st.text_area("📝 Additional Context", placeholder="Any info about the company...", height=80)

generate = st.button("📊 Generate Due Diligence Report", type="primary", use_container_width=True,
                     disabled=not (gemini_key and company_name))

if generate:
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    with st.status("🧠 Running due diligence analysis...", expanded=True) as status:
        st.write(f"Analyzing {company_name}...")

        prompt = f"""You are a senior VC analyst. Perform comprehensive due diligence on this startup.

COMPANY: {company_name}
WEBSITE: {company_url or 'Not provided'}
STAGE: {stage}
SECTOR: {sector or 'Not specified'}
RAISING: {raise_amount or 'Not specified'}
ADDITIONAL CONTEXT: {additional_context or 'None'}

Using your knowledge, generate a thorough investment analysis. Return JSON:
{{
    "company_overview": {{
        "name": "{company_name}",
        "sector": "<sector>",
        "stage": "{stage}",
        "founded": "<year if known>",
        "headquarters": "<location if known>",
        "description": "<2-3 sentence description>",
        "business_model": "<how they make money>"
    }},
    "market_analysis": {{
        "tam": "<total addressable market estimate>",
        "sam": "<serviceable addressable market>",
        "som": "<serviceable obtainable market>",
        "growth_rate": "<market CAGR>",
        "market_trends": ["<key trends>"],
        "market_risks": ["<key risks>"]
    }},
    "competitive_landscape": {{
        "direct_competitors": [
            {{"name": "<competitor>", "funding": "<funding>", "differentiator": "<what sets them apart>"}}
        ],
        "competitive_advantages": ["<moats>"],
        "competitive_risks": ["<threats>"]
    }},
    "team_assessment": {{
        "leadership_quality": "<assessment>",
        "key_hires_needed": ["<roles>"],
        "team_risks": ["<risks>"]
    }},
    "financial_analysis": {{
        "revenue_model": "<description>",
        "unit_economics": "<LTV/CAC/margins if estimable>",
        "burn_rate_assessment": "<assessment>",
        "path_to_profitability": "<assessment>"
    }},
    "investment_thesis": {{
        "bull_case": "<why this could be huge>",
        "bear_case": "<what could go wrong>",
        "base_case": "<most likely outcome>"
    }},
    "risk_matrix": [
        {{"risk": "<risk>", "likelihood": "<low|medium|high>", "impact": "<low|medium|high>", "mitigation": "<strategy>"}}
    ],
    "recommendation": {{
        "verdict": "<INVEST|PASS|WATCH>",
        "confidence": "<low|medium|high>",
        "rationale": "<2-3 sentences>",
        "suggested_terms": "<if INVEST, suggested terms>"
    }},
    "due_diligence_checklist": [
        {{"item": "<what to verify>", "priority": "<critical|important|nice-to-have>", "status": "pending"}}
    ],
    "score": {{
        "overall": <1-10>,
        "market": <1-10>,
        "team": <1-10>,
        "product": <1-10>,
        "financials": <1-10>,
        "timing": <1-10>
    }}
}}

Be thorough and specific. Use real market data where possible. Return ONLY valid JSON."""

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

        status.update(label="✅ Report ready!", state="complete")

    # Display report
    overview = data.get("company_overview", {})
    scores = data.get("score", {})
    rec = data.get("recommendation", {})

    # Header with verdict
    verdict = rec.get("verdict", "WATCH")
    verdict_color = {"INVEST": "#10b981", "PASS": "#ef4444", "WATCH": "#f59e0b"}.get(verdict, "#6b7280")

    st.markdown(f"""
    <div style="text-align:center; padding:2rem; background:#f8f9fa; border-radius:16px; margin:1rem 0;">
        <h2>{overview.get('name', company_name)}</h2>
        <p style="color:#6b7280;">{overview.get('description', '')}</p>
        <div style="font-size:2.5rem; font-weight:800; color:{verdict_color}; margin:1rem 0;">{verdict}</div>
        <p>Overall Score: <b>{scores.get('overall', 'N/A')}/10</b> | Confidence: {rec.get('confidence', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Scores
    st.subheader("📊 Scores")
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Market", f"{scores.get('market', '?')}/10")
    s2.metric("Team", f"{scores.get('team', '?')}/10")
    s3.metric("Product", f"{scores.get('product', '?')}/10")
    s4.metric("Financials", f"{scores.get('financials', '?')}/10")
    s5.metric("Timing", f"{scores.get('timing', '?')}/10")

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📈 Market", "⚔️ Competition", "👥 Team", "💰 Financials", "⚠️ Risks", "✅ Checklist"])

    with tab1:
        market = data.get("market_analysis", {})
        m1, m2, m3 = st.columns(3)
        m1.metric("TAM", market.get("tam", "N/A"))
        m2.metric("SAM", market.get("sam", "N/A"))
        m3.metric("Growth", market.get("growth_rate", "N/A"))
        st.markdown("**Trends:**")
        for t in market.get("market_trends", []): st.markdown(f"- 📈 {t}")
        st.markdown("**Risks:**")
        for r in market.get("market_risks", []): st.markdown(f"- ⚠️ {r}")

    with tab2:
        comp = data.get("competitive_landscape", {})
        for c in comp.get("direct_competitors", []):
            st.markdown(f"**{c.get('name', '')}** — {c.get('funding', '')} — {c.get('differentiator', '')}")
        st.markdown("**Moats:**")
        for a in comp.get("competitive_advantages", []): st.markdown(f"- 🏰 {a}")

    with tab3:
        team = data.get("team_assessment", {})
        st.markdown(team.get("leadership_quality", ""))
        st.markdown("**Key Hires Needed:**")
        for h in team.get("key_hires_needed", []): st.markdown(f"- 👤 {h}")

    with tab4:
        fin = data.get("financial_analysis", {})
        st.markdown(f"**Revenue Model:** {fin.get('revenue_model', '')}")
        st.markdown(f"**Unit Economics:** {fin.get('unit_economics', '')}")
        st.markdown(f"**Path to Profitability:** {fin.get('path_to_profitability', '')}")

    with tab5:
        for risk in data.get("risk_matrix", []):
            emoji = "🔴" if risk.get("impact") == "high" else "🟡" if risk.get("impact") == "medium" else "🟢"
            with st.expander(f"{emoji} {risk.get('risk', '')} (L:{risk.get('likelihood', '')} / I:{risk.get('impact', '')})"):
                st.markdown(f"**Mitigation:** {risk.get('mitigation', '')}")

    with tab6:
        for item in data.get("due_diligence_checklist", []):
            priority_emoji = "🔴" if item.get("priority") == "critical" else "🟡" if item.get("priority") == "important" else "🔵"
            st.checkbox(f"{priority_emoji} {item.get('item', '')} [{item.get('priority', '')}]")

    # Investment thesis
    st.markdown("### 📋 Investment Thesis")
    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown("**🟢 Bull Case**")
        st.markdown(data.get("investment_thesis", {}).get("bull_case", ""))
    with t2:
        st.markdown("**🟡 Base Case**")
        st.markdown(data.get("investment_thesis", {}).get("base_case", ""))
    with t3:
        st.markdown("**🔴 Bear Case**")
        st.markdown(data.get("investment_thesis", {}).get("bear_case", ""))

    st.markdown(f"### Recommendation\n{rec.get('rationale', '')}")

    st.download_button("📥 Download Report (JSON)", json.dumps(data, indent=2),
                      file_name=f"diligence-{company_name.replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}.json")

    st.markdown("""
    ---
    ### 🚀 Managing a portfolio?
    **Cortex Pro** tracks your entire deal flow, generates reports in bulk, and alerts you to market changes.
    [Start Pro — $199/mo](https://buy.stripe.com/test_placeholder)
    """)

st.markdown("---")
st.markdown("*Cortex VC Diligence — [Cortex AI Suite](/) • Powered by Gemini • No data stored*")
