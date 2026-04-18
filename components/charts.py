"""
NexCare AI — components/charts.py
Visual data insights using Plotly charts.
  - Bar chart: LOW / MEDIUM / HIGH risk distribution
  - Pie chart:  patient distribution by department
  - Line chart: vital-signs scatter for risk correlation
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


_RISK_COLORS = {
    "LOW":    "#22c55e",
    "MEDIUM": "#f59e0b",
    "HIGH":   "#ef4444",
}

_DEPT_COLORS = px.colors.qualitative.Pastel


def render_charts(patients: list[dict]) -> None:
    st.markdown("## 📊 Data Visualisation")

    if not patients:
        st.warning("No patient data to visualise.")
        return

    df = pd.DataFrame(patients)

    # --- Row 1: Risk Distribution Bar + Department Pie ---
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("#### Risk Level Distribution")
        risk_counts = (
            df["risk_level"].value_counts()
              .reindex(["HIGH", "MEDIUM", "LOW"], fill_value=0)
              .reset_index()
        )
        risk_counts.columns = ["Risk Level", "Count"]

        fig_bar = go.Figure(
            go.Bar(
                x=risk_counts["Risk Level"],
                y=risk_counts["Count"],
                marker_color=[_RISK_COLORS[r] for r in risk_counts["Risk Level"]],
                text=risk_counts["Count"],
                textposition="outside",
            )
        )
        fig_bar.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            margin=dict(t=20, b=20, l=20, r=20),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
            height=320,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.markdown("#### Patient Distribution by Department")
        dept_counts = df["department"].value_counts().reset_index()
        dept_counts.columns = ["Department", "Count"]

        fig_pie = go.Figure(
            go.Pie(
                labels=dept_counts["Department"],
                values=dept_counts["Count"],
                hole=0.40,
                marker_colors=_DEPT_COLORS[:len(dept_counts)],
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Patients: %{value}<extra></extra>",
            )
        )
        fig_pie.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            margin=dict(t=20, b=20, l=20, r=20),
            height=320,
            showlegend=True,
            legend=dict(font=dict(color="#e2e8f0")),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- Row 2: Heart Rate vs O2 Scatter coloured by Risk ---
    st.markdown("#### Heart Rate vs Oxygen Level (Risk Correlation)")
    fig_scatter = px.scatter(
        df,
        x="heart_rate",
        y="oxygen_level",
        color="risk_level",
        color_discrete_map=_RISK_COLORS,
        hover_data=["patient_id", "disease", "department", "risk_score"],
        labels={
            "heart_rate":   "Heart Rate (BPM)",
            "oxygen_level": "Oxygen Level (%)",
            "risk_level":   "Risk Level",
        },
        size="risk_score",
        size_max=18,
    )
    # Add reference lines
    fig_scatter.add_vline(x=120, line_dash="dash", line_color="#ef4444",
                          annotation_text="HR Threshold", annotation_font_color="#ef4444")
    fig_scatter.add_hline(y=90,  line_dash="dash", line_color="#f59e0b",
                          annotation_text="SpO₂ Threshold", annotation_font_color="#f59e0b")
    fig_scatter.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        margin=dict(t=20, b=40, l=40, r=20),
        height=350,
        legend=dict(font=dict(color="#e2e8f0")),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # --- Row 3: Risk Score histogram ---
    st.markdown("#### Risk Score Distribution")
    fig_hist = px.histogram(
        df,
        x="risk_score",
        nbins=10,
        color_discrete_sequence=["#6366f1"],
        labels={"risk_score": "Risk Score (0–100)"},
    )
    fig_hist.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        margin=dict(t=20, b=40, l=40, r=20),
        height=280,
        bargap=0.05,
    )
    st.plotly_chart(fig_hist, use_container_width=True)
