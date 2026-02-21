import streamlit as st
from agents import LeadResearcher, calculate_datavex_fit
import time

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="LeadForge AI", layout="wide")

# -------------------- STYLING --------------------
st.markdown("""
<style>
/* BODY BACKGROUND */
body {
    background: linear-gradient(135deg, #1f4037, #99f2c8);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* GLASS CARD */
.glass-card {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(20px);
    border-radius: 25px;
    border: 1px solid rgba(255,255,255,0.25);
    padding: 25px;
    margin-bottom: 30px;
    box-shadow: 0 8px 32px rgba(31,38,135,0.3);
    transition: transform 0.3s, box-shadow 0.3s;
}
.glass-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 50px rgba(31,38,135,0.5);
}

/* HEADINGS */
h1,h2,h3 { color:#ffffff; font-weight:700; }

/* BUTTONS */
.stButton>button {
    background: linear-gradient(90deg,#ff7e5f,#feb47b);
    color:white;
    border-radius:12px;
    font-weight:700;
    height:50px;
    width:100%;
    border:none;
    transition: transform 0.3s, box-shadow 0.3s;
    font-size:16px;
}
.stButton>button:hover { 
    transform: scale(1.05);
    box-shadow: 0 10px 25px rgba(255,126,95,0.6);
}

/* TEXT INPUT / TEXTAREA */
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    border-radius:12px;
    border:1px solid rgba(255,255,255,0.3);
    background: rgba(255,255,255,0.2);
    color:#0b1e3d;
    font-weight:500;
    padding:12px;
}

/* TECH ICONS */
.tech-icons img {
    width:50px;
    margin-right:10px;
    transition: transform 0.3s;
}
.tech-icons img:hover { transform: scale(1.3); }

/* PROGRESS BAR COLORS */
.css-1q8dd3e { background: linear-gradient(90deg,#ff7e5f,#feb47b) !important; }

</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.markdown('<h1 style="text-align:center; color:#ffffff;">🚀 LeadForge AI</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#f0f0f0;">Autonomous B2B Intelligence Engine for DataVex</p>', unsafe_allow_html=True)
st.markdown("---")

# -------------------- INPUT --------------------
with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    domain = st.text_input("Enter Company Domain (e.g., flipkart.com)", placeholder="company.com")
    st.markdown('</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    analyze = st.button("Analyze Company")

# -------------------- RESULTS --------------------
if analyze:
    if not domain:
        st.warning("Please enter a company domain.")
        st.stop()

    with st.spinner("Running intelligence engine..."):
        researcher = LeadResearcher()
        research_data = researcher.research_company(domain)
        if "error" in research_data:
            st.error("Failed to fetch company data. Check API key or network.")
            st.stop()
        verdict_data = calculate_datavex_fit(research_data)

    # -------------------- TABS --------------------
    tab1, tab2, tab3 = st.tabs(["📊 Executive Verdict", "🏢 Company Intelligence", "✉️ Outreach"])

    # -------------------- TAB 1 --------------------
    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("## Executive Verdict")
        c1, c2 = st.columns(2)
        c1.metric("Fit Score", f"{verdict_data['score']}/10")
        c2.metric("Decision", verdict_data['verdict'])

        progress = st.progress(0)
        for i in range(int((verdict_data['score']/10)*100)+1):
            progress.progress(i)
            time.sleep(0.01)

        with st.expander("View Score Breakdown"):
            for k,v in verdict_data['breakdown'].items():
                st.write(f"**{k}**: {v}")
        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------- TAB 2 --------------------
    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("## Company Intelligence")
        st.write("**Employees:**", research_data.get("employees","N/A"))
        st.write("**CTO:**", research_data.get("cto_name","N/A"))

        tech_icons = {
            "AWS":"https://img.icons8.com/color/48/000000/amazon-web-services.png",
            "GCP":"https://img.icons8.com/color/48/000000/google-cloud.png",
            "Kubernetes":"https://img.icons8.com/color/48/000000/kubernetes.png",
            "Docker":"https://img.icons8.com/color/48/000000/docker.png",
            "Azure":"https://img.icons8.com/color/48/000000/azure.png"
        }

        st.markdown("**Tech Stack:**")
        icons_html = '<div class="tech-icons">'
        for tech in research_data.get("tech_stack", []):
            if tech in tech_icons:
                icons_html += f'<img src="{tech_icons[tech]}" title="{tech}"/>'
        icons_html += '</div>'
        st.markdown(icons_html, unsafe_allow_html=True)

        st.write("**Growth Signal:**", research_data.get("growth","N/A"))
        st.write("**Cloud Signal:**", research_data.get("cloud_costs","N/A"))

        with st.expander("View Raw Research Data"):
            st.text_area("Raw Text", research_data.get("raw_text",""), height=220)
        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------- TAB 3 --------------------
    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("## Suggested Outreach")
        cto = research_data.get("cto_name") or "CTO"
        email = f"""Subject: Cloud Optimization Opportunity at {domain}

Hi {cto},

Our analysis indicates infrastructure growth and potential cloud inefficiencies at {domain}.

DataVex helps engineering teams reduce cloud spend and automate DevOps pipelines.

Would you be open to a 30-minute technical audit?

Best,
DataVex Team
"""
        st.text_area("Email Draft", email, height=250)
        st.markdown('</div>', unsafe_allow_html=True)