"""
NexCare AI  —  pages/2_Patient_Portal.py
Patient-facing portal: login by Patient ID, view profile, vitals,
treatment timeline, medications, lab results, doctor info.
"""

import os, sys
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(
    page_title="NexCare AI — Patient Portal",
    page_icon="🧑‍⚕️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

_css = os.path.join(os.path.dirname(__file__), "..", "assets", "patient_style.css")
if os.path.exists(_css):
    with open(_css) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from data.simulator import generate_patients, DOCTORS
from ai.risk_engine import process_all_patients

# ── Shared data (cached for session so lookup is stable) ──────────────────────
if "all_patients" not in st.session_state:
    # Generate exactly 10 patients as requested
    st.session_state.all_patients = process_all_patients(generate_patients(10))

patients     = st.session_state.all_patients
patient_map  = {p["email"]: p for p in patients}
doctor_map   = {d["doctor_id"]: d for d in DOCTORS}

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="pat-header">
<div>
<div class="pat-header-logo">🏥 NexCare AI</div>
<div class="pat-header-sub">Patient Portal — My Health Records</div>
</div>
</div>
    """,
    unsafe_allow_html=True,
)

# ── Login ─────────────────────────────────────────────────────────────────────
if "pat_logged_in" not in st.session_state:
    st.session_state["pat_logged_in"] = False
    st.session_state["pat_email"]     = None

if not st.session_state["pat_logged_in"]:
    col_l, col_c, col_r = st.columns([1, 1.8, 1])
    with col_c:
        st.markdown(
            """
<div class="pat-login-wrap">
<span class="pat-login-icon">🔐</span>
<div class="pat-login-title">Access Your Records</div>
<div class="pat-login-hint">
Please enter your registered Email ID to view your records.<br/>
<strong>Demo Mode:</strong> Select a patient from the dropdown below.
</div>
            """,
            unsafe_allow_html=True,
        )
        
        # Demo Dropdown
        demo_patient = st.selectbox(
            "Quick Select (Demo):",
            ["-- Select a Patient --"] + [f"{p['name']} ({p['email']})" for p in patients],
            index=0
        )
        
        email_input = ""
        if demo_patient != "-- Select a Patient --":
            email_input = demo_patient.split("(")[1].replace(")", "")
            
        final_email = st.text_input(
            "Email ID",
            value=email_input,
            placeholder="e.g. john.doe@nexcare.ai",
            label_visibility="visible",
        )
        
        if st.button("View My Records →", use_container_width=True):
            email = final_email.strip().lower()
            if email in patient_map:
                st.session_state["pat_logged_in"] = True
                st.session_state["pat_email"]      = email
                st.rerun()
            else:
                st.error(f"Email ID **{email}** not found.")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
<div style='text-align:center;margin-top:1.5rem;font-size:0.78rem;color:#9ca3af;'>
🔒 Your health data is private and secure.<br/>
For assistance, contact the nursing station at your ward.
</div>
            """,
            unsafe_allow_html=True,
        )
    st.stop()

# ── Patient is logged in ──────────────────────────────────────────────────────
p      = patient_map[st.session_state["pat_email"]]

doctor = doctor_map.get(p["doctor_id"], {})

# Sidebar: logout + quick nav
with st.sidebar:
    st.markdown(f"**👋 {p['name'].split()[0]}**")
    st.caption(f"ID: {p['patient_id']}")
    st.markdown("---")
    nav = st.radio("Navigate", [
        "📋 My Overview",
        "💊 Medications",
        "🧪 Lab Results",
        "📅 Treatment History",
        "👨‍⚕️ My Doctor",
    ])
    st.markdown("---")
    if st.button("🚪 Sign Out"):
        st.session_state["pat_logged_in"] = False
        st.session_state["pat_id"]        = None
        st.rerun()

show_all = nav == "📋 My Overview"

# ════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
if show_all:

    # ── Profile card ──────────────────────────────────────────────────────────
    status_emoji = "🔴" if p["status"] == "Critical" else "🟢"
    risk_level   = p.get("risk_level", "LOW")
    risk_emoji   = {"HIGH": "⚠️", "MEDIUM": "🔶", "LOW": "✅"}.get(risk_level, "✅")

    st.markdown(
        f"""
        <div class="pat-profile">
            <div class="pat-pid">PATIENT ID · {p['patient_id']}</div>
            <div class="pat-pname">{p['name']}</div>
            <div class="pat-pmeta">
                {p['age']} yrs · {p['gender']} · Blood Group: {p['blood_type']}
            </div>
            <div class="pat-ptags">
                <span class="pat-tag">🏥 {p['ward']}</span>
                <span class="pat-tag">🚪 Room {p['room']}</span>
                <span class="pat-tag">📅 Admitted {p['admission_date']}</span>
                <span class="pat-tag">🗓️ Est. Discharge {p['discharge_est']}</span>
                <span class="pat-tag">{status_emoji} {p['status']}</span>
                <span class="pat-tag">{risk_emoji} {risk_level} Risk</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Vitals ────────────────────────────────────────────────────────────────
    hr   = p["heart_rate"]
    spo2 = p["oxygen_level"]
    temp = p["temperature"]
    sbp  = p["bp_systolic"]
    dbp  = p["bp_diastolic"]

    st.markdown(
        f"""
        <div class="vitals-grid">
            <div class="vital-card">
                <span class="vital-icon">❤️</span>
                <span class="vital-value {'vital-alert' if hr>120 or hr<55 else ''}">{hr}</span>
                <span class="vital-unit">BPM</span>
                <span class="vital-label">Heart Rate</span>
            </div>
            <div class="vital-card">
                <span class="vital-icon">🫁</span>
                <span class="vital-value {'vital-alert' if spo2<90 else ''}">{spo2}%</span>
                <span class="vital-unit">SpO₂</span>
                <span class="vital-label">Oxygen Level</span>
            </div>
            <div class="vital-card">
                <span class="vital-icon">🌡️</span>
                <span class="vital-value {'vital-alert' if temp>101 else ''}">{temp}°F</span>
                <span class="vital-unit">Fahrenheit</span>
                <span class="vital-label">Temperature</span>
            </div>
            <div class="vital-card">
                <span class="vital-icon">🩸</span>
                <span class="vital-value {'vital-alert' if sbp>160 else ''}">{sbp}/{dbp}</span>
                <span class="vital-unit">mmHg</span>
                <span class="vital-label">Blood Pressure</span>
            </div>
            <div class="vital-card">
                <span class="vital-icon">🦠</span>
                <span class="vital-value">{p['disease']}</span>
                <span class="vital-unit">&nbsp;</span>
                <span class="vital-label">Primary Diagnosis</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Personal info cols ─────────────────────────────────────────────────────
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            f"""
            <div class="section-card">
                <div class="section-title">👤 Personal Information</div>
                <table style="width:100%;font-size:0.85rem;border-collapse:collapse;">
                    <tr><td style="color:#9ca3af;padding:4px 0;width:45%;">Full Name</td>
                        <td style="font-weight:600;color:#1f2937;">{p['name']}</td></tr>
                    <tr><td style="color:#9ca3af;padding:4px 0;">Age</td>
                        <td style="font-weight:600;color:#1f2937;">{p['age']} years</td></tr>
                    <tr><td style="color:#9ca3af;padding:4px 0;">Gender</td>
                        <td style="font-weight:600;color:#1f2937;">{p['gender']}</td></tr>
                    <tr><td style="color:#9ca3af;padding:4px 0;">Blood Group</td>
                        <td style="font-weight:600;color:#1f2937;">{p['blood_type']}</td></tr>
                    <tr><td style="color:#9ca3af;padding:4px 0;">Phone</td>
                        <td style="font-weight:600;color:#1f2937;">{p['phone']}</td></tr>
                    <tr><td style="color:#9ca3af;padding:4px 0;">Address</td>
                        <td style="font-weight:600;color:#1f2937;">{p['address']}</td></tr>
                    <tr><td style="color:#9ca3af;padding:4px 0;">Insurance</td>
                        <td style="font-weight:600;color:#1f2937;">{p['insurance']}</td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        ec = p["emergency_contact"]
        st.markdown(
            f"""
            <div class="section-card">
                <div class="section-title">🚨 Emergency Contact</div>
                <table style="width:100%;font-size:0.85rem;border-collapse:collapse;">
                    <tr><td style="color:#9ca3af;padding:4px 0;width:45%;">Name</td>
                        <td style="font-weight:600;color:#1f2937;">{ec['name']}</td></tr>
                    <tr><td style="color:#9ca3af;padding:4px 0;">Relation</td>
                        <td style="font-weight:600;color:#1f2937;">{ec['relation']}</td></tr>
                    <tr><td style="color:#9ca3af;padding:4px 0;">Phone</td>
                        <td style="font-weight:600;color:#1f2937;">{ec['phone']}</td></tr>
                </table>
                <div style="margin-top:1.4rem;">
                    <div class="section-title" style="margin-bottom:0.6rem;">🏥 Admission Details</div>
                    <table style="width:100%;font-size:0.85rem;border-collapse:collapse;">
                        <tr><td style="color:#9ca3af;padding:4px 0;width:45%;">Department</td>
                            <td style="font-weight:600;color:#1f2937;">{p['department']}</td></tr>
                        <tr><td style="color:#9ca3af;padding:4px 0;">Ward</td>
                            <td style="font-weight:600;color:#1f2937;">{p['ward']}</td></tr>
                        <tr><td style="color:#9ca3af;padding:4px 0;">Room</td>
                            <td style="font-weight:600;color:#1f2937;">{p['room']}</td></tr>
                        <tr><td style="color:#9ca3af;padding:4px 0;">Admitted On</td>
                            <td style="font-weight:600;color:#1f2937;">{p['admission_date']}</td></tr>
                        <tr><td style="color:#9ca3af;padding:4px 0;">Est. Discharge</td>
                            <td style="font-weight:600;color:#1f2937;">{p['discharge_est']}</td></tr>
                    </table>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ════════════════════════════════════════════════════════════════════════════
# MEDICATIONS
# ════════════════════════════════════════════════════════════════════════════
if show_all or nav == "💊 Medications":
    meds         = p.get("medications", [])
    active_meds  = [m for m in meds if m["status"] == "Active"]
    stopped_meds = [m for m in meds if m["status"] == "Discontinued"]

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>💊 Current Medications</div>", unsafe_allow_html=True)

    if active_meds:
        for m in active_meds:
            st.markdown(
                f"""
                <div class="med-pill">
                    <div class="med-name">{m['name']} &nbsp;<span style="font-weight:400;color:#6b7280;">· {m['dosage']}</span></div>
                    <div class="med-sub">{m['frequency']} &nbsp;|&nbsp; Route: {m['route']} &nbsp;|&nbsp; Since {m['start_date']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown("<p style='color:#9ca3af;font-size:0.85rem;'>No active medications.</p>", unsafe_allow_html=True)

    if stopped_meds:
        st.markdown("<div style='margin-top:1rem;font-size:0.8rem;color:#9ca3af;'>Previously prescribed (discontinued):</div>", unsafe_allow_html=True)
        for m in stopped_meds:
            st.markdown(
                f"""
                <div class="med-pill med-pill-disc">
                    <div class="med-name">{m['name']} · {m['dosage']}</div>
                    <div class="med-sub">{m['frequency']} · Discontinued</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# LAB RESULTS
# ════════════════════════════════════════════════════════════════════════════
if show_all or nav == "🧪 Lab Results":
    labs = p.get("lab_results", [])
    status_cls = {"Normal": "lab-status-normal", "Borderline": "lab-status-borderline", "Abnormal": "lab-status-abnormal"}

    rows = ""
    for lab in labs:
        cls = status_cls.get(lab["status"], "")
        rows += f"""
        <tr>
            <td>{lab['test']}</td>
            <td style="font-size:0.78rem;color:#6b7280;">{lab['date']}</td>
            <td style="font-family:monospace;font-size:0.79rem;">{lab['result']}</td>
            <td class="{cls}">{lab['status']}</td>
            <td style="font-size:0.78rem;color:#6b7280;">{lab['ordered_by']}</td>
        </tr>
        """

    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">🧪 Laboratory Results</div>
            <table class="lab-table">
                <thead>
                    <tr>
                        <th>Test</th><th>Date</th><th>Result</th><th>Status</th><th>Ordered By</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ════════════════════════════════════════════════════════════════════════════
# TREATMENT HISTORY
# ════════════════════════════════════════════════════════════════════════════
if show_all or nav == "📅 Treatment History":
    history = p.get("treatment_history", [])
    tl_items = ""
    for i, h in enumerate(history):
        dot_cls = "tl-dot-first" if i == 0 else "tl-dot"
        tl_items += f"""
        <div class="timeline-item">
            <div class="{dot_cls}"></div>
            <div class="tl-date">{h['date']} &nbsp;·&nbsp; {h['time']}</div>
            <div class="tl-type">{h['type']}</div>
            <div class="tl-desc">{h['description']}</div>
            <div style="font-size:0.78rem;color:#9ca3af;margin-top:4px;">
                📝 {h['notes']}<br/>
                👨‍⚕️ {h['doctor']}
            </div>
        </div>
        """

    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">📅 Treatment History</div>
            <div class="timeline">{tl_items}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ════════════════════════════════════════════════════════════════════════════
# MY DOCTOR
# ════════════════════════════════════════════════════════════════════════════
if show_all or nav == "👨‍⚕️ My Doctor":
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">👨‍⚕️ Your Treating Doctor</div>
            <div class="doc-info-card">
                <div class="doc-avatar">👨‍⚕️</div>
                <div>
                    <div class="doc-name">{doctor.get('name', p['doctor'])}</div>
                    <div class="doc-spec">{doctor.get('specialty', 'Specialist')}</div>
                    <div class="doc-phone">📞 {doctor.get('phone', '—')}</div>
                </div>
            </div>
            <table style="width:100%;font-size:0.84rem;border-collapse:collapse;margin-top:1.2rem;">
                <tr><td style="color:#9ca3af;padding:5px 0;width:40%;">Qualification</td>
                    <td style="color:#374151;font-weight:500;">{doctor.get('qualification','—')}</td></tr>
                <tr><td style="color:#9ca3af;padding:5px 0;">Department</td>
                    <td style="color:#374151;font-weight:500;">{doctor.get('department','—')}</td></tr>
                <tr><td style="color:#9ca3af;padding:5px 0;">Experience</td>
                    <td style="color:#374151;font-weight:500;">{doctor.get('experience','—')}</td></tr>
                <tr><td style="color:#9ca3af;padding:5px 0;">Current Shift</td>
                    <td style="color:#374151;font-weight:500;">{doctor.get('shift','—')}</td></tr>
                <tr><td style="color:#9ca3af;padding:5px 0;">Email</td>
                    <td style="color:#374151;font-weight:500;">{doctor.get('email','—')}</td></tr>
            </table>
            <div style="margin-top:1.2rem;background:#f0fdf4;border:1px solid #bbf7d0;
                        border-radius:10px;padding:0.75rem 1rem;font-size:0.82rem;color:#065f46;">
                💬 To speak with your doctor, contact the nursing station at your ward
                or call the hospital helpline. All medical decisions require direct consultation.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
