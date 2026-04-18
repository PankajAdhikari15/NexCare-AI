"""
NexCare AI  —  pages/3_Doctor_Panel.py
Doctor-facing portal: login → my patients roster, detailed clinical view,
today's rounds, ward stats, lab reviews.
"""

import os, sys, random, datetime
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(
    page_title="NexCare AI — Doctor Panel",
    page_icon="👨‍⚕️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

_css = os.path.join(os.path.dirname(__file__), "..", "assets", "doctor_style.css")
if os.path.exists(_css):
    with open(_css) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Data Persistence & Loading ───────────────────────────────────────────────
if "patients" not in st.session_state:
    from data.simulator import generate_patients, DOCTORS
    from ai.risk_engine import process_all_patients
    st.session_state.patients = process_all_patients(generate_patients(30))

patients = st.session_state.patients
from data.simulator import DOCTORS
doctor_map  = {d["doctor_id"]: d for d in DOCTORS}

# ── Top bar ────────────────────────────────────────────────────────────────────
now_str = datetime.datetime.now().strftime("%d %b %Y  ·  %H:%M")
st.markdown(
    f"""
<div class="doc-topbar">
<div class="doc-logo">Nex<span>Care</span> AI</div>
<div class="doc-panel-label">Doctor Panel &nbsp;·&nbsp; {now_str}</div>
</div>
    """,
    unsafe_allow_html=True,
)

# ── Login ─────────────────────────────────────────────────────────────────────
if "doc_logged_in" not in st.session_state:
    st.session_state["doc_logged_in"] = False
    st.session_state["doc_id"]        = None

if not st.session_state["doc_logged_in"]:
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown(
            """
<div class="doc-login-card">
<div style="font-size:2.2rem;margin-bottom:0.6rem;">命</div>
<div class="doc-login-title">Doctor Sign In</div>
<div class="doc-login-sub">Select your name to access your patient panel</div>
            """,
            unsafe_allow_html=True,
        )
        doc_names = [d["name"] for d in DOCTORS]
        selected  = st.selectbox("Select Doctor", doc_names, label_visibility="collapsed")
        if st.button("Sign In →", use_container_width=True):
            doc = next(d for d in DOCTORS if d["name"] == selected)
            st.session_state["doc_logged_in"] = True
            st.session_state["doc_id"]        = doc["doctor_id"]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style='text-align:center;margin-top:1.2rem;font-size:0.76rem;color:#334155;'>
                🔒 Access restricted to credentialled medical staff only.
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.stop()

# ── Doctor is logged in ────────────────────────────────────────────────────────
doc        = doctor_map[st.session_state["doc_id"]]
my_patients = [p for p in patients if p["doctor_id"] == st.session_state["doc_id"]]

# Sidebar
with st.sidebar:
    st.markdown(f"**{doc['name']}**")
    st.caption(doc["specialty"])
    st.markdown("---")
    nav = st.radio("Navigate", [
        "📊 My Dashboard",
        "🧑‍🤝‍🧑 My Patients",
        "🔬 Patient Detail",
        "📅 Today's Rounds",
        "🚨 Risk Alerts",
    ])
    st.markdown("---")
    if st.button("🚪 Sign Out"):
        st.session_state["doc_logged_in"] = False
        st.session_state["doc_id"]        = None
        st.rerun()

show_all = nav == "📊 My Dashboard"

# ── Doctor profile strip ────────────────────────────────────────────────────────
avail_cls  = "doc-pill-avail" if doc["available"] else ""
avail_text = "🟢 On Duty" if doc["available"] else "🔴 Off Duty"

st.markdown(
    f"""
    <div class="doc-profile-strip">
        <div class="doc-avatar-lg">👨‍⚕️</div>
        <div>
            <div class="doc-name-lg">{doc['name']}</div>
            <div class="doc-specialty-lg">{doc['specialty']}</div>
            <div class="doc-quals">{doc['qualification']} &nbsp;·&nbsp; {doc['experience']} experience</div>
            <div class="doc-pills">
                <span class="doc-pill {avail_cls}">{avail_text}</span>
                <span class="doc-pill">🏥 {doc['department']}</span>
                <span class="doc-pill">⏰ {doc['shift']}</span>
                <span class="doc-pill">✉️ {doc['email']}</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
if show_all or nav == "📊 My Dashboard":

    total      = len(my_patients)
    high_risk  = sum(1 for p in my_patients if p.get("risk_level") == "HIGH")
    medium     = sum(1 for p in my_patients if p.get("risk_level") == "MEDIUM")
    critical   = sum(1 for p in my_patients if p.get("status") == "Critical")
    icu_count  = sum(1 for p in my_patients if p.get("department") == "ICU")

    st.markdown(
        f"""
        <div class="stat-row">
            <div class="stat-card stat-card-blue">
                <div class="stat-number">{total}</div>
                <div class="stat-label">My Patients</div>
            </div>
            <div class="stat-card stat-card-red">
                <div class="stat-number">{high_risk}</div>
                <div class="stat-label">High Risk</div>
            </div>
            <div class="stat-card stat-card-amber">
                <div class="stat-number">{medium}</div>
                <div class="stat-label">Medium Risk</div>
            </div>
            <div class="stat-card stat-card-green">
                <div class="stat-number">{total - critical}</div>
                <div class="stat-label">Stable</div>
            </div>
            <div class="stat-card stat-card-teal">
                <div class="stat-number">{icu_count}</div>
                <div class="stat-label">In ICU</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quick patient roster preview
    if my_patients:
        st.markdown("<div class='doc-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='doc-panel-title'>Quick Patient Overview</div>", unsafe_allow_html=True)

        sorted_pts = sorted(
            my_patients,
            key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(x.get("risk_level","LOW"), 3)
        )
        for p in sorted_pts:
            rl  = p.get("risk_level", "LOW")
            bc  = {"HIGH": "pr-high", "MEDIUM": "pr-medium", "LOW": "pr-low"}.get(rl, "pr-low")
            sc  = "pr-status-critical" if p["status"] == "Critical" else "pr-status-stable"
            st.markdown(
                f"""
                <div class="patient-row">
                    <span class="pr-id">{p['patient_id']}</span>
                    <span class="pr-name">{p['name']}</span>
                    <span class="pr-disease">{p['disease']}</span>
                    <span class="pr-dept">{p['department']}</span>
                    <span class="pr-room">Room {p['room']}</span>
                    <span class="pr-badge {bc}">{rl}</span>
                    <span class="{sc}">{p['status']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No patients currently assigned to you.")

# ════════════════════════════════════════════════════════════════════════════
# MY PATIENTS (full table)
# ════════════════════════════════════════════════════════════════════════════
if show_all or nav == "🧑‍🤝‍🧑 My Patients":
    st.markdown("<div class='doc-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='doc-panel-title'>All Patients Under My Care</div>", unsafe_allow_html=True)

    if not my_patients:
        st.info("No patients currently assigned.")
    else:
        import pandas as pd
        df = pd.DataFrame([{
            "ID":         p["patient_id"],
            "Name":       p["name"],
            "Age":        p["age"],
            "Gender":     p["gender"],
            "Disease":    p["disease"],
            "Department": p["department"],
            "Room":       p["room"],
            "Admitted":   p["admission_date"],
            "Status":     p["status"],
            "Risk":       p.get("risk_level","LOW"),
            "Risk Score": f"{p.get('risk_score',0)}%",
            "BP":         f"{p['bp_systolic']}/{p['bp_diastolic']}",
            "HR":         p["heart_rate"],
            "SpO₂":       f"{p['oxygen_level']}%",
        } for p in my_patients])

        def _risk_color(v):
            if v == "HIGH":   return "color:#f87171;font-weight:700;"
            if v == "MEDIUM": return "color:#fbbf24;font-weight:700;"
            return "color:#86efac;font-weight:600;"

        def _status_color(v):
            return "color:#f87171;font-weight:600;" if v == "Critical" else "color:#86efac;font-weight:600;"

        styled = (
            df.style
              .map(_risk_color,   subset=["Risk"])
              .map(_status_color, subset=["Status"])
        )
        st.dataframe(styled, use_container_width=True, height=460)

    st.markdown("</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PATIENT DETAIL
# ════════════════════════════════════════════════════════════════════════════
if show_all or nav == "🔬 Patient Detail":
    st.markdown("<div class='doc-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='doc-panel-title'>Detailed Clinical Record</div>", unsafe_allow_html=True)

    if not my_patients:
        st.info("No patients assigned.")
    else:
        pid_options = [f"{p['patient_id']} — {p['name']}" for p in my_patients]
        sel = st.selectbox("Select patient", pid_options, label_visibility="collapsed")
        pid = sel.split(" — ")[0]
        p   = next(x for x in my_patients if x["patient_id"] == pid)

        # Vitals row
        hr   = p["heart_rate"];  spo2 = p["oxygen_level"]
        temp = p["temperature"]; sbp  = p["bp_systolic"];  dbp = p["bp_diastolic"]

        def _vp(val, lbl, alert=False):
            cls = "vp-alert" if alert else ""
            return f'<div class="vital-pill {cls}"><span class="vp-val">{val}</span><span class="vp-lbl">{lbl}</span></div>'

        st.markdown(
            f"""
            <div class="vital-row-doc">
                {_vp(hr, "Heart Rate (BPM)", hr>120 or hr<55)}
                {_vp(f"{spo2}%", "SpO₂", spo2<90)}
                {_vp(f"{temp}°F", "Temperature", temp>101)}
                {_vp(f"{sbp}/{dbp}", "BP (mmHg)", sbp>160)}
                {_vp(p['risk_score'], "Risk Score", p.get('risk_level')=='HIGH')}
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2, gap="medium")

        # Patient details
        with c1:
            st.markdown(
                f"""
                <div class="detail-grid">
                    <div class="detail-item"><div class="detail-label">Patient ID</div><div class="detail-value">{p['patient_id']}</div></div>
                    <div class="detail-item"><div class="detail-label">Full Name</div><div class="detail-value">{p['name']}</div></div>
                    <div class="detail-item"><div class="detail-label">Age / Gender</div><div class="detail-value">{p['age']} yrs · {p['gender']}</div></div>
                    <div class="detail-item"><div class="detail-label">Blood Group</div><div class="detail-value">{p['blood_type']}</div></div>
                    <div class="detail-item"><div class="detail-label">Primary Diagnosis</div><div class="detail-value">{p['disease']}</div></div>
                    <div class="detail-item"><div class="detail-label">Department</div><div class="detail-value">{p['department']}</div></div>
                    <div class="detail-item"><div class="detail-label">Room / Ward</div><div class="detail-value">{p['room']} · {p['ward']}</div></div>
                    <div class="detail-item"><div class="detail-label">Status</div><div class="detail-value">{p['status']}</div></div>
                    <div class="detail-item"><div class="detail-label">Admitted</div><div class="detail-value">{p['admission_date']}</div></div>
                    <div class="detail-item"><div class="detail-label">Est. Discharge</div><div class="detail-value">{p['discharge_est']}</div></div>
                    <div class="detail-item"><div class="detail-label">Insurance</div><div class="detail-value">{p['insurance']}</div></div>
                    <div class="detail-item"><div class="detail-label">Phone</div><div class="detail-value">{p['phone']}</div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # AI risk reasons
            reasons = p.get("reasons", [])
            if reasons:
                r_html = "".join(f"<div style='margin-bottom:4px;'>▪ {r}</div>" for r in reasons)
                rl = p.get("risk_level","LOW")
                col_map = {"HIGH":"#f87171","MEDIUM":"#fbbf24","LOW":"#86efac"}
                st.markdown(
                    f"""
                    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);
                                border-radius:10px;padding:0.9rem 1rem;margin-top:0.8rem;">
                        <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;
                                    color:#475569;margin-bottom:0.5rem;">⚠️ AI Risk Assessment</div>
                        <div style="font-size:0.78rem;font-weight:700;color:{col_map[rl]};margin-bottom:0.4rem;">
                            {rl} RISK · Score {p.get('risk_score',0)}%
                        </div>
                        <div style="font-size:0.82rem;color:#94a3b8;line-height:1.7;">{r_html}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Medications
            meds = p.get("medications", [])
            if meds:
                tags = "".join(
                    f'<div class="med-tag{" med-tag-disc" if m["status"]!="Active" else ""}">'
                    f'{m["name"]} {m["dosage"]}'
                    f'</div>'
                    for m in meds
                )
                st.markdown(
                    f"""
                    <div style="margin-top:0.8rem;">
                        <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;
                                    color:#475569;margin-bottom:0.5rem;">💊 Current Medications</div>
                        <div class="med-tags">{tags}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Treatment history + labs
        with c2:
            history = p.get("treatment_history", [])
            tl_html = ""
            for i, h in enumerate(history):
                tl_html += f"""
                <div class="tl-doc-item">
                    <div class="tl-doc-dot"></div>
                    <div class="tl-doc-date">{h['date']} &nbsp;{h['time']}</div>
                    <div class="tl-doc-type">{h['type']}</div>
                    <div class="tl-doc-desc">{h['notes']}</div>
                    <div style="font-size:0.72rem;color:#334155;margin-top:2px;">— {h['doctor']}</div>
                </div>
                """

            st.markdown(
                f"""
                <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;
                            color:#475569;margin-bottom:0.6rem;">📅 Treatment History</div>
                <div class="tl-doc">{tl_html}</div>
                """,
                unsafe_allow_html=True,
            )

            # Lab results
            labs = p.get("lab_results", [])
            if labs:
                lab_rows = ""
                for lab in labs:
                    cls_map = {"Normal":"lab-normal","Borderline":"lab-border","Abnormal":"lab-abnormal"}
                    cls = cls_map.get(lab["status"],"")
                    lab_rows += f"""
                    <tr>
                        <td>{lab['test']}</td>
                        <td style="font-size:0.72rem;color:#475569;">{lab['date']}</td>
                        <td class="{cls}">{lab['status']}</td>
                    </tr>
                    """
                st.markdown(
                    f"""
                    <div style="margin-top:1.2rem;">
                        <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;
                                    color:#475569;margin-bottom:0.6rem;">🧪 Lab Results</div>
                        <table class="lab-tbl-dark">
                            <thead><tr><th>Test</th><th>Date</th><th>Status</th></tr></thead>
                            <tbody>{lab_rows}</tbody>
                        </table>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TODAY'S ROUNDS
# ════════════════════════════════════════════════════════════════════════════
if show_all or nav == "📅 Today's Rounds":
    st.markdown("<div class='doc-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='doc-panel-title'>Today's Rounds Schedule</div>", unsafe_allow_html=True)

    if not my_patients:
        st.info("No patients to schedule rounds for.")
    else:
        # Generate pseudo-schedule
        base_hour = 8
        sorted_for_rounds = sorted(
            my_patients,
            key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(x.get("risk_level","LOW"), 3)
        )
        sched_html = ""
        t = base_hour
        for i, p in enumerate(sorted_for_rounds):
            time_str  = f"{t:02d}:{random.choice(['00','15','30','45'])}"
            note      = "⚠️ Priority review" if p.get("risk_level") == "HIGH" else "Routine round"
            sched_html += f"""
            <div class="sched-item">
                <span class="sched-time">{time_str}</span>
                <div>
                    <div class="sched-name">{p['name']} &nbsp;
                        <span style="font-size:0.72rem;color:#475569;">({p['patient_id']})</span>
                    </div>
                    <div class="sched-room">Room {p['room']} · {p['disease']} · {note}</div>
                </div>
            </div>
            """
            t += random.randint(0, 1)
            if i % 3 == 2:
                t += 1

        st.markdown(sched_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# RISK ALERTS
# ════════════════════════════════════════════════════════════════════════════
if show_all or nav == "🚨 Risk Alerts":
    _ACTIONS = {
        "Cardiac Arrest": "Initiate cardiac protocol immediately.",
        "Heart Failure":  "Administer diuretics, restrict fluids. Recheck in 1 hour.",
        "Hypertension":   "Monitor BP every 15 min. Antihypertensive if >180/120.",
        "Stroke":         "Activate stroke code. CT scan within 30 min.",
        "Sepsis":         "Blood cultures, IV fluids, broad-spectrum antibiotics.",
        "Pneumonia":      "O₂ supplementation, chest X-ray, pulmonology consult.",
        "Kidney Failure": "Renal panel, restrict potassium, nephrology consult.",
        "Diabetes":       "Glucose monitoring every hour. Insulin drip if needed.",
        "COVID-19":       "Isolate patient, remdesivir protocol, respiratory support.",
        "Asthma":         "Bronchodilator nebulisation, O₂ therapy.",
    }
    DEFAULT_ACTION = "Escalate to attending physician immediately."

    at_risk = [p for p in my_patients if p.get("risk_level") in ("HIGH", "MEDIUM")]

    st.markdown("<div class='doc-panel'>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='doc-panel-title'>Risk Alerts — {len(at_risk)} patient(s) require attention</div>",
        unsafe_allow_html=True,
    )

    if not at_risk:
        st.markdown(
            "<div style='color:#86efac;font-size:0.9rem;padding:0.5rem 0;'>✅ All your patients are currently stable.</div>",
            unsafe_allow_html=True,
        )
    else:
        for p in sorted(at_risk, key=lambda x: {"HIGH":0,"MEDIUM":1}.get(x.get("risk_level"),2)):
            rl      = p.get("risk_level", "MEDIUM")
            bc      = "#ef4444" if rl == "HIGH" else "#f59e0b"
            reasons = p.get("reasons", [])
            action  = _ACTIONS.get(p["disease"], DEFAULT_ACTION)
            rlist   = "".join(f"<div style='margin-bottom:3px;'>▪ {r}</div>" for r in reasons)

            st.markdown(
                f"""
                <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);
                            border-left:3px solid {bc};border-radius:12px;padding:1rem 1.1rem;
                            margin-bottom:0.8rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                        <span style="font-weight:700;color:#e2e8f0;">{p['name']}
                            <span style="font-size:0.75rem;color:#64748b;font-weight:400;"> · {p['patient_id']} · Room {p['room']}</span>
                        </span>
                        <span style="background:rgba(255,255,255,0.06);color:{bc};font-size:0.7rem;
                                     font-weight:700;padding:3px 10px;border-radius:999px;
                                     border:1px solid {bc}40;">{rl} RISK · {p.get('risk_score',0)}%</span>
                    </div>
                    <div style="font-size:0.8rem;color:#94a3b8;margin-bottom:0.5rem;">{rlist}</div>
                    <div style="font-size:0.8rem;color:#cbd5e1;background:rgba(255,255,255,0.03);
                                border-radius:8px;padding:0.5rem 0.75rem;">
                        <strong>Suggested:</strong> {action}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)
