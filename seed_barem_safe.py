from app.database import db
barem_collection = db["barems"]



def insert_if_not_exists(rule):
    """
    Insert a rule only if it does not already exist.
    A rule is uniquely identified by (score, key, value).
    """

    existing = barem_collection.find_one({
        "score": rule["score"],
        "key": rule["key"],
        "value": rule["value"]
    })

    if existing:
        print(f"✔ Rule already exists → {rule['key']} / {rule['value']}")
    else:
        barem_collection.insert_one(rule)
        print(f"➕ Inserted → {rule['key']} / {rule['value']}")


# -----------------------------
# DEFINE INITIAL MEDICAL RULES
# -----------------------------

initial_rules = [

    # ===== SCORE 1 =====

  { "score": "SCORE_1", "key": "recipient_age", "value": "18-40", "impact": 5 },
  { "score": "SCORE_1", "key": "recipient_age", "value": "41-60", "impact": 3 },
  { "score": "SCORE_1", "key": "recipient_age", "value": ">60", "impact": -2 },

  { "score": "SCORE_1", "key": "donor_age", "value": "18-35", "impact": 8 },
  { "score": "SCORE_1", "key": "donor_age", "value": "36-50", "impact": 5 },
  { "score": "SCORE_1", "key": "donor_age", "value": "51-65", "impact": 2 },
  { "score": "SCORE_1", "key": "donor_age", "value": "<18 or >65", "impact": -5 },

  { "score": "SCORE_1", "key": "bmi", "value": "18.5-25", "impact": 4 },
  { "score": "SCORE_1", "key": "bmi", "value": "25-30", "impact": 2 },
  { "score": "SCORE_1", "key": "bmi", "value": ">30 or <18.5", "impact": -3 },

  { "score": "SCORE_1", "key": "blood_compatibility", "value": "Identical", "impact": 10 },
  { "score": "SCORE_1", "key": "blood_compatibility", "value": "Compatible", "impact": 6 },
  { "score": "SCORE_1", "key": "blood_compatibility", "value": "Incompatible", "impact": -10 },

  { "score": "SCORE_1", "key": "hla_matching", "value": "0/6 mismatches", "impact": 12 },
  { "score": "SCORE_1", "key": "hla_matching", "value": "1-2/6 mismatches", "impact": 8 },
  { "score": "SCORE_1", "key": "hla_matching", "value": "3-4/6 mismatches", "impact": 4 },
  { "score": "SCORE_1", "key": "hla_matching", "value": "5-6/6 mismatches", "impact": -6 },

  { "score": "SCORE_1", "key": "donor_type", "value": "Living", "impact": 10 },
  { "score": "SCORE_1", "key": "donor_type", "value": "Deceased", "impact": 4 },

  { "score": "SCORE_1", "key": "cold_ischemia", "value": "<12 hours", "impact": 10 },
  { "score": "SCORE_1", "key": "cold_ischemia", "value": "12-18 hours", "impact": 6 },
  { "score": "SCORE_1", "key": "cold_ischemia", "value": "18-24 hours", "impact": 2 },
  { "score": "SCORE_1", "key": "cold_ischemia", "value": ">24 hours", "impact": -4 },

  { "score": "SCORE_1", "key": "warm_ischemia", "value": "<30 minutes", "impact": 6 },
  { "score": "SCORE_1", "key": "warm_ischemia", "value": "30-45 minutes", "impact": 3 },
  { "score": "SCORE_1", "key": "warm_ischemia", "value": "45-60 minutes", "impact": 1 },
  { "score": "SCORE_1", "key": "warm_ischemia", "value": ">60 minutes", "impact": -3 },

  { "score": "SCORE_1", "key": "diabetes", "value": "False", "impact": 5 },
  { "score": "SCORE_1", "key": "diabetes", "value": "True", "impact": -6 },

  { "score": "SCORE_1", "key": "hypertension", "value": "False", "impact": 4 },
  { "score": "SCORE_1", "key": "hypertension", "value": "True", "impact": -4 },

  { "score": "SCORE_1", "key": "acc", "value": "False", "impact": 3 },
  { "score": "SCORE_1", "key": "acc", "value": "True", "impact": -5 },

  { "score": "SCORE_1", "key": "hbsag", "value": "Negative", "impact": 2 },
  { "score": "SCORE_1", "key": "hbsag", "value": "Positive", "impact": -8 },

  { "score": "SCORE_1", "key": "anti_hcv", "value": "Negative", "impact": 2 },
  { "score": "SCORE_1", "key": "anti_hcv", "value": "Positive", "impact": -8 },

  { "score": "SCORE_1", "key": "previous_transplants", "value": "0", "impact": 6 },
  { "score": "SCORE_1", "key": "previous_transplants", "value": "1", "impact": 2 },
  { "score": "SCORE_1", "key": "previous_transplants", "value": "≥2", "impact": -6 },

  { "score": "SCORE_1", "key": "transfusion_history", "value": "None", "impact": 4 },
  { "score": "SCORE_1", "key": "transfusion_history", "value": "Yes", "impact": -3 },

  { "score": "SCORE_1", "key": "donor_type", "value": "Living", "impact": 10 },
  { "score": "SCORE_1", "key": "donor_type", "value": "Deceased", "impact": 4 },
  { "score": "SCORE_1", "key": "donor_type", "value": "ECD", "impact": -4 },

  { "score": "SCORE_1", "key": "eer_modality", "value": "HD", "impact": 3 },
  { "score": "SCORE_1", "key": "eer_modality", "value": "PD", "impact": 2 },
  { "score": "SCORE_1", "key": "eer_modality", "value": "Preemptive", "impact": 6 },

  { "score": "SCORE_1", "key": "nephropathy", "value": "Diabetes", "impact": -6 },
  { "score": "SCORE_1", "key": "nephropathy", "value": "Glomerular", "impact": 4 },
  { "score": "SCORE_1", "key": "nephropathy", "value": "Vascular", "impact": -2 },
  { "score": "SCORE_1", "key": "nephropathy", "value": "Hereditary", "impact": 3 },
  { "score": "SCORE_1", "key": "nephropathy", "value": "NTIC", "impact": 2 },
  { "score": "SCORE_1", "key": "nephropathy", "value": "NI", "impact": 1 },




    # ===== SCORE 2 =====
{"score":"SCORE_2","key":"creatinine","value":"<1.2","impact":15},
{"score":"SCORE_2","key":"creatinine","value":"1.2-1.9","impact":8},
{"score":"SCORE_2","key":"creatinine","value":"2.0-2.5","impact":0},
{"score":"SCORE_2","key":"creatinine","value":">2.5","impact":-15},

{"score":"SCORE_2","key":"egfr","value":">60","impact":12},
{"score":"SCORE_2","key":"egfr","value":"45-60","impact":6},
{"score":"SCORE_2","key":"egfr","value":"30-44","impact":0},
{"score":"SCORE_2","key":"egfr","value":"<30","impact":-12},

{"score":"SCORE_2","key":"proteinuria","value":"<0.3g","impact":10},
{"score":"SCORE_2","key":"proteinuria","value":"0.3-1g","impact":5},
{"score":"SCORE_2","key":"proteinuria","value":">1g","impact":-10},

{"score":"SCORE_2","key":"acute_rejection","value":"None","impact":12},
{"score":"SCORE_2","key":"acute_rejection","value":"Treated","impact":4},
{"score":"SCORE_2","key":"acute_rejection","value":"Recurrent","impact":-12},

{"score":"SCORE_2","key":"infection","value":"None","impact":10},
{"score":"SCORE_2","key":"infection","value":"Minor","impact":4},
{"score":"SCORE_2","key":"infection","value":"Major","impact":-10},

{"score":"SCORE_2","key":"hospitalization","value":"None","impact":8},
{"score":"SCORE_2","key":"hospitalization","value":"1_episode","impact":2},
{"score":"SCORE_2","key":"hospitalization","value":">1_episode","impact":-8},

{"score":"SCORE_2","key":"adherence","value":">=95%","impact":15},
{"score":"SCORE_2","key":"adherence","value":"80-94%","impact":5},
{"score":"SCORE_2","key":"adherence","value":"<80%","impact":-20},

{"score":"SCORE_2","key":"blood_pressure_control","value":"Controlled","impact":8},
{"score":"SCORE_2","key":"blood_pressure_control","value":"Partially_controlled","impact":2},
{"score":"SCORE_2","key":"blood_pressure_control","value":"Uncontrolled","impact":-8},

{"score":"SCORE_2","key":"hemoglobin","value":">11","impact":6},
{"score":"SCORE_2","key":"hemoglobin","value":"9-11","impact":2},
{"score":"SCORE_2","key":"hemoglobin","value":"<9","impact":-6},

{"score":"SCORE_2","key":"followup_regular","value":"Regular","impact":10},
{"score":"SCORE_2","key":"followup_regular","value":"Irregular","impact":-10},

{"score":"SCORE_2","key":"graft_ultrasound","value":"Normal","impact":8},
{"score":"SCORE_2","key":"graft_ultrasound","value":"Minor_abnormality","impact":2},
{"score":"SCORE_2","key":"graft_ultrasound","value":"Significant_abnormality","impact":-8},
    # ===== SCORE 3 =====
    # =========================
# SCORE 3 — EMERGENCY SCORE
# =========================

{"score":"SCORE_3","key":"urine_output","value":">1ml/kg/hr","impact":0},
{"score":"SCORE_3","key":"urine_output","value":"0.5-1ml/kg/hr","impact":3},
{"score":"SCORE_3","key":"urine_output","value":"<0.5ml/kg/hr","impact":8},
{"score":"SCORE_3","key":"urine_output","value":"Anuric","impact":15},

{"score":"SCORE_3","key":"fever","value":"<37.5","impact":0},
{"score":"SCORE_3","key":"fever","value":"37.5-38","impact":3},
{"score":"SCORE_3","key":"fever","value":">38","impact":8},

{"score":"SCORE_3","key":"blood_pressure","value":"Stable","impact":0},
{"score":"SCORE_3","key":"blood_pressure","value":"Mild_hypotension","impact":4},
{"score":"SCORE_3","key":"blood_pressure","value":"Severe_hypotension","impact":10},

{"score":"SCORE_3","key":"heart_rate","value":"<100","impact":0},
{"score":"SCORE_3","key":"heart_rate","value":"100-120","impact":3},
{"score":"SCORE_3","key":"heart_rate","value":">120","impact":7},

{"score":"SCORE_3","key":"oxygen_saturation","value":">95%","impact":0},
{"score":"SCORE_3","key":"oxygen_saturation","value":"90-95%","impact":4},
{"score":"SCORE_3","key":"oxygen_saturation","value":"<90%","impact":10},

{"score":"SCORE_3","key":"mental_status","value":"Normal","impact":0},
{"score":"SCORE_3","key":"mental_status","value":"Confused","impact":6},
{"score":"SCORE_3","key":"mental_status","value":"Altered","impact":12},

{"score":"SCORE_3","key":"graft_ultrasound","value":"Normal","impact":0},
{"score":"SCORE_3","key":"graft_ultrasound","value":"Suspicious","impact":5},
{"score":"SCORE_3","key":"graft_ultrasound","value":"Thrombosis_or_rejection","impact":15},

{"score":"SCORE_3","key":"creatinine_rise","value":"<20%","impact":0},
{"score":"SCORE_3","key":"creatinine_rise","value":"20-50%","impact":5},
{"score":"SCORE_3","key":"creatinine_rise","value":">50%","impact":12},

{"score":"SCORE_3","key":"infection_severity","value":"None","impact":0},
{"score":"SCORE_3","key":"infection_severity","value":"Localized","impact":4},
{"score":"SCORE_3","key":"infection_severity","value":"Sepsis","impact":15},
]


# -----------------------------
# RUN SAFE INSERTION
# -----------------------------

print("🌱 Running SAFE Barem Seed...\n")

for rule in initial_rules:
    insert_if_not_exists(rule)

print("\n✅ Safe seed completed.")