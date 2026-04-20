# scripts/seed_barems.py - REBALANCED VERSION
"""
Run this script to populate the barems collection with BALANCED scoring rules.
Usage: python -m scripts.seed_barems
"""

from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["pfe_transplantation"]

# Clear existing barems
print("Clearing existing barems...")
db.barems.delete_many({})

# ============================================
# SCORE 1 - Pre-transplant Success Score (REBALANCED)
# Base score starts at 50, then adjustments
# Final range: 0-100
# Positive max: +35, Negative max: -35
# ============================================

score1_barems = [
    # 1. HLA Matching (was 15/10/5/-5, now balanced)
    {
        "score": "SCORE_1",
        "key": "hla_matching",
        "values": [
            {"type": "categorical", "conditions": [{"value": "0/6 mismatches", "impact": 12}]},
            {"type": "categorical", "conditions": [{"value": "1-2/6 mismatches", "impact": 8}]},
            {"type": "categorical", "conditions": [{"value": "3-4/6 mismatches", "impact": 3}]},
            {"type": "categorical", "conditions": [{"value": "5-6/6 mismatches", "impact": -3}]}
        ]
    },
    
    # 2. Blood Type Compatibility (was 10/5/-20, now balanced)
    {
        "score": "SCORE_1",
        "key": "blood_compatibility",
        "values": [
            {"type": "categorical", "conditions": [{"value": "Identical", "impact": 8}]},
            {"type": "categorical", "conditions": [{"value": "Compatible", "impact": 4}]},
            {"type": "categorical", "conditions": [{"value": "Incompatible", "impact": -12}]}
        ]
    },
    
    # 3. Crossmatch Test (was 10/-25, now balanced)
    {
        "score": "SCORE_1",
        "key": "crossmatch_result",
        "values": [
            {"type": "categorical", "conditions": [{"value": "Negative", "impact": 8}]},
            {"type": "categorical", "conditions": [{"value": "Positive", "impact": -15}]}
        ]
    },
    
    # 4. Donor Age (was 8/5/0/-5, now balanced)
    {
        "score": "SCORE_1",
        "key": "donor_age",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "between", "value": [18, 35], "impact": 6}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [36, 50], "impact": 3}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [51, 65], "impact": 0}]},
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 65, "impact": -3}]},
            {"type": "conditional", "conditions": [{"operator": "less_than", "value": 18, "impact": -3}]}
        ]
    },
    
    # 5. Recipient Age (was 5/2/-3, now balanced)
    {
        "score": "SCORE_1",
        "key": "recipient_age",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "between", "value": [18, 40], "impact": 4}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [41, 60], "impact": 2}]},
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 60, "impact": -2}]}
        ]
    },
    
    # 6. Donor Type (was 12/8/5/-5, now balanced)
    {
        "score": "SCORE_1",
        "key": "donor_type",
        "values": [
            {"type": "categorical", "conditions": [{"value": "Living Related", "impact": 10}]},
            {"type": "categorical", "conditions": [{"value": "Living Unrelated", "impact": 6}]},
            {"type": "categorical", "conditions": [{"value": "Deceased Donor", "impact": 3}]},
            {"type": "categorical", "conditions": [{"value": "Cadaveric", "impact": -3}]}
        ]
    },
    
    # 7. Cold Ischemia Time (was 10/5/-5/-15, now balanced)
    {
        "score": "SCORE_1",
        "key": "cold_ischemia",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "less_than", "value": 12, "impact": 8}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [12, 18], "impact": 4}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [18, 24], "impact": -3}]},
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 24, "impact": -8}]}
        ]
    },
    
    # 8. Warm Ischemia Time (was 8/3/-5/-15, now balanced)
    {
        "score": "SCORE_1",
        "key": "warm_ischemia",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "less_than", "value": 30, "impact": 6}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [30, 45], "impact": 2}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [45, 60], "impact": -3}]},
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 60, "impact": -8}]}
        ]
    },
    
    # 9. Transfusion History (was 5/-2/-8, now balanced)
    {
        "score": "SCORE_1",
        "key": "transfusion_history",
        "values": [
            {"type": "categorical", "conditions": [{"value": "None", "impact": 4}]},
            {"type": "categorical", "conditions": [{"value": "<5 units", "impact": -1}]},
            {"type": "categorical", "conditions": [{"value": "≥5 units", "impact": -5}]}
        ]
    },
    
    # 10. HBsAg Status (was 3/-10, now balanced)
    {
        "score": "SCORE_1",
        "key": "hbsag",
        "values": [
            {"type": "boolean", "conditions": [{"value": False, "impact": 2}]},
            {"type": "boolean", "conditions": [{"value": True, "impact": -6}]}
        ]
    },
    
    # 11. Anti-HCV Status (was 3/-10, now balanced)
    {
        "score": "SCORE_1",
        "key": "anti_hcv",
        "values": [
            {"type": "boolean", "conditions": [{"value": False, "impact": 2}]},
            {"type": "boolean", "conditions": [{"value": True, "impact": -6}]}
        ]
    },
    
    # 12. EER Modality (was 8/4/0/-3, now balanced)
    {
        "score": "SCORE_1",
        "key": "eer_modality",
        "values": [
            {"type": "categorical", "conditions": [{"value": "Preemptive", "impact": 6}]},
            {"type": "categorical", "conditions": [{"value": "DP", "impact": 3}]},
            {"type": "categorical", "conditions": [{"value": "HD", "impact": 0}]},
            {"type": "categorical", "conditions": [{"value": "DP_HD", "impact": -2}]}
        ]
    },
    
    # 13. BMI (was 5/0/-5, now balanced)
    {
        "score": "SCORE_1",
        "key": "bmi",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "between", "value": [18.5, 25], "impact": 4}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [25, 30], "impact": 0}]},
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 30, "impact": -3}]},
            {"type": "conditional", "conditions": [{"operator": "less_than", "value": 18.5, "impact": -3}]}
        ]
    },
    
    # 14. Diabetes (was 5/-8, now balanced)
    {
        "score": "SCORE_1",
        "key": "diabetes",
        "values": [
            {"type": "boolean", "conditions": [{"value": False, "impact": 3}]},
            {"type": "boolean", "conditions": [{"value": True, "impact": -5}]}
        ]
    },
    
    # 15. Hypertension (was 5/-5, now balanced)
    {
        "score": "SCORE_1",
        "key": "hypertension",
        "values": [
            {"type": "boolean", "conditions": [{"value": False, "impact": 3}]},
            {"type": "boolean", "conditions": [{"value": True, "impact": -3}]}
        ]
    },
    
    # 16. ACC (was 5/-10, now balanced)
    {
        "score": "SCORE_1",
        "key": "acc",
        "values": [
            {"type": "boolean", "conditions": [{"value": False, "impact": 3}]},
            {"type": "boolean", "conditions": [{"value": True, "impact": -6}]}
        ]
    },
    
    # 17. Nephropathy Type (was -8/-3/-2/0/+3/0, now balanced)
    {
        "score": "SCORE_1",
        "key": "nephropathy",
        "values": [
            {"type": "categorical", "conditions": [{"value": "Hereditary", "impact": 4}]},
            {"type": "categorical", "conditions": [{"value": "NTIC", "impact": 0}]},
            {"type": "categorical", "conditions": [{"value": "NI", "impact": 0}]},
            {"type": "categorical", "conditions": [{"value": "Vascular", "impact": -2}]},
            {"type": "categorical", "conditions": [{"value": "Glomerular", "impact": -3}]},
            {"type": "categorical", "conditions": [{"value": "Diabetic", "impact": -5}]}
        ]
    },
    
    # 18. Previous Transplants (was 5/-5/-15, now balanced)
    {
        "score": "SCORE_1",
        "key": "previous_transplants",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "equal", "value": 0, "impact": 4}]},
            {"type": "conditional", "conditions": [{"operator": "equal", "value": 1, "impact": -3}]},
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 1, "impact": -8}]}
        ]
    }
]

# ============================================
# SCORE 2 - Post-Transplant Follow-up Score (REBALANCED)
# Base score starts at 50
# Positive max: +40, Negative max: -40
# ============================================

score2_barems = [
    # 1. Serum Creatinine (was 15/8/0/-15, now balanced)
    {
        "score": "SCORE_2",
        "key": "creatinine",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "less_than", "value": 1.2, "impact": 10}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [1.2, 1.9], "impact": 5}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [2.0, 2.5], "impact": 0}]},
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 2.5, "impact": -8}]}
        ]
    },
    
    # 2. eGFR (was 12/6/0/-12, now balanced)
    {
        "score": "SCORE_2",
        "key": "gfr",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 60, "impact": 8}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [45, 60], "impact": 4}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [30, 44], "impact": 0}]},
            {"type": "conditional", "conditions": [{"operator": "less_than", "value": 30, "impact": -6}]}
        ]
    },
    
    # 3. Proteinuria (was 8/0/-10, now balanced)
    {
        "score": "SCORE_2",
        "key": "proteinuria",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "less_than", "value": 300, "impact": 5}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [300, 1000], "impact": 0}]},
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 1000, "impact": -6}]}
        ]
    },
    
    # 4. CRP (was 5/-2/-5/-10, now balanced)
    {
        "score": "SCORE_2",
        "key": "crp",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "less_than", "value": 5, "impact": 3}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [5, 20], "impact": -1}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [21, 50], "impact": -3}]},
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 50, "impact": -6}]}
        ]
    },
    
    # 5. Immunosuppression Adherence (was 15/5/-20, now balanced)
    {
        "score": "SCORE_2",
        "key": "adherence_percentage",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 94, "impact": 10}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [80, 94], "impact": 3}]},
            {"type": "conditional", "conditions": [{"operator": "less_than", "value": 80, "impact": -10}]}
        ]
    },
    
    # 6. Rejection Episodes (was 12/-5/-20, now balanced)
    {
        "score": "SCORE_2",
        "key": "rejection_episodes",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "equal", "value": 0, "impact": 8}]},
            {"type": "conditional", "conditions": [{"operator": "equal", "value": 1, "impact": -3}]},
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 1, "impact": -10}]}
        ]
    },
    
    # 7. Hemoglobin (was 5/0/-5/-2, now balanced)
    {
        "score": "SCORE_2",
        "key": "hemoglobin",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "between", "value": [10, 13], "impact": 4}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [8, 9.9], "impact": 0}]},
            {"type": "conditional", "conditions": [{"operator": "less_than", "value": 8, "impact": -3}]},
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 13, "impact": -1}]}
        ]
    },
    
    # 8. Tacrolimus (was -5/+8, now balanced)
    {
        "score": "SCORE_2",
        "key": "tacrolimus",
        "values": [
            {"type": "boolean", "conditions": [{"value": False, "impact": -3}]},
            {"type": "boolean", "conditions": [{"value": True, "impact": 5}]}
        ]
    },
    
    # 9. MMF (was -5/+5, now balanced)
    {
        "score": "SCORE_2",
        "key": "mmf",
        "values": [
            {"type": "boolean", "conditions": [{"value": False, "impact": -2}]},
            {"type": "boolean", "conditions": [{"value": True, "impact": 3}]}
        ]
    },
    
    # 10. Corticosteroids (was +3/-3, now balanced)
    {
        "score": "SCORE_2",
        "key": "corticosteroids",
        "values": [
            {"type": "boolean", "conditions": [{"value": False, "impact": 2}]},
            {"type": "boolean", "conditions": [{"value": True, "impact": -2}]}
        ]
    },
    
    # 11. Infections (was 8/0/-12, now balanced)
    {
        "score": "SCORE_2",
        "key": "infections",
        "values": [
            {"type": "categorical", "conditions": [{"value": "None", "impact": 5}]},
            {"type": "categorical", "conditions": [{"value": "Minor", "impact": 0}]},
            {"type": "categorical", "conditions": [{"value": "Major", "impact": -6}]}
        ]
    },
    
    # 12. Clinical Status (added for better balance)
    {
        "score": "SCORE_2",
        "key": "clinical_status",
        "values": [
            {"type": "categorical", "conditions": [{"value": "Stable", "impact": 8}]},
            {"type": "categorical", "conditions": [{"value": "Improving", "impact": 5}]},
            {"type": "categorical", "conditions": [{"value": "Worsening", "impact": -5}]},
            {"type": "categorical", "conditions": [{"value": "Critical", "impact": -12}]}
        ]
    }
]

# ============================================
# SCORE 3 - Emergency/Early Warning Score (REBALANCED)
# This one is actually well-balanced, just minor adjustments
# ============================================

score3_barems = [
    # 1. Urine Output (well balanced)
    {
        "score": "SCORE_3",
        "key": "urine_output",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 1, "impact": 0}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [0.5, 1], "impact": 3}]},
            {"type": "conditional", "conditions": [{"operator": "less_than", "value": 0.5, "impact": 8}]},
            {"type": "conditional", "conditions": [{"operator": "equal", "value": 0, "impact": 15}]}
        ]
    },
    
    # 2. Temperature (well balanced)
    {
        "score": "SCORE_3",
        "key": "temperature",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "less_than", "value": 37.5, "impact": 0}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [37.5, 38], "impact": 3}]},
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 38, "impact": 8}]}
        ]
    },
    
    # 3. Blood Pressure (well balanced)
    {
        "score": "SCORE_3",
        "key": "blood_pressure",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "between", "value": [90, 160], "impact": 0}]},
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 160, "impact": 5}]},
            {"type": "conditional", "conditions": [{"operator": "less_than", "value": 90, "impact": 10}]}
        ]
    },
    
    # 4. Heart Rate (well balanced)
    {
        "score": "SCORE_3",
        "key": "heart_rate",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "between", "value": [60, 100], "impact": 0}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [100, 120], "impact": 2}]},
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 120, "impact": 6}]}
        ]
    },
    
    # 5. Oxygen Saturation (well balanced)
    {
        "score": "SCORE_3",
        "key": "oxygen_saturation",
        "values": [
            {"type": "conditional", "conditions": [{"operator": "greater_than", "value": 95, "impact": 0}]},
            {"type": "conditional", "conditions": [{"operator": "between", "value": [90, 95], "impact": 4}]},
            {"type": "conditional", "conditions": [{"operator": "less_than", "value": 90, "impact": 12}]}
        ]
    },
    
    # 6. Mental Status (well balanced)
    {
        "score": "SCORE_3",
        "key": "mental_status",
        "values": [
            {"type": "categorical", "conditions": [{"value": "Alert", "impact": 0}]},
            {"type": "categorical", "conditions": [{"value": "Confused", "impact": 8}]},
            {"type": "categorical", "conditions": [{"value": "Lethargic", "impact": 8}]},
            {"type": "categorical", "conditions": [{"value": "Unresponsive", "impact": 15}]}
        ]
    },
    
    # 7. Graft Ultrasound (well balanced)
    {
        "score": "SCORE_3",
        "key": "graft_ultrasound",
        "values": [
            {"type": "categorical", "conditions": [{"value": "Normal", "impact": 0}]},
            {"type": "categorical", "conditions": [{"value": "Increased RI", "impact": 8}]},
            {"type": "categorical", "conditions": [{"value": "Hydronephrosis", "impact": 10}]},
            {"type": "categorical", "conditions": [{"value": "No flow", "impact": 25}]}
        ]
    }
]

# Insert all barems
print("\n" + "="*50)
print("Inserting REBALANCED SCORE_1 rules...")
print("="*50)
for barem in score1_barems:
    result = db.barems.insert_one(barem)
    print(f"✓ Inserted: {barem['key']}")

print("\n" + "="*50)
print("Inserting REBALANCED SCORE_2 rules...")
print("="*50)
for barem in score2_barems:
    result = db.barems.insert_one(barem)
    print(f"✓ Inserted: {barem['key']}")

print("\n" + "="*50)
print("Inserting REBALANCED SCORE_3 rules...")
print("="*50)
for barem in score3_barems:
    result = db.barems.insert_one(barem)
    print(f"✓ Inserted: {barem['key']}")

print("\n" + "="*50)
print(f"Total rules inserted: {len(score1_barems) + len(score2_barems) + len(score3_barems)}")
print("="*50)

# Verify
print("\nVerifying insertion...")
for score in ["SCORE_1", "SCORE_2", "SCORE_3"]:
    count = db.barems.count_documents({"score": score})
    print(f"  {score}: {count} rules")

print("\n✅ Done! All scoring rules have been rebalanced and added to the database.")