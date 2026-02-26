from bson import ObjectId
from app.database import db


transplantations = db["transplantations"]
patients = db["patients"]


def extract_score1_attributes(transplantation_id: str):

    tx = transplantations.find_one({"_id": ObjectId(transplantation_id)})
    if not tx:
        raise ValueError("Transplantation not found")

    recipient = patients.find_one({"_id": ObjectId(tx["recipient_id"])})
    donor = patients.find_one({"_id": ObjectId(tx["donor_id"])})

    if not recipient or not donor:
        raise ValueError("Recipient or donor not found")

    assessment = tx.get("preTransplantAssessment", {})
    attributes = {}

    # =========================================================
    # 1️⃣ Recipient Age
    # =========================================================
    recipient_age = recipient.get("clinicalData", {}).get("age_at_transplant", 0)

    if recipient_age < 40:
        attributes["recipient_age"] = "18-40"
    elif recipient_age <= 60:
        attributes["recipient_age"] = "41-60"
    else:
        attributes["recipient_age"] = ">60"

    # =========================================================
    # 2️⃣ Donor Age
    # =========================================================
    donor_age = donor.get("ageAtDonation", 0)

    if 18 <= donor_age <= 35:
        attributes["donor_age"] = "18-35"
    elif donor_age <= 50:
        attributes["donor_age"] = "36-50"
    elif donor_age <= 65:
        attributes["donor_age"] = "51-65"
    else:
        attributes["donor_age"] = "<18 or >65"

    # =========================================================
    # 3️⃣ BMI
    # =========================================================
    height = recipient.get("heightCm", 0)
    weight = recipient.get("weightKg", 0)

    if height > 0:
        bmi = weight / ((height / 100) ** 2)
        if 18.5 <= bmi <= 25:
            attributes["bmi"] = "18.5-25"
        elif bmi <= 30:
            attributes["bmi"] = "25-30"
        else:
            attributes["bmi"] = ">30 or <18.5"

    # =========================================================
    # 4️⃣ Blood Compatibility
    # =========================================================
    recipient_bg = recipient.get("bloodGroup")
    donor_bg = donor.get("bloodGroup")

    if recipient_bg == donor_bg:
        attributes["blood_compatibility"] = "Identical"
    else:
        compatible = {
            "A+": ["A+", "O+"],
            "A-": ["A-", "O-"],
            "B+": ["B+", "O+"],
            "B-": ["B-", "O-"],
            "AB+": ["A+", "B+", "AB+", "O+"],
            "O+": ["O+"],
            "O-": ["O-"]
        }

        if donor_bg in compatible.get(recipient_bg, []):
            attributes["blood_compatibility"] = "Compatible"
        else:
            attributes["blood_compatibility"] = "Incompatible"

    # =========================================================
    # 5️⃣ HLA Matching
    # =========================================================
    recipient_hla = recipient.get("hlaTyping", {})
    donor_hla = donor.get("hlaTyping", {})

    mismatches = 0
    loci = ["hlaA1","hlaA2","hlaB1","hlaB2","hlaDR1","hlaDR2"]

    for locus in loci:
        if recipient_hla.get(locus) != donor_hla.get(locus):
            mismatches += 1

    if mismatches == 0:
        attributes["hla_matching"] = "0/6 mismatches"
    elif mismatches <= 2:
        attributes["hla_matching"] = "1-2/6 mismatches"
    elif mismatches <= 4:
        attributes["hla_matching"] = "3-4/6 mismatches"
    else:
        attributes["hla_matching"] = "5-6/6 mismatches"

    # =========================================================
    # 6️⃣ Donor Type
    # =========================================================
    attributes["donor_type"] = donor.get("donorType")

    # =========================================================
    # 7️⃣ Cold Ischemia
    # =========================================================
    cold = tx.get("coldIschemiaHours", 0)

    if cold < 12:
        attributes["cold_ischemia"] = "<12 hours"
    elif cold <= 18:
        attributes["cold_ischemia"] = "12-18 hours"
    elif cold <= 24:
        attributes["cold_ischemia"] = "18-24 hours"
    else:
        attributes["cold_ischemia"] = ">24 hours"

    # =========================================================
    # 8️⃣ Warm Ischemia
    # =========================================================
    warm = tx.get("warmIschemiaMinutes", 0)

    if warm < 30:
        attributes["warm_ischemia"] = "<30 minutes"
    elif warm <= 45:
        attributes["warm_ischemia"] = "30-45 minutes"
    elif warm <= 60:
        attributes["warm_ischemia"] = "45-60 minutes"
    else:
        attributes["warm_ischemia"] = ">60 minutes"

    # =========================================================
    # 9️⃣ Assessment Fields
    # =========================================================
    attributes["diabetes"] = "True" if assessment.get("diabetes") else "False"
    attributes["hypertension"] = "True" if assessment.get("hypertension") else "False"
    attributes["acc"] = "True" if assessment.get("acc") else "False"
    attributes["hbsag"] = "Positive" if assessment.get("hbsAg") else "Negative"
    attributes["anti_hcv"] = "Positive" if assessment.get("antiHCV") else "Negative"

    # =========================================================
    # 🔟 Previous Transplants
    # =========================================================
    n = assessment.get("numberOfPreviousTransplants", 0)

    if n == 0:
        attributes["previous_transplants"] = "0"
    elif n == 1:
        attributes["previous_transplants"] = "1"
    else:
        attributes["previous_transplants"] = "≥2"

    # =========================================================
    # 1️⃣1️⃣ Nephropathy Type
    # =========================================================
    attributes["nephropathy"] = recipient.get("clinicalData", {}).get("primary_nephropathy")

    # =========================================================
    # 1️⃣2️⃣ EER Modality
    # =========================================================
    attributes["eer_modality"] = assessment.get("eerModality")

    # =========================================================
    # 1️⃣3️⃣ Transfusion History
    # =========================================================
    attributes["transfusion_history"] = "Yes" if assessment.get("transfusion") else "None"

    return attributes