"""
Cortex AI Suite — Launcher / Hub
"""
import streamlit as st

st.set_page_config(page_title="Cortex AI Suite", page_icon="🧠", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
.stApp { font-family: 'Inter', sans-serif; background: #fafafa; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding:3rem 0 1rem;">
    <h1 style="font-size:3rem; font-weight:800; letter-spacing:-0.02em;">🧠 Cortex AI Suite</h1>
    <p style="font-size:1.2rem; color:#6b7280; max-width:600px; margin:0 auto;">
        Professional AI tools for business. Powered by Google Gemini. Bring your own API key.
    </p>
</div>
""", unsafe_allow_html=True)

tools = [
    {
        "icon": "🔍",
        "name": "SEO Audit",
        "desc": "AI-powered on-page SEO analysis with competitive SERP insights. Get actionable recommendations in seconds.",
        "price": "$49/mo Pro",
        "color": "#667eea",
        "page": "seo-audit/app.py"
    },
    {
        "icon": "⚔️",
        "name": "Sales Intel",
        "desc": "Generate competitive battle cards with objection handlers, SWOT analysis, and killer questions.",
        "price": "$99/mo Pro",
        "color": "#ef4444",
        "page": "sales-intel/app.py"
    },
    {
        "icon": "📊",
        "name": "VC Diligence",
        "desc": "Startup investment analysis in minutes. Team, market, product, traction scoring with investment thesis.",
        "price": "$199/mo Pro",
        "color": "#10b981",
        "page": "vc-diligence/app.py"
    },
]

cols = st.columns(3)
for i, tool in enumerate(tools):
    with cols[i]:
        st.markdown(f"""
        <div style="background:white; border:1px solid #e5e7eb; border-radius:16px; padding:2rem; height:300px; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
                <p style="font-size:2.5rem; margin:0;">{tool['icon']}</p>
                <h3 style="font-weight:700; margin:0.5rem 0;">{tool['name']}</h3>
                <p style="color:#6b7280; font-size:0.9rem;">{tool['desc']}</p>
            </div>
            <div>
                <p style="color:{tool['color']}; font-weight:600; margin:0;">{tool['price']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Multipage navigation
page = st.selectbox("🚀 Launch a tool:", ["Choose...", "🔍 SEO Audit", "⚔️ Sales Intel", "📊 VC Diligence"])

if page == "🔍 SEO Audit":
    exec(open("/app/seo-audit/app.py").read())
elif page == "⚔️ Sales Intel":
    exec(open("/app/sales-intel/app.py").read())
elif page == "📊 VC Diligence":
    exec(open("/app/vc-diligence/app.py").read())

st.markdown("""
<div style="text-align:center; color:#9ca3af; padding:2rem;">
    <p>Built by Cortex AI • Your API keys never leave your browser • No data stored</p>
</div>
""", unsafe_allow_html=True)
