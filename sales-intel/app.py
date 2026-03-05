"""
Cortex Sales Intel — AI-Powered Competitive Battle Cards
Generates sales battle cards comparing your product vs competitors
"""
import streamlit as st
import google.generativeai as genai
import json
import re
from datetime import datetime

st.set_page_config(
    page_title="Cortex Sales Intel | AI Battle Cards",
    page_icon="⚔️",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; }
    .main-header { text-align: center; padding: 2rem 0; }
    .main-header h1 { font-size: 2.5rem; font-weight: 700; background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>⚔️ Cortex Sales Intel</h1>
    <p>AI-powered competitive battle cards for your sales team</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Settings")
    gemini_key = st.text_input("Google Gemini API Key", type="password",
                                help="Free at aistudio.google.com/apikey")
    st.divider()
    st.markdown("### 💎 Cortex Pro")
    st.markdown("Unlimited battle cards, CRM integration, team sharing.")
    st.link_button("Upgrade — $99/mo", "https://buy.stripe.com/test_placeholder",
                   use_container_width=True)

# Main form
col1, col2 = st.columns(2)
with col1:
    your_product = st.text_input("🏢 Your Product/Company", placeholder="e.g. Slack")
    your_description = st.text_area("Your Product Description", placeholder="Team messaging platform with channels, integrations, and file sharing...", height=100)
with col2:
    competitor = st.text_input("🎯 Competitor", placeholder="e.g. Microsoft Teams")
    competitor_description = st.text_area("Competitor Description (optional)", placeholder="Leave blank for AI to research...", height=100)

industry = st.text_input("🏭 Industry/Market", placeholder="e.g. Enterprise collaboration software")

generate = st.button("⚔️ Generate Battle Card", type="primary", use_container_width=True,
                     disabled=not (gemini_key and your_product and competitor))

if generate:
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    with st.status("🧠 Generating battle card...", expanded=True) as status:
        st.write(f"Analyzing {your_product} vs {competitor}...")

        prompt = f"""You are a sales intelligence analyst. Create a comprehensive competitive battle card.

YOUR PRODUCT: {your_product}
YOUR DESCRIPTION: {your_description or 'Research based on product name'}
COMPETITOR: {competitor}
COMPETITOR DESCRIPTION: {competitor_description or 'Research based on company name'}
INDUSTRY: {industry or 'General'}

Return a JSON object with this exact structure:
{{
    "overview": {{
        "your_product": "{your_product}",
        "competitor": "{competitor}",
        "market_position": "<brief market context>"
    }},
    "strengths_vs_competitor": [
        {{"area": "<area>", "advantage": "<specific advantage>", "proof_point": "<data/evidence>"}}
    ],
    "weaknesses_vs_competitor": [
        {{"area": "<area>", "weakness": "<honest assessment>", "mitigation": "<how to handle in sales>"}}
    ],
    "feature_comparison": [
        {{"feature": "<feature>", "your_product": "<rating/detail>", "competitor": "<rating/detail>", "winner": "<who wins>"}}
    ],
    "pricing_comparison": {{
        "your_pricing": "<pricing structure>",
        "competitor_pricing": "<pricing structure>",
        "value_argument": "<why your pricing is better>"
    }},
    "objection_handling": [
        {{"objection": "<common objection>", "response": "<recommended sales response>", "proof": "<supporting evidence>"}}
    ],
    "win_themes": ["<key messages that win deals>"],
    "ideal_customer_profile": "<who you win against this competitor>",
    "trap_questions": ["<questions to ask prospects that highlight competitor weaknesses>"],
    "competitive_landmines": ["<things to plant early in the sales cycle>"]
}}

Be specific, actionable, and data-driven. Include real market knowledge.
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
            response = model.generate_content(prompt + "\n\nReturn ONLY valid JSON, no markdown.")
            text = response.text.strip()
            if text.startswith("```"):
                text = re.sub(r'^```json?\n?', '', text)
                text = re.sub(r'\n?```$', '', text)
            data = json.loads(text)

        status.update(label="✅ Battle card ready!", state="complete")

    # Display battle card
    st.markdown(f"## ⚔️ {your_product} vs {competitor}")
    st.markdown(f"*{data.get('overview', {}).get('market_position', '')}*")

    # Strengths & Weaknesses
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 💪 Your Advantages")
        for s in data.get("strengths_vs_competitor", []):
            with st.expander(f"✅ {s.get('area', '')}: {s.get('advantage', '')}"):
                st.markdown(f"**Proof:** {s.get('proof_point', '')}")

    with col2:
        st.markdown("### ⚠️ Watch Out For")
        for w in data.get("weaknesses_vs_competitor", []):
            with st.expander(f"🔶 {w.get('area', '')}: {w.get('weakness', '')}"):
                st.markdown(f"**Mitigation:** {w.get('mitigation', '')}")

    # Feature comparison
    st.markdown("### 📊 Feature Comparison")
    if data.get("feature_comparison"):
        for feat in data["feature_comparison"]:
            c1, c2, c3, c4 = st.columns([3, 3, 3, 1])
            c1.markdown(f"**{feat.get('feature', '')}**")
            c2.markdown(feat.get("your_product", ""))
            c3.markdown(feat.get("competitor", ""))
            winner = feat.get("winner", "")
            c4.markdown("🏆" if your_product.lower() in winner.lower() else "⚠️")

    # Pricing
    st.markdown("### 💰 Pricing")
    pricing = data.get("pricing_comparison", {})
    p1, p2 = st.columns(2)
    p1.metric(your_product, pricing.get("your_pricing", "N/A"))
    p2.metric(competitor, pricing.get("competitor_pricing", "N/A"))
    st.info(f"💡 **Value Argument:** {pricing.get('value_argument', '')}")

    # Objection handling
    st.markdown("### 🛡️ Objection Handling Scripts")
    for obj in data.get("objection_handling", []):
        with st.expander(f"❓ \"{obj.get('objection', '')}\""):
            st.markdown(f"**Response:** {obj.get('response', '')}")
            st.markdown(f"**Evidence:** {obj.get('proof', '')}")

    # Win themes
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏆 Win Themes")
        for theme in data.get("win_themes", []):
            st.markdown(f"- {theme}")

        st.markdown("### 🎯 Ideal Customer")
        st.markdown(data.get("ideal_customer_profile", ""))

    with col2:
        st.markdown("### 🪤 Trap Questions")
        for q in data.get("trap_questions", []):
            st.markdown(f"- ❓ {q}")

        st.markdown("### 💣 Competitive Landmines")
        for l in data.get("competitive_landmines", []):
            st.markdown(f"- 💣 {l}")

    # Download
    st.download_button(
        "📥 Download Battle Card (JSON)",
        json.dumps(data, indent=2),
        file_name=f"battlecard-{your_product}-vs-{competitor}-{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json"
    )

    # CTA
    st.markdown("""
    ---
    ### 📈 Need battle cards for your whole competitive landscape?
    **Cortex Pro** generates unlimited battle cards, syncs with your CRM, and keeps them updated automatically.

    [Start Pro Trial — $99/mo](https://buy.stripe.com/test_placeholder)
    """)

st.markdown("---")
st.markdown("*Cortex Sales Intel — Part of [Cortex AI Suite](/) • Powered by Gemini • No data stored*")
