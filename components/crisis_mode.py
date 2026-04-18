"""
NexCare AI — components/crisis_mode.py
Simulates a hospital crisis and provides AI-driven resource management
with admin Accept / Reject controls (human override).
"""

import random
import streamlit as st

from data.simulator import generate_nearby_hospitals


def _generate_crisis_suggestions(patients: list[dict], resources: dict) -> list[dict]:
    """Generate AI-driven reallocation suggestions for crisis scenario."""
    suggestions = []
    beds = resources.get("beds", {})

    high_risk = [p for p in patients if p.get("risk_level") == "HIGH"]

    for i, patient in enumerate(high_risk[:8]):   # cap at 8 suggestions
        pid        = patient.get("patient_id", f"P{i+1:02d}")
        dept       = patient.get("department", "General")
        score      = patient.get("risk_score", 75)
        doctor     = patient.get("doctor", "Dr. Sharma")
        disease    = patient.get("disease", "Unknown")

        if dept != "ICU":
            suggestions.append({
                "id":     f"SG-{i+1:02d}",
                "type":   "Transfer",
                "icon":   "🚑",
                "text":   (
                    f"Transfer **{pid}** (Risk {score}%, {disease}) "
                    f"from {dept} → ICU. Assign {doctor}."
                ),
                "urgency": "HIGH" if score >= 80 else "MEDIUM",
            })
        else:
            alt_doctor = random.choice([
                "Dr. Patel", "Dr. Mehta", "Dr. Verma", "Dr. Rao"
            ])
            suggestions.append({
                "id":     f"SG-{i+1:02d}",
                "type":   "Doctor",
                "icon":   "👨‍⚕️",
                "text":   (
                    f"Assign additional physician **{alt_doctor}** to {pid} "
                    f"in ICU. Risk score {score}%."
                ),
                "urgency": "HIGH" if score >= 80 else "MEDIUM",
            })

    # Bed reallocation suggestion
    available_beds = beds.get("available", 0)
    if available_beds < 10:
        suggestions.append({
            "id":     "SG-BED",
            "type":   "Beds",
            "icon":   "🛏️",
            "text":   (
                f"Only **{available_beds} beds** remaining. "
                "Request emergency bed allocation from nearby hospitals."
            ),
            "urgency": "HIGH",
        })

    return suggestions


def render_crisis_mode(
    patients: list[dict],
    resources: dict,
) -> None:
    st.markdown("## 🆘 Crisis Mode")

    # Toggle
    crisis_active = st.toggle(
        "🚨 Activate Crisis Mode",
        value=st.session_state.get("crisis_active", False),
        help="Simulates an emergency patient surge and activates AI reallocation.",
    )
    st.session_state["crisis_active"] = crisis_active

    if not crisis_active:
        st.info("Crisis Mode is **OFF**. Toggle the switch above to simulate an emergency surge.")
        return

    # ------------------------------------------------------------------ #
    # CRISIS BANNER
    # ------------------------------------------------------------------ #
    st.markdown(
        """
<div class="crisis-banner">
🚨 CRISIS MODE ACTIVE — Emergency Patient Surge Detected 🚨<br/>
<span style="font-size:0.85rem;font-weight:400;">
AI is generating reallocation suggestions. All actions require admin approval.
</span>
</div>
        """,
        unsafe_allow_html=True,
    )

    # Simulate surge stats
    surge_patients  = random.randint(15, 30)
    surge_beds_lost = random.randint(10, 20)
    surge_staff_lost= random.randint(5, 12)

    s1, s2, s3 = st.columns(3)
    s1.metric("🆕 Surge Patients Incoming",  surge_patients,   delta="↑ Emergency")
    s2.metric("🛏️ Beds Lost to Surge",       surge_beds_lost,  delta=f"−{surge_beds_lost}", delta_color="inverse")
    s3.metric("👨‍⚕️ Staff Reassigned",        surge_staff_lost, delta=f"−{surge_staff_lost}", delta_color="inverse")

    st.markdown("---")

    # ------------------------------------------------------------------ #
    # NEARBY HOSPITALS
    # ------------------------------------------------------------------ #
    st.markdown("#### 🗺️ Nearby Hospital Bed Availability")
    nearby = generate_nearby_hospitals()

    cols = st.columns(len(nearby))
    for col, hosp in zip(cols, nearby):
        beds_avail = hosp["available_beds"]
        color = "#22c55e" if beds_avail >= 15 else ("#f59e0b" if beds_avail >= 5 else "#ef4444")
        col.markdown(
            f"""
<div class="nearby-card" style="border-top: 3px solid {color};">
<div class="nearby-name">{hosp['name']}</div>
<div class="nearby-beds" style="color:{color};">{beds_avail} beds</div>
<div class="nearby-dist">📍 {hosp['distance_km']} km</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ------------------------------------------------------------------ #
    # AI SUGGESTIONS + ACCEPT / REJECT
    # ------------------------------------------------------------------ #
    st.markdown("#### 🤖 AI Resource Reallocation Suggestions")
    st.caption("Every suggestion below requires your approval. The AI assists — it never decides alone.")

    suggestions = _generate_crisis_suggestions(patients, resources)

    # Initialise tracking dicts in session state
    if "accepted_suggestions" not in st.session_state:
        st.session_state["accepted_suggestions"] = []
    if "rejected_suggestions" not in st.session_state:
        st.session_state["rejected_suggestions"] = []

    # Filter out already-actioned suggestions
    actioned = (
        st.session_state["accepted_suggestions"] +
        st.session_state["rejected_suggestions"]
    )
    pending = [s for s in suggestions if s["id"] not in actioned]

    if not pending:
        st.success("✅ All AI suggestions have been reviewed.")
    else:
        for sug in pending:
            urgency_color = "#ef4444" if sug["urgency"] == "HIGH" else "#f59e0b"
            with st.container():
                st.markdown(
                    f"""
<div class="suggestion-card" style="border-left: 4px solid {urgency_color};">
<span class="sug-icon">{sug['icon']}</span>
<span class="sug-id" style="color:{urgency_color};">[{sug['id']}]</span>
&nbsp;{sug['text']}
</div>
                    """,
                    unsafe_allow_html=True,
                )
                btn_col1, btn_col2, _ = st.columns([1, 1, 6])
                if btn_col1.button("✅ Accept", key=f"accept_{sug['id']}"):
                    st.session_state["accepted_suggestions"].append(sug["id"])
                    st.rerun()
                if btn_col2.button("❌ Reject", key=f"reject_{sug['id']}"):
                    st.session_state["rejected_suggestions"].append(sug["id"])
                    st.rerun()

    # ------------------------------------------------------------------ #
    # DECISION LOG
    # ------------------------------------------------------------------ #
    accepted = st.session_state["accepted_suggestions"]
    rejected = st.session_state["rejected_suggestions"]

    if accepted or rejected:
        st.markdown("#### 📋 Admin Decision Log")
        log_col1, log_col2 = st.columns(2)

        with log_col1:
            st.markdown("**✅ Accepted**")
            for sid in accepted:
                st.markdown(f"- {sid}")

        with log_col2:
            st.markdown("**❌ Rejected**")
            for sid in rejected:
                st.markdown(f"- {sid}")

        if st.button("🔄 Reset Decision Log"):
            st.session_state["accepted_suggestions"] = []
            st.session_state["rejected_suggestions"]  = []
            st.rerun()
