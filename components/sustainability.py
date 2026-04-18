"""
NexCare AI — components/sustainability.py
Simulated energy & sustainability widget — satisfies the sustainability
pillar of the Intelligent Healthcare Ecosystems problem statement.
"""

import random
import streamlit as st
import plotly.graph_objects as go


def _gauge(value: float, max_val: float, title: str, color: str) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": "", "font": {"color": "#e2e8f0", "size": 28}},
            title={"text": title, "font": {"color": "#94a3b8", "size": 13}},
            gauge={
                "axis":  {"range": [0, max_val], "tickcolor": "#94a3b8"},
                "bar":   {"color": color},
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": "rgba(255,255,255,0.1)",
                "steps": [
                    {"range": [0, max_val * 0.4],  "color": "rgba(34,197,94,0.1)"},
                    {"range": [max_val * 0.4, max_val * 0.75], "color": "rgba(245,158,11,0.1)"},
                    {"range": [max_val * 0.75, max_val],       "color": "rgba(239,68,68,0.1)"},
                ],
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=10, l=20, r=20),
        height=200,
        font_color="#e2e8f0",
    )
    return fig


def render_sustainability() -> None:
    st.markdown("## 🌿 Sustainability & Energy Monitor")

    # Simulated values (would come from IoT sensors in production)
    energy_saved      = round(random.uniform(120.0, 380.0), 1)   # kWh saved today
    rooms_optimised   = random.randint(18, 45)                    # HVAC / lights auto-adjusted
    carbon_reduction  = round(energy_saved * 0.233, 1)            # kg CO₂ (UK grid factor)
    energy_used       = round(random.uniform(600.0, 950.0), 1)    # kWh consumed today
    renewable_pct     = random.randint(28, 65)                    # % from renewables

    # ---- Top metrics ----
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("⚡ Energy Saved (kWh)",      f"{energy_saved}",     delta="Today")
    m2.metric("🏠 Rooms Optimised",         rooms_optimised,       delta="Auto-adjusted")
    m3.metric("🌍 CO₂ Reduced (kg)",        f"{carbon_reduction}", delta="vs. baseline")
    m4.metric("🔋 Total Consumed (kWh)",    f"{energy_used}")
    m5.metric("☀️ Renewable Mix (%)",       f"{renewable_pct}%")

    st.markdown("---")

    # ---- Gauges ----
    g1, g2, g3 = st.columns(3)

    with g1:
        st.plotly_chart(
            _gauge(energy_saved, 500, "Energy Saved (kWh)", "#22c55e"),
            use_container_width=True,
        )

    with g2:
        st.plotly_chart(
            _gauge(carbon_reduction, 120, "CO₂ Reduced (kg)", "#6366f1"),
            use_container_width=True,
        )

    with g3:
        st.plotly_chart(
            _gauge(renewable_pct, 100, "Renewable Mix (%)", "#f59e0b"),
            use_container_width=True,
        )

    # ---- Room breakdown table ----
    st.markdown("#### 🏥 Smart Room Optimisation Breakdown")
    room_types = {
        "ICU Wards":        {"lights": random.randint(4, 8),  "hvac": random.randint(3, 6)},
        "General Wards":    {"lights": random.randint(8, 16), "hvac": random.randint(5, 12)},
        "Operating Rooms":  {"lights": random.randint(2, 4),  "hvac": random.randint(2, 4)},
        "Waiting Areas":    {"lights": random.randint(4, 10), "hvac": random.randint(3, 8)},
        "Admin Offices":    {"lights": random.randint(3, 7),  "hvac": random.randint(2, 5)},
    }

    rows_html = ""
    for room, data in room_types.items():
        total_opt = data["lights"] + data["hvac"]
        rows_html += f"""
<tr>
<td>{room}</td>
<td style="text-align:center;">{data['lights']}</td>
<td style="text-align:center;">{data['hvac']}</td>
<td style="text-align:center; color:#22c55e; font-weight:700;">{total_opt}</td>
</tr>
        """

    st.markdown(
        f"""
<div class="sustain-table-wrapper">
<table class="sustain-table">
<thead>
<tr>
<th>Room Type</th>
<th style="text-align:center;">💡 Lights Adjusted</th>
<th style="text-align:center;">❄️ HVAC Adjusted</th>
<th style="text-align:center;">✅ Total Optimised</th>
</tr>
</thead>
<tbody>{rows_html}</tbody>
</table>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "📊 Values are simulated from IoT sensor models. In production, "
        "these connect to BMS (Building Management System) via MQTT/REST API."
    )
