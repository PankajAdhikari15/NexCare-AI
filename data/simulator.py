"""
NexCare AI  —  data/simulator.py
Generates rich, realistic hospital data. No seed — fresh data on every call.
"""

import random
from datetime import datetime, timedelta

# ── Name pools ────────────────────────────────────────────────────────────────
_MALE_NAMES = [
    "Rajesh Kumar", "Amit Sharma", "Vikram Singh", "Suresh Patel",
    "Rohit Mehta", "Ankit Verma", "Deepak Joshi", "Sanjay Rao",
    "Manish Gupta", "Pradeep Nair", "Arun Mishra", "Dinesh Tiwari",
    "Nikhil Saxena", "Gaurav Pandey", "Harish Chandra", "Ravi Bhatia",
]
_FEMALE_NAMES = [
    "Priya Sharma", "Sunita Devi", "Kavita Singh", "Rekha Patel",
    "Pooja Mehta", "Neha Verma", "Anita Joshi", "Meera Rao",
    "Shikha Gupta", "Radha Nair", "Geeta Mishra", "Savita Tiwari",
    "Divya Kapoor", "Ritu Agarwal", "Swati Bhatia", "Nisha Chauhan",
]
_BLOOD_TYPES = ["A+", "A−", "B+", "B−", "AB+", "AB−", "O+", "O−"]
_INSURANCE   = [
    "Star Health", "HDFC ERGO", "Care Health", "Bajaj Allianz",
    "ICICI Lombard", "Niva Bupa", "Aditya Birla Health", "Govt. CGHS",
]
_CITIES = [
    "New Delhi", "Noida", "Gurgaon", "Faridabad",
    "Ghaziabad", "Greater Noida", "Rohini", "Dwarka",
]

# ── Doctor master list ────────────────────────────────────────────────────────
DOCTORS = [
    {
        "doctor_id":     "D01",
        "name":          "Dr. Rajiv Patel",
        "display":       "Dr. R. Patel",
        "specialty":     "Interventional Cardiology",
        "department":    "Cardiology",
        "qualification": "MBBS, MD, DM (Cardiology), FACC",
        "experience":    "16 years",
        "phone":         "+91-98110-34567",
        "email":         "r.patel@nexcareai.in",
        "available":     True,
        "shift":         "Morning  08:00 – 16:00",
    },
    {
        "doctor_id":     "D02",
        "name":          "Dr. Sunaina Mehta",
        "display":       "Dr. S. Mehta",
        "specialty":     "Cardiac Surgery",
        "department":    "Cardiology",
        "qualification": "MBBS, MS, MCh (Cardiac Surgery)",
        "experience":    "12 years",
        "phone":         "+91-98710-22345",
        "email":         "s.mehta@nexcareai.in",
        "available":     True,
        "shift":         "Evening  16:00 – 00:00",
    },
    {
        "doctor_id":     "D03",
        "name":          "Dr. Arjun Sharma",
        "display":       "Dr. A. Sharma",
        "specialty":     "Neurology",
        "department":    "Neurology",
        "qualification": "MBBS, MD (Neurology), DM",
        "experience":    "11 years",
        "phone":         "+91-99100-56789",
        "email":         "a.sharma@nexcareai.in",
        "available":     True,
        "shift":         "Morning  08:00 – 16:00",
    },
    {
        "doctor_id":     "D04",
        "name":          "Dr. Kavya Nair",
        "display":       "Dr. K. Nair",
        "specialty":     "Pulmonology",
        "department":    "General",
        "qualification": "MBBS, MD (Pulmonology), FCCP",
        "experience":    "9 years",
        "phone":         "+91-97420-11234",
        "email":         "k.nair@nexcareai.in",
        "available":     False,
        "shift":         "Night  00:00 – 08:00",
    },
    {
        "doctor_id":     "D05",
        "name":          "Dr. Vikram Rao",
        "display":       "Dr. V. Rao",
        "specialty":     "Critical Care & ICU",
        "department":    "ICU",
        "qualification": "MBBS, MD (Critical Care), EDIC",
        "experience":    "14 years",
        "phone":         "+91-98230-78901",
        "email":         "v.rao@nexcareai.in",
        "available":     True,
        "shift":         "Morning  08:00 – 16:00",
    },
    {
        "doctor_id":     "D06",
        "name":          "Dr. Priya Verma",
        "display":       "Dr. P. Verma",
        "specialty":     "Diabetology & Endocrinology",
        "department":    "General",
        "qualification": "MBBS, MD (Medicine), DM (Endocrinology)",
        "experience":    "8 years",
        "phone":         "+91-99810-45678",
        "email":         "p.verma@nexcareai.in",
        "available":     True,
        "shift":         "Morning  08:00 – 16:00",
    },
    {
        "doctor_id":     "D07",
        "name":          "Dr. Dinesh Joshi",
        "display":       "Dr. D. Joshi",
        "specialty":     "Nephrology",
        "department":    "Neurology",
        "qualification": "MBBS, MD, DM (Nephrology)",
        "experience":    "13 years",
        "phone":         "+91-98990-23456",
        "email":         "d.joshi@nexcareai.in",
        "available":     True,
        "shift":         "Evening  16:00 – 00:00",
    },
    {
        "doctor_id":     "D08",
        "name":          "Dr. Meera Singh",
        "display":       "Dr. M. Singh",
        "specialty":     "General Medicine",
        "department":    "General",
        "qualification": "MBBS, MD (General Medicine)",
        "experience":    "7 years",
        "phone":         "+91-97560-89012",
        "email":         "m.singh@nexcareai.in",
        "available":     True,
        "shift":         "Morning  08:00 – 16:00",
    },
]

# disease → (department, doctor_id, ward_letter)
_DISEASE_MAP = {
    "Hypertension":   ("Cardiology", "D01", "C"),
    "Cardiac Arrest": ("Cardiology", "D01", "C"),
    "Heart Failure":  ("Cardiology", "D02", "C"),
    "Stroke":         ("Neurology",  "D03", "N"),
    "Epilepsy":       ("Neurology",  "D03", "N"),
    "Kidney Failure": ("Neurology",  "D07", "N"),
    "Pneumonia":      ("General",    "D04", "G"),
    "Asthma":         ("General",    "D04", "G"),
    "Diabetes":       ("General",    "D06", "G"),
    "Sepsis":         ("ICU",        "D05", "I"),
    "COVID-19":       ("ICU",        "D05", "I"),
    "Trauma":         ("ICU",        "D05", "I"),
    "Appendicitis":   ("General",    "D08", "G"),
    "Typhoid":        ("General",    "D08", "G"),
}

_MED_MAP = {
    "Hypertension":   [("Amlodipine","5 mg"),("Telmisartan","40 mg"),("Hydrochlorothiazide","12.5 mg")],
    "Cardiac Arrest": [("Aspirin","150 mg"),("Clopidogrel","75 mg"),("Atorvastatin","40 mg"),("Metoprolol","25 mg")],
    "Heart Failure":  [("Furosemide","40 mg"),("Carvedilol","6.25 mg"),("Spironolactone","25 mg")],
    "Stroke":         [("Aspirin","150 mg"),("Atorvastatin","40 mg"),("Clopidogrel","75 mg")],
    "Epilepsy":       [("Levetiracetam","500 mg"),("Sodium Valproate","200 mg")],
    "Kidney Failure": [("Sodium Bicarbonate","500 mg"),("Calcium Carbonate","500 mg"),("Erythropoietin","4000 IU")],
    "Pneumonia":      [("Amoxicillin-Clavulanate","625 mg"),("Azithromycin","500 mg"),("Dexamethasone","6 mg")],
    "Asthma":         [("Salbutamol Inhaler","200 mcg"),("Budesonide Inhaler","200 mcg"),("Montelukast","10 mg")],
    "Diabetes":       [("Metformin","500 mg"),("Glipizide","5 mg"),("Insulin Glargine","10 units")],
    "Sepsis":         [("Piperacillin-Tazobactam","4.5 g"),("Vancomycin","1 g"),("Norepinephrine","0.1 mcg/kg/min")],
    "COVID-19":       [("Remdesivir","200 mg"),("Dexamethasone","6 mg"),("Enoxaparin","40 mg")],
    "Trauma":         [("Morphine","4 mg"),("Ceftriaxone","1 g"),("Tetanus Toxoid","0.5 ml")],
    "Appendicitis":   [("Metronidazole","500 mg"),("Ceftriaxone","1 g"),("Paracetamol","1 g")],
    "Typhoid":        [("Ceftriaxone","2 g"),("Azithromycin","500 mg"),("Paracetamol","500 mg")],
}

_TX_NOTES = {
    "Admission":              "Patient admitted via {entry}. Vitals recorded. Initial workup and investigations ordered.",
    "Consultation":           "Clinical assessment completed. Treatment plan reviewed and discussed with patient and family.",
    "Procedure":              "Procedure performed under aseptic precautions. Patient tolerated well with no immediate complications.",
    "Observation":            "Patient monitored closely. Vitals recorded every 2 hours. Condition stable. No acute deterioration.",
    "Lab Review":             "Laboratory reports reviewed. Findings discussed with patient. Treatment plan adjusted accordingly.",
    "Medication Adjustment":  "Dosage reviewed and titrated based on clinical response and tolerance. Patient counselled on changes.",
    "Imaging":                "Imaging studies reviewed by radiologist. Findings incorporated into current management plan.",
    "Specialist Review":      "Specialist opinion obtained. Recommendations noted and incorporated into management plan.",
}

_LAB_TESTS = [
    ("Complete Blood Count (CBC)",   "WBC: {w} K/μL,  RBC: {r} M/μL,  HGB: {h} g/dL,  PLT: {p} K/μL"),
    ("Liver Function Test (LFT)",    "ALT: {a} U/L,  AST: {b} U/L,  Total Bilirubin: {c} mg/dL"),
    ("Renal Function Test (RFT)",    "Creatinine: {c:.2f} mg/dL,  BUN: {b} mg/dL,  eGFR: {a} mL/min"),
    ("Blood Glucose (Fasting)",      "Glucose: {a} mg/dL"),
    ("Electrolytes Panel",           "Na⁺: {a} mEq/L,  K⁺: {b:.1f} mEq/L,  Cl⁻: {c} mEq/L"),
    ("Lipid Profile",                "Total Cholesterol: {a} mg/dL,  LDL: {b} mg/dL,  HDL: {c} mg/dL,  TG: {d} mg/dL"),
    ("Troponin I",                   "Troponin I: {a:.3f} ng/mL"),
    ("Coagulation Profile (PT/INR)", "PT: {a:.1f} sec,  INR: {b:.2f}"),
    ("C-Reactive Protein (CRP)",     "CRP: {a:.1f} mg/L"),
    ("HbA1c",                        "HbA1c: {a:.1f}%"),
]


def _rnd_phone() -> str:
    return f"+91-{random.randint(70000,99999)}-{random.randint(10000,99999)}"


def _get_doctor(doc_id: str) -> dict:
    return next((d for d in DOCTORS if d["doctor_id"] == doc_id), DOCTORS[-1])


def _treatment_history(disease: str, adm_str: str) -> list[dict]:
    adm      = datetime.strptime(adm_str, "%d %b %Y")
    days_in  = max(4, (datetime.now() - adm).days)
    n        = random.randint(4, min(8, days_in + 1))
    offsets  = sorted(random.sample(range(days_in + 1), n))
    tx_types = ["Consultation","Procedure","Observation","Lab Review",
                "Medication Adjustment","Imaging","Specialist Review"]
    entries  = []
    for i, off in enumerate(offsets):
        dt   = adm + timedelta(days=off)
        kind = "Admission" if i == 0 else random.choice(tx_types)
        note = _TX_NOTES[kind].replace(
            "{entry}", random.choice(["OPD referral", "Emergency department"])
        ) if kind == "Admission" else _TX_NOTES[kind]
        doc  = _get_doctor(random.choice(["D01","D02","D03","D04","D05","D06","D07","D08"]))
        entries.append({
            "date":        dt.strftime("%d %b %Y"),
            "time":        f"{random.randint(7,21):02d}:{random.choice(['00','15','30','45'])}",
            "type":        kind,
            "description": f"{kind} — {disease}",
            "doctor":      doc["name"],
            "notes":       note,
        })
    return entries


def _medications(disease: str, adm_date: str) -> list[dict]:
    pool = _MED_MAP.get(disease, [("Paracetamol","500 mg"),("Normal Saline","0.9%")])
    freqs  = ["Once daily","Twice daily","Thrice daily","Every 6 hours","Every 8 hours","As needed"]
    routes = ["Oral","IV","IM","Inhalation","Subcutaneous"]
    result = []
    for name, dose in pool[:random.randint(2, len(pool))]:
        result.append({
            "name":       name,
            "dosage":     dose,
            "frequency":  random.choice(freqs),
            "route":      random.choice(routes),
            "start_date": adm_date,
            "status":     "Active",
        })
    if random.random() > 0.6 and pool:
        old = random.choice(pool)
        result.append({
            "name":       old[0],
            "dosage":     old[1],
            "frequency":  "Once daily",
            "route":      "Oral",
            "start_date": adm_date,
            "status":     "Discontinued",
        })
    return result


def _lab_results() -> list[dict]:
    selected = random.sample(_LAB_TESTS, random.randint(3, 5))
    out = []
    for test_name, tpl in selected:
        vals = dict(
            w=round(random.uniform(4.0, 11.0), 1),
            r=round(random.uniform(3.5, 5.5), 1),
            h=round(random.uniform(10.0, 17.0), 1),
            p=random.randint(150, 400),
            a=round(random.uniform(15, 180), 1),
            b=round(random.uniform(15, 150), 1),
            c=round(random.uniform(0.5, 4.0), 1),
            d=random.randint(50, 250),
        )
        out.append({
            "test":       test_name,
            "date":       (datetime.now() - timedelta(days=random.randint(0, 5))).strftime("%d %b %Y"),
            "result":     tpl.format(**vals),
            "status":     random.choice(["Normal","Normal","Normal","Borderline","Abnormal"]),
            "ordered_by": _get_doctor(random.choice(["D01","D02","D03","D04","D05","D06","D07","D08"]))["display"],
        })
    return out


# ── Public API ────────────────────────────────────────────────────────────────
def generate_patients(n: int = 25) -> list[dict]:
    diseases = list(_DISEASE_MAP.keys())
    patients = []

    for i in range(1, n + 1):
        gender  = random.choice(["Male", "Female"])
        name    = random.choice(_MALE_NAMES if gender == "Male" else _FEMALE_NAMES)
        disease = random.choice(diseases)
        dept, doc_id, ward = _DISEASE_MAP[disease]
        doctor  = _get_doctor(doc_id)

        hr   = random.randint(55, 145)
        spo2 = random.randint(84, 100)
        temp = round(random.uniform(96.5, 103.5), 1)
        sbp  = random.randint(90, 190)
        dbp  = random.randint(55, 110)

        is_critical = hr > 120 or spo2 < 90 or temp > 101.5 or sbp > 160

        days_ago      = random.randint(1, 14)
        adm_date      = (datetime.now() - timedelta(days=days_ago)).strftime("%d %b %Y")
        discharge_est = (datetime.now() + timedelta(days=random.randint(1, 7))).strftime("%d %b %Y")

        ec_gender  = "Female" if gender == "Male" else "Male"
        ec_name    = random.choice(_FEMALE_NAMES if ec_gender == "Female" else _MALE_NAMES).split()[0]
        ec_relation = random.choice(
            ["Wife","Mother","Sister","Daughter"] if gender == "Male"
            else ["Husband","Father","Brother","Son"]
        )

        email_name = name.lower().replace(" ", ".")
        pid = f"P{i:02d}"
        patients.append({
            "patient_id":      pid,
            "name":            name,
            "email":           f"{email_name}@nexcare.ai",
            "age":             random.randint(18, 82),
            "gender":          gender,
            "blood_type":      random.choice(_BLOOD_TYPES),
            "phone":           _rnd_phone(),
            "address":         f"{random.randint(1,200)}, Sector {random.randint(1,50)}, {random.choice(_CITIES)}",
            "insurance":       random.choice(_INSURANCE),
            "emergency_contact": {
                "name":     ec_name,
                "relation": ec_relation,
                "phone":    _rnd_phone(),
            },
            "disease":         disease,
            "department":      dept,
            "doctor_id":       doc_id,
            "doctor":          doctor["name"],
            "doctor_display":  doctor["display"],
            "room":            f"{ward}-{random.randint(100, 399)}",
            "ward":            "ICU" if dept == "ICU" else f"{dept} Ward",
            "admission_date":  adm_date,
            "discharge_est":   discharge_est,
            "status":          "Critical" if is_critical else "Stable",
            "heart_rate":      hr,
            "oxygen_level":    spo2,
            "temperature":     temp,
            "bp_systolic":     sbp,
            "bp_diastolic":    dbp,
            "treatment_history": _treatment_history(disease, adm_date),
            "medications":       _medications(disease, adm_date),
            "lab_results":       _lab_results(),
        })
    return patients


def generate_hospital_resources() -> dict:
    tb = random.randint(80, 150);  ob = random.randint(45, tb)
    ts = random.randint(35, 65);   as_ = random.randint(20, ts)
    ta = random.randint(8, 16);    iu = random.randint(2, ta)
    return {
        "beds":       {"total": tb,  "occupied": ob,  "available": tb  - ob},
        "staff":      {"total": ts,  "assigned": as_, "available": ts  - as_},
        "ambulances": {"total": ta,  "in_use": iu,    "available": ta  - iu},
    }


def generate_nearby_hospitals() -> list[dict]:
    hospitals = []
    for name in ["Apollo Hospital","Fortis Healthcare","Max Hospital",
                 "AIIMS Delhi","Medanta","Manipal Hospital"]:
        hospitals.append({
            "name":           name,
            "available_beds": random.randint(0, 45),
            "distance_km":    round(random.uniform(1.2, 18.0), 1),
            "contact":        _rnd_phone(),
        })
    return hospitals
