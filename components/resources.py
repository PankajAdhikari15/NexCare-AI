"""
NexCare AI — components/resources.py
Displays hospital resource availability using metric cards.
Visual indicators turn red when critically low.
"""

import streamlit as st


_LOW_THRESHOLD = 0.20   # ≤ 20 % available → critical


def _availability_color(available: int, total: int) -> str:
    if total == 0:
        return "🔴"
    ratio = available / total
    if ratio <= _LOW_THRESHOLD:
        return "🔴"
    if ratio <= 0.40:
        return "🟡"
    return "🟢"


def _progress_bar_color(available: int, total: int) -> str:
    if total == 0:
        return "#ef4444"
    ratio = available / total
    if ratio <= _LOW_THRESHOLD:
        return "#ef4444"   # red
    if ratio <= 0.40:
        return "#f59e0b"   # amber
    return "#22c55e"       # green


def _resource_card(
    label: str,
    total: int,
    occupied_or_assigned: int,
    available: int,
    icon: str,
) -> None:
    pct        = int((available / total * 100)) if total else 0
    bar_color  = _progress_bar_color(available, total)
    status_dot = _availability_color(available, total)

    html = f"""
<div class="resource-card">
<div class="resource-title">{icon} {label}</div>
<div class="resource-metrics">
<div class="resource-stat">
<div class="stat-number">{total}</div>
<div class="stat-label">Total</div>
</div>
<div class="resource-stat">
<div class="stat-number" style="color:#94a3b8;">{occupied_or_assigned}</div>
<div class="stat-label">In Use</div>
</div>
<div class="resource-stat">
<div class="stat-number" style="color:{bar_color};">{available}</div>
<div class="stat-label">Available {status_dot}</div>
</div>
</div>
<div class="resource-bar-bg">
<div class="resource-bar-fill" style="width:{pct}%; background:{bar_color};"></div>
</div>
<div class="resource-pct" style="color:{bar_color};">{pct}% available</div>
</div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_resources(resources: dict) -> None:
    st.markdown("## 🏥 Hospital Resource Monitor")

    beds        = resources.get("beds",        {})
    staff       = resources.get("staff",       {})
    ambulances  = resources.get("ambulances",  {})

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        _resource_card(
            label="Beds",
            total=beds.get("total", 0),
            occupied_or_assigned=beds.get("occupied", 0),
            available=beds.get("available", 0),
            icon="🛏️",
        )

    with col2:
        _resource_card(
            label="Medical Staff",
            total=staff.get("total", 0),
            occupied_or_assigned=staff.get("assigned", 0),
            available=staff.get("available", 0),
            icon="👨‍⚕️",
        )

    with col3:
        _resource_card(
            label="Ambulances",
            total=ambulances.get("total", 0),
            occupied_or_assigned=ambulances.get("in_use", 0),
            available=ambulances.get("available", 0),
            icon="🚑",
        )

    # Show a banner if any resource is critically low
    low_resources = []
    for name, res in [("Beds", beds), ("Staff", staff), ("Ambulances", ambulances)]:
        t = res.get("total", 1)
        a = res.get("available", 0)
        if t and (a / t) <= _LOW_THRESHOLD:
            low_resources.append(name)

    if low_resources:
        st.error(
            f"⚠️ **Critical Resource Alert**: {', '.join(low_resources)} "
            f"are critically low. Consider activating Crisis Mode."
        )
