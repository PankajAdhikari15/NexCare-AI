"""
NexCare AI — ai/risk_engine.py
The brain of the system: takes patient vitals → risk score + explainable reasons.
Uses rule-based logic (fast, interpretable, hackathon-safe).
"""


def calculate_risk(patient: dict) -> dict:
    """
    Input : one patient dict (from simulator or kaggle_loader)
    Output: dict with keys — risk_score (0-100), risk_level, reasons (list[str])
    """
    score   = 0
    reasons = []

    # --- Heart Rate ---
    hr = patient.get("heart_rate", 80)
    if hr > 120:
        score += 35
        reasons.append(f"Tachycardia ({hr} BPM)")
    elif hr < 55:
        score += 20
        reasons.append(f"Bradycardia ({hr} BPM)")

    # --- Oxygen Level (SpO2) ---
    spo2 = patient.get("oxygen_level", 98)
    if spo2 < 90:
        score += 45
        reasons.append(f"Hypoxia (SpO₂ {spo2}%)")
    elif spo2 < 95:
        score += 15
        reasons.append(f"Borderline Oxygen ({spo2}%)")

    # --- Temperature ---
    temp = patient.get("temperature", 98.6)
    if temp > 102.5:
        score += 30
        reasons.append(f"High Fever ({temp}°F)")
    elif temp > 100.5:
        score += 15
        reasons.append(f"Pyrexia ({temp}°F)")
    elif temp < 96.5:
        score += 20
        reasons.append(f"Hypothermia Risk ({temp}°F)")

    # --- Blood Pressure (SBP/DBP) ---
    sbp = patient.get("bp_systolic", 120)
    dbp = patient.get("bp_diastolic", 80)
    if sbp > 170 or dbp > 105:
        score += 30
        reasons.append(f"Severe Hypertension ({sbp}/{dbp})")
    elif sbp > 150 or dbp > 95:
        score += 15
        reasons.append(f"Elevated BP ({sbp}/{dbp})")
    elif sbp < 95:
        score += 20
        reasons.append(f"Hypotension ({sbp}/{dbp})")

    # Cap at 100
    score = min(score, 100)

    if score >= 75:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    if not reasons:
        reasons.append("Clinical vitals within normal range")

    return {
        "risk_score": int(score),
        "risk_level": level,
        "reasons":    reasons,
    }


def process_all_patients(patients: list[dict]) -> list[dict]:
    """Enrich every patient dict with risk_score, risk_level, and reasons."""
    enriched = []
    for p in patients:
        risk = calculate_risk(p)
        enriched.append({**p, **risk})
    return enriched
