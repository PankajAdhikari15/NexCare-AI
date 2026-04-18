"""
NexCare AI  —  pages/1_Admin_Panel.py
Hospital Admin dashboard: resources, patient table, alerts, charts, crisis, sustainability.
"""

import os, sys, datetime
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(
    page_title="NexCare AI — Admin Panel",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

_css = os.path.join(os.path.dirname(__file__), "..", "assets", "admin_style.css")
if os.path.exists(_css):
    with open(_css) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from data.simulator  import generate_patients, generate_hospital_resources, generate_nearby_hospitals
from ai.risk_engine  import process_all_patients
from components.patient_table  import render_patient_table
from components.alerts         import render_alerts
from components.resources      import render_resources
from components.charts         import render_charts
from components.crisis_mode    import render_crisis_mode
from components.sustainability import render_sustainability

# ── Data Persistence & Loading ───────────────────────────────────────────────
if "patients" not in st.session_state:
    st.session_state.patients = process_all_patients(generate_patients(30))
if "resources" not in st.session_state:
    st.session_state.resources = generate_hospital_resources()

patients  = st.session_state.patients
resources = st.session_state.resources
now       = datetime.datetime.now().strftime("%d %b %Y  %H:%M:%S")

# ── Top Navigation Bar ────────────────────────────────────────────────────────
st.markdown("### ⚙️ Dashboard Controls")
nav_cols = st.columns([2, 1, 1, 3])

with nav_cols[0]:
    section = st.selectbox("View Section:", [
        "🏠 Overview", "🛏️ Resources", "🧑 Patients",
        "🚨 Alerts", "📊 Charts", "🆘 Crisis Mode", "🌿 Sustainability"
    ])

with nav_cols[1]:
    # Filter toggle for Critical/Medium patients
    only_critical = st.checkbox("High/Med Risk Only", value=True)

with nav_cols[2]:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.session_state.patients = process_all_patients(generate_patients(30))
        st.session_state.resources = generate_hospital_resources()
        st.rerun()

# ── Filter Patients ───────────────────────────────────────────────────────────
if only_critical:
    display_patients = [p for p in patients if p.get("risk_level") in ("HIGH", "MEDIUM") or p.get("status") == "Critical"]
else:
    display_patients = patients

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
<div class="admin-header">
<div>
<div class="admin-logo">🏥 NexCare AI</div>
<div style="font-size:0.75rem;color:#475569;margin-top:2px;">
AI-Powered Hospital Monitoring &amp; Alert System
</div>
</div>
<div style="text-align:right;">
<div class="admin-panel-tag">Admin Panel</div>
<div class="admin-timestamp" style="margin-top:6px;">🕒 {now}</div>
</div>
</div>
    """,
    unsafe_allow_html=True,
)

show_all = section == "🏠 Overview"

if show_all or section == "🛏️ Resources":
    st.markdown("---")
    render_resources(resources)

if show_all or section == "🧑 Patients":
    st.markdown("---")
    if only_critical:
        st.info(f"Showing {len(display_patients)} Critical/Medium risk patients (Filter active)")
    render_patient_table(display_patients)

if show_all or section == "🚨 Alerts":
    st.markdown("---")
    render_alerts(display_patients)

if show_all or section == "📊 Charts":
    st.markdown("---")
    render_charts(patients) # Charts should probably show the full picture

if show_all or section == "🌿 Sustainability":
    st.markdown("---")
    render_sustainability()

if show_all or section == "🆘 Crisis Mode":
    st.markdown("---")
    render_crisis_mode(display_patients, resources)

st.markdown(
    "<div style='text-align:center;color:#1e293b;font-size:0.75rem;padding:2rem 0 0;'>"
    "NexCare AI · Admin Panel · Hackathon 2025</div>",
    unsafe_allow_html=True,
)

