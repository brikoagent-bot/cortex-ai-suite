"""
Cortex SEO Audit — AI-Powered SEO Analysis Tool
Built on Gemini + Firecrawl for comprehensive on-page SEO audits
"""
import streamlit as st
import google.generativeai as genai
import requests
import json
import re
from datetime import datetime

st.set_page_config(
    page_title="Cortex SEO Audit | AI-Powered SEO Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: #6b7280;
        font-size: 1.1rem;
    }
    
    .metric-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e5e7eb;
    }
    
    .priority-p0 { border-left: 4px solid #ef4444; }
    .priority-p1 { border-left: 4px solid #f59e0b; }
    .priority-p2 { border-left: 4px solid #3b82f6; }
    
    .cta-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 2rem;
        color: white;
        text-align: center;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>🔍 Cortex SEO Audit</h1>
    <p>AI-powered on-page SEO analysis with competitive SERP insights</p>
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/search-in-browser.png", width=64)
    st.title("Settings")
    
    gemini_key = st.text_input("Google Gemini API Key", type="password", 
                                help="Get free at aistudio.google.com/apikey")
    firecrawl_key = st.text_input("Firecrawl API Key (optional)", type="password",
                                   help="Get free at firecrawl.dev — 500 free credits")
    
    st.divider()
    st.markdown("### 💎 Cortex Pro")
    st.markdown("Unlock unlimited audits, competitor tracking, and weekly reports.")
    st.link_button("Upgrade to Pro — $49/mo", "https://buy.stripe.com/test_placeholder", 
                   use_container_width=True)
    
    st.divider()
    st.markdown("**Free tier:** 3 audits/day")
    st.markdown("**Pro:** Unlimited + tracking")
    st.markdown("---")
    st.markdown("Built by [Cortex AI](https://cortex-ai.tools)")


def scrape_with_firecrawl(url: str, api_key: str) -> dict:
    """Scrape a URL using Firecrawl API"""
    try:
        resp = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"url": url, "formats": ["markdown", "links"]},
            timeout=60
        )
        if resp.status_code == 200:
            return resp.json().get("data", {})
        else:
            return {"error": f"Firecrawl returned {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def scrape_with_fetch(url: str) -> dict:
    """Fallback: basic scrape with requests"""
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 CortexSEO/1.0"}, timeout=30)
        html = resp.text
        
        # Extract basic SEO elements
        title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        meta_desc = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
        h1s = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
        h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.IGNORECASE | re.DOTALL)
        
        # Clean HTML tags from extracted text
        def clean(text):
            return re.sub(r'<[^>]+>', '', text).strip() if text else ""
        
        # Count links
        internal_links = len(re.findall(r'href=["\']/', html))
        external_links = len(re.findall(r'href=["\'](https?://)', html))
        
        # Get text content for word count
        text_content = re.sub(r'<[^>]+>', ' ', html)
        text_content = re.sub(r'\s+', ' ', text_content)
        word_count = len(text_content.split())
        
        return {
            "markdown": text_content[:5000],
            "metadata": {
                "title": clean(title.group(1)) if title else "Not found",
                "description": clean(meta_desc.group(1)) if meta_desc else "Not found",
            },
            "h1": [clean(h) for h in h1s],
            "h2": [clean(h) for h in h2s],
            "internal_links": internal_links,
            "external_links": external_links,
            "word_count": word_count,
            "status_code": resp.status_code,
        }
    except Exception as e:
        return {"error": str(e)}


def run_seo_audit(url: str, gemini_key: str, firecrawl_key: str = None):
    """Run the full SEO audit pipeline"""
    
    # Step 1: Scrape the page
    with st.status("🔍 Scraping page...", expanded=True) as status:
        if firecrawl_key:
            st.write("Using Firecrawl for deep scraping...")
            page_data = scrape_with_firecrawl(url, firecrawl_key)
        else:
            st.write("Using basic scraper (add Firecrawl key for deeper analysis)...")
            page_data = scrape_with_fetch(url)
        
        if "error" in page_data:
            st.error(f"Scraping failed: {page_data['error']}")
            return None
        
        status.update(label="✅ Page scraped successfully", state="complete")
    
    # Step 2: AI Analysis with Gemini
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    with st.status("🧠 Running AI analysis...", expanded=True) as status:
        st.write("Analyzing on-page SEO factors...")
        
        audit_prompt = f"""You are an expert SEO auditor. Analyze this page data and provide a comprehensive SEO audit.

URL: {url}
Page Data: {json.dumps(page_data, indent=2)[:8000]}

Provide your analysis as a JSON object with these exact keys:
{{
    "score": <number 0-100>,
    "title_tag": "<current title>",
    "title_length": <number>,
    "title_analysis": "<analysis>",
    "meta_description": "<current meta description>",
    "meta_length": <number>,
    "meta_analysis": "<analysis>",
    "h1_tags": ["<list of h1 tags found>"],
    "heading_structure": "<analysis of heading hierarchy>",
    "word_count": <approximate>,
    "content_analysis": "<analysis of content quality and depth>",
    "internal_links": <count>,
    "external_links": <count>,
    "link_analysis": "<analysis>",
    "primary_keyword": "<inferred primary keyword>",
    "secondary_keywords": ["<list>"],
    "search_intent": "<informational|transactional|navigational|commercial>",
    "technical_issues": ["<list of issues found>"],
    "content_opportunities": ["<list of opportunities>"],
    "recommendations": [
        {{"priority": "P0", "action": "<specific action>", "impact": "<expected impact>", "effort": "<low|medium|high>"}},
        {{"priority": "P1", "action": "<action>", "impact": "<impact>", "effort": "<effort>"}},
        {{"priority": "P2", "action": "<action>", "impact": "<impact>", "effort": "<effort>"}}
    ]
}}

Be specific with data. Include actual character counts, specific issues, and actionable recommendations.
Return ONLY valid JSON, no markdown fences."""
        
        response = model.generate_content(audit_prompt)
        
        try:
            # Clean response
            text = response.text.strip()
            if text.startswith("```"):
                text = re.sub(r'^```json?\n?', '', text)
                text = re.sub(r'\n?```$', '', text)
            audit_result = json.loads(text)
        except json.JSONDecodeError:
            st.error("Failed to parse AI response. Retrying...")
            response = model.generate_content(audit_prompt + "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanation.")
            text = response.text.strip()
            if text.startswith("```"):
                text = re.sub(r'^```json?\n?', '', text)
                text = re.sub(r'\n?```$', '', text)
            audit_result = json.loads(text)
        
        status.update(label="✅ AI analysis complete", state="complete")
    
    # Step 3: Competitive SERP Analysis
    with st.status("📊 Analyzing competitors...", expanded=True) as status:
        st.write(f"Researching SERP for: {audit_result.get('primary_keyword', 'N/A')}")
        
        serp_prompt = f"""You are an SEO competitor analyst. For the keyword "{audit_result.get('primary_keyword', url)}", analyze the competitive SERP landscape.

Based on your knowledge of typical search results for this keyword, provide:

{{
    "keyword": "{audit_result.get('primary_keyword', '')}",
    "top_competitors": [
        {{"rank": 1, "title": "<title>", "url": "<url>", "content_type": "<type>"}},
        {{"rank": 2, "title": "<title>", "url": "<url>", "content_type": "<type>"}},
        {{"rank": 3, "title": "<title>", "url": "<url>", "content_type": "<type>"}}
    ],
    "title_patterns": ["<common patterns in competitor titles>"],
    "content_formats": ["<dominant content formats>"],
    "content_gaps": ["<opportunities the audited page could exploit>"],
    "differentiation_ideas": ["<ways to stand out>"]
}}

Return ONLY valid JSON."""
        
        serp_response = model.generate_content(serp_prompt)
        try:
            text = serp_response.text.strip()
            if text.startswith("```"):
                text = re.sub(r'^```json?\n?', '', text)
                text = re.sub(r'\n?```$', '', text)
            serp_result = json.loads(text)
        except:
            serp_result = {"keyword": audit_result.get("primary_keyword", ""), "top_competitors": [], "content_gaps": []}
        
        status.update(label="✅ Competitor analysis complete", state="complete")
    
    return {"audit": audit_result, "serp": serp_result, "page_data": page_data}


# --- Main UI ---
url_input = st.text_input("🌐 Enter URL to audit", placeholder="https://example.com", 
                           help="Enter the full URL including https://")

col1, col2 = st.columns([3, 1])
with col1:
    audit_button = st.button("🚀 Run SEO Audit", type="primary", use_container_width=True, 
                              disabled=not (url_input and gemini_key))
with col2:
    if not gemini_key:
        st.warning("⬅️ Add API key")

if audit_button and url_input and gemini_key:
    results = run_seo_audit(url_input, gemini_key, firecrawl_key)
    
    if results:
        audit = results["audit"]
        serp = results["serp"]
        
        # Score display
        score = audit.get("score", 0)
        score_color = "#22c55e" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
        
        st.markdown(f"""
        <div style="text-align:center; padding:2rem; background:linear-gradient(135deg, #f8f9fa, #e5e7eb); border-radius:16px; margin:1rem 0;">
            <h2 style="color:#374151; margin-bottom:0.5rem;">SEO Score</h2>
            <div style="font-size:4rem; font-weight:800; color:{score_color};">{score}/100</div>
            <p style="color:#6b7280;">for {url_input}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key Metrics
        st.subheader("📊 Key Metrics")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Title Length", f"{audit.get('title_length', 'N/A')} chars", 
                   "✅ Good" if 50 <= (audit.get('title_length', 0) or 0) <= 60 else "⚠️ Fix")
        m2.metric("Meta Description", f"{audit.get('meta_length', 'N/A')} chars",
                   "✅ Good" if 120 <= (audit.get('meta_length', 0) or 0) <= 160 else "⚠️ Fix")
        m3.metric("Word Count", f"{audit.get('word_count', 'N/A')}")
        m4.metric("Internal Links", f"{audit.get('internal_links', 'N/A')}")
        
        # Tabs for detailed analysis
        tab1, tab2, tab3, tab4 = st.tabs(["🏷️ On-Page", "🎯 Keywords", "📈 Competitors", "✅ Recommendations"])
        
        with tab1:
            st.markdown("### Title Tag")
            st.code(audit.get("title_tag", "Not found"))
            st.markdown(audit.get("title_analysis", ""))
            
            st.markdown("### Meta Description")
            st.code(audit.get("meta_description", "Not found"))
            st.markdown(audit.get("meta_analysis", ""))
            
            st.markdown("### Heading Structure")
            st.markdown(audit.get("heading_structure", ""))
            
            st.markdown("### Content Analysis")
            st.markdown(audit.get("content_analysis", ""))
            
            st.markdown("### Link Profile")
            st.markdown(audit.get("link_analysis", ""))
            
            if audit.get("technical_issues"):
                st.markdown("### ⚠️ Technical Issues")
                for issue in audit["technical_issues"]:
                    st.markdown(f"- {issue}")
        
        with tab2:
            st.markdown(f"### Primary Keyword: `{audit.get('primary_keyword', 'N/A')}`")
            st.markdown(f"**Search Intent:** {audit.get('search_intent', 'N/A')}")
            
            if audit.get("secondary_keywords"):
                st.markdown("### Secondary Keywords")
                for kw in audit["secondary_keywords"]:
                    st.markdown(f"- {kw}")
            
            if audit.get("content_opportunities"):
                st.markdown("### 💡 Content Opportunities")
                for opp in audit["content_opportunities"]:
                    st.markdown(f"- {opp}")
        
        with tab3:
            if serp.get("top_competitors"):
                st.markdown(f"### SERP Analysis for: `{serp.get('keyword', '')}`")
                for comp in serp["top_competitors"]:
                    st.markdown(f"**#{comp.get('rank', '?')}** [{comp.get('title', '')}]({comp.get('url', '')}) — {comp.get('content_type', '')}")
            
            if serp.get("title_patterns"):
                st.markdown("### Title Patterns")
                for p in serp["title_patterns"]:
                    st.markdown(f"- {p}")
            
            if serp.get("content_gaps"):
                st.markdown("### 🎯 Content Gaps (Your Opportunity)")
                for gap in serp["content_gaps"]:
                    st.markdown(f"- {gap}")
            
            if serp.get("differentiation_ideas"):
                st.markdown("### 💡 Differentiation Ideas")
                for idea in serp["differentiation_ideas"]:
                    st.markdown(f"- {idea}")
        
        with tab4:
            if audit.get("recommendations"):
                for rec in audit["recommendations"]:
                    priority = rec.get("priority", "P2")
                    emoji = "🔴" if priority == "P0" else "🟡" if priority == "P1" else "🔵"
                    with st.expander(f"{emoji} [{priority}] {rec.get('action', '')}", expanded=(priority == "P0")):
                        st.markdown(f"**Impact:** {rec.get('impact', '')}")
                        st.markdown(f"**Effort:** {rec.get('effort', '')}")
        
        # CTA
        st.markdown("""
        <div class="cta-box">
            <h2>📈 Want weekly SEO tracking?</h2>
            <p>Cortex Pro monitors your pages automatically and alerts you to SEO changes.</p>
            <a href="https://buy.stripe.com/test_placeholder" style="background:white;color:#667eea;padding:12px 32px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:1rem;">
                Start Pro Trial — $49/mo
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # Download report
        report_md = f"""# SEO Audit Report — {url_input}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Score: {score}/100

## On-Page Analysis
- Title: {audit.get('title_tag', 'N/A')}
- Meta: {audit.get('meta_description', 'N/A')}
- Word Count: {audit.get('word_count', 'N/A')}
- Primary Keyword: {audit.get('primary_keyword', 'N/A')}

## Recommendations
"""
        for rec in audit.get("recommendations", []):
            report_md += f"\n### [{rec.get('priority', '')}] {rec.get('action', '')}\n- Impact: {rec.get('impact', '')}\n- Effort: {rec.get('effort', '')}\n"
        
        st.download_button("📥 Download Full Report (Markdown)", report_md, 
                          file_name=f"seo-audit-{url_input.replace('https://', '').replace('/', '_')}.md",
                          mime="text/markdown")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#9ca3af; padding:1rem;">
    <p>Cortex SEO Audit — Part of the <a href="/">Cortex AI Suite</a></p>
    <p>Powered by Google Gemini • No data stored • Your API keys never leave your browser</p>
</div>
""", unsafe_allow_html=True)
