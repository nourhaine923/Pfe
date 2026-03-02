ATTRIBUTE_METADATA = {
    # Demographics
    "recipient_age": {"label": "Recipient Age", "type": "numeric", "unit": "years"},
    "donor_age": {"label": "Donor Age", "type": "numeric", "unit": "years"},
    "sex": {"label": "Sex", "type": "categorical"},
    "foreign_patient": {"label": "Foreign Patient", "type": "boolean"},

    # Morphology
    "height_cm": {"label": "Height", "type": "numeric", "unit": "cm"},
    "weight_kg": {"label": "Weight", "type": "numeric", "unit": "kg"},
    "bmi": {"label": "BMI", "type": "numeric"},

    # Clinical
    "nephropathy": {"label": "Primary Nephropathy", "type": "categorical"},
    "dialysis_type": {"label": "Dialysis Type", "type": "categorical"},
    "dialysis_duration": {"label": "Dialysis Duration", "type": "numeric", "unit": "months"},
    "comorbidities": {"label": "Comorbidities", "type": "categorical"},
    "transplant_rank": {"label": "Transplant Rank", "type": "numeric"},

    # Assessment
    "diabetes": {"label": "Diabetes", "type": "boolean"},
    "hypertension": {"label": "Hypertension", "type": "boolean"},
    "acc": {"label": "ACC", "type": "boolean"},
    "hbsag": {"label": "HBsAg", "type": "boolean"},
    "anti_hcv": {"label": "Anti-HCV", "type": "boolean"},
    "transfusion_history": {"label": "Transfusion History", "type": "boolean"},
    "eer_modality": {"label": "EER Modality", "type": "categorical"},
    "previous_transplants": {"label": "Previous Transplants", "type": "numeric"},
    "etiology_irc": {"label": "Etiology IRC", "type": "categorical"},
    "transplant_delay": {"label": "Transplant Delay", "type": "numeric"},
    "serum_creatinine": {"label": "Serum Creatinine", "type": "numeric", "unit": "µmol/L"},

    # Transplant
    "donor_type": {"label": "Donor Type", "type": "categorical"},
    "cold_ischemia": {"label": "Cold Ischemia Time", "type": "numeric", "unit": "hours"},
    "warm_ischemia": {"label": "Warm Ischemia Time", "type": "numeric", "unit": "minutes"},
    "transplant_location": {"label": "Location", "type": "categorical"},
    "service_origin": {"label": "Service Origin", "type": "categorical"},

    # Immunology
    "blood_compatibility": {"label": "Blood Compatibility", "type": "computed"},
    "hla_matching": {"label": "HLA Matching", "type": "computed"},
}