"""
NexCare AI — components/alerts.py
Generates and displays actionable alert cards for HIGH / MEDIUM risk patients.
"""

import streamlit as st

# Suggested action templates keyed on risk level & disease keywords
_ACTIONS = {
    "Cardiac Arrest":  "Initiate cardiac protocol — alert on-call cardiologist immediately.",
    "Heart Failure":   "Administer diuretics, restrict fluids. Notify Cardiology.",
    "Hypertension":    "Monitor BP every 15 min. Start antihypertensive therapy if >180/120.",
    "Stroke":          "Activate stroke code. CT scan within 30 min. Neurology consult.",
    "Sepsis":          "Start sepsis bundle: blood cultures, IV fluids, broad-spectrum antibiotics.",
    "Pneumonia":       "Oxygen supplementation, chest X-ray, pulmonology consult.",
    "Asthma":          "Bronchodilator nebulisation, O₂ therapy, watch for status asthmaticus.",
    "Kidney Failure":  "Renal panel, restrict potassium intake, nephrology consult.",
    "Diabetes":        "Glucose monitoring every hour, insulin drip if needed.",
    "COVID-19":        "Isolate patient, remdesivir protocol, respiratory support if SpO₂ < 94%.",
    "DEFAULT":         "Escalate to attending physician for immediate assessment.",
}

# For ICU transfers
_ICU_THRESHOLD = 80   # risk_score above this → recommend ICU transfer


def _get_suggested_action(patient: dict) -> str:
    disease = patient.get("disease", "")
    action  = _ACTIONS.get(disease, _ACTIONS["DEFAULT"])
    if patient.get("risk_score", 0) >= _ICU_THRESHOLD and patient.get("department") != "ICU":
        action += " 🚨 Transfer to ICU immediately."
    return action


def render_alerts(patients: list[dict]) -> None:
    st.markdown("## 🚨 Smart Alert System")

    at_risk = [
        p for p in patients
        if p.get("risk_level") in ("HIGH", "MEDIUM")
    ]

    if not at_risk:
        st.success("✅ All patients are currently stable. No active alerts.")
        return

    high_count   = sum(1 for p in at_risk if p.get("risk_level") == "HIGH")
    medium_count = sum(1 for p in at_risk if p.get("risk_level") == "MEDIUM")

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("🔴 HIGH Risk Alerts",   high_count)
    col_b.metric("🟡 MEDIUM Risk Alerts", medium_count)
    col_c.metric("📋 Total Active Alerts", len(at_risk))

    st.markdown("---")

    # Responsive 2-column card grid
    left_col, right_col = st.columns(2, gap="medium")

    for idx, patient in enumerate(at_risk):
        pid         = patient.get("patient_id", "—")
        risk_score  = patient.get("risk_score",  0)
        risk_level  = patient.get("risk_level",  "MEDIUM")
        reasons     = patient.get("reasons",     [])
        department  = patient.get("department",  "—")
        doctor      = patient.get("doctor",      "—")
        action      = _get_suggested_action(patient)

        is_high = risk_level == "HIGH"
        border_color  = "#ef4444" if is_high else "#f59e0b"
        badge_bg      = "#ef4444" if is_high else "#f59e0b"
        emoji         = "🔴" if is_high else "🟡"

        card_html = f"""
<div class="alert-card" style="border-left: 4px solid {border_color};">
<div class="alert-header">
<span class="alert-pid">{emoji} Patient {pid}</span>
<span class="alert-badge" style="background:{badge_bg};">{risk_level}</span>
</div>
<div class="alert-score">Risk Score: <strong>{risk_score}%</strong></div>
<div class="alert-info">
<span>🏥 {department}</span>&nbsp;&nbsp;
<span>👨‍⚕️ {doctor}</span>
</div>
<div class="alert-reasons">
<strong>⚠️ Reasons:</strong><br/>
{"<br/>".join(f"• {r}" for r in reasons)}
</div>
<div class="alert-action">
<strong>✅ Suggested Action:</strong><br/>{action}
</div>
</div>
        """

        # Alternate between left and right columns
        target_col = left_col if idx % 2 == 0 else right_col
        target_col.markdown(card_html, unsafe_allow_html=True)
