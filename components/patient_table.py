"""
NexCare AI — components/patient_table.py
Renders the main patient monitoring table: colour-coded, sortable by risk.
"""

import streamlit as st
import pandas as pd


def render_patient_table(patients: list[dict]) -> None:
    st.markdown("## 🧑‍⚕️ Patient Monitoring Table")

    if not patients:
        st.warning("No patient data available.")
        return

    df = pd.DataFrame(patients)

    # --- Keep & rename only display columns ---
    display_cols = {
        "patient_id":   "Patient ID",
        "heart_rate":   "Heart Rate (BPM)",
        "oxygen_level": "O₂ Level (%)",
        "temperature":  "Temp (°F)",
        "disease":      "Disease",
        "department":   "Department",
        "doctor":       "Doctor",
        "status":       "Status",
        "risk_score":   "Risk Score",
        "risk_level":   "Risk Level",
    }
    df = df[[c for c in display_cols if c in df.columns]].rename(columns=display_cols)

    # Sort: HIGH first, then MEDIUM, then LOW
    level_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    if "Risk Level" in df.columns:
        df["_sort"] = df["Risk Level"].map(level_order).fillna(3)
        df = df.sort_values("_sort").drop(columns="_sort")

    # --- Styling ---
    def row_style(row):
        if row.get("Risk Level") == "HIGH" or row.get("Status") == "Critical":
            bg = "background-color: rgba(239,68,68,0.12);"
        elif row.get("Risk Level") == "MEDIUM":
            bg = "background-color: rgba(245,158,11,0.10);"
        else:
            bg = "background-color: rgba(34,197,94,0.08);"
        return [bg] * len(row)

    def risk_badge(val):
        colors = {"HIGH": "#ef4444", "MEDIUM": "#f59e0b", "LOW": "#22c55e"}
        c = colors.get(val, "#6b7280")
        return f"color: {c}; font-weight: 700;"

    def status_badge(val):
        return (
            "color: #ef4444; font-weight: 700;"
            if val == "Critical"
            else "color: #22c55e; font-weight: 600;"
        )

    styled = (
        df.style
          .apply(row_style, axis=1)
          .map(risk_badge,   subset=["Risk Level"] if "Risk Level" in df.columns else [])
          .map(status_badge, subset=["Status"]     if "Status"     in df.columns else [])
          .format({"Risk Score": "{:.0f}%"} if "Risk Score" in df.columns else {})
    )

    st.dataframe(styled, use_container_width=True, height=420)

    # --- Quick summary strip ---
    total    = len(df)
    high     = (df["Risk Level"] == "HIGH").sum()   if "Risk Level" in df.columns else 0
    critical = (df["Status"]     == "Critical").sum() if "Status"     in df.columns else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Patients",   total)
    c2.metric("⚠️ High Risk",     high,     delta=f"{high/total*100:.0f}%" if total else "0%")
    c3.metric("🔴 Critical",      critical, delta=f"{critical/total*100:.0f}%" if total else "0%")
