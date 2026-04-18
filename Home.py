"""
NexCare AI  —  Home.py
Landing page. Presents the three portals with a clean card UI.
Run:  streamlit run Home.py
"""

import os, datetime
import streamlit as st

st.set_page_config(
    page_title="NexCare AI — Healthcare Portal",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Load CSS
_css = os.path.join(os.path.dirname(__file__), "assets", "home_style.css")
if os.path.exists(_css):
    with open(_css) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Hero HTML ─────────────────────────────────────────────────────────────────
st.markdown(
    f"""
<div class="home-hero">
<div class="home-logo">NexCare AI</div>
<div class="home-sub">Intelligent Healthcare Ecosystem</div>
<div class="home-tagline">
AI-driven monitoring · Explainable risk prediction · Real-time resource management
</div>
<div class="portal-grid">

<a href="Admin_Panel" target="_self" class="portal-card portal-admin">
<span class="portal-icon">🖥️</span>
<div class="portal-title">Admin Panel</div>
<div class="portal-desc">
Full hospital command-centre. Monitor all patients, resources, crisis alerts,
charts, and sustainability metrics in real time.
</div>
<span class="portal-badge badge-admin">Hospital Staff Only</span>
</a>

<a href="Patient_Portal" target="_self" class="portal-card portal-patient">
<span class="portal-icon">🧑‍⚕️</span>
<div class="portal-title">Patient Portal</div>
<div class="portal-desc">
View your health records, current vitals, treatment timeline, medications,
and lab results using your Patient ID.
</div>
<span class="portal-badge badge-patient">Patients</span>
</a>

<a href="Doctor_Panel" target="_self" class="portal-card portal-doctor">
<span class="portal-icon">👨‍⚕️</span>
<div class="portal-title">Doctor Panel</div>
<div class="portal-desc">
Access patient rosters, detailed clinical records, risk alerts, today's
rounds schedule, and ward-level statistics.
</div>
<span class="portal-badge badge-doctor">Doctors Only</span>
</a>

</div>

<div class="home-footer">
NexCare AI · Hackathon 2025 · Click a portal to enter
</div>
</div>
    """,
    unsafe_allow_html=True,
)
