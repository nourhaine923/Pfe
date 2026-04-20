# scripts/seed_data.py
"""
Run this script to populate the database with realistic test data.
Usage: python -m scripts.seed_data
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import random
from bson import ObjectId

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["pfe_transplantation"]

# Clear existing data (optional - uncomment if you want fresh data)
print("Clearing existing data...")
db.patients.delete_many({})
db.transplantations.delete_many({})
db.followups.delete_many({})
db.biological_measurements.delete_many({})
db.vitals.delete_many({})
db.immunological_markers.delete_many({})
db.rejections.delete_many({})
db.adverse_events.delete_many({})
db.adherence.delete_many({})
db.treatments.delete_many({})
db.immunosuppression_regimens.delete_many({})
db.crossmatch_tests.delete_many({})
db.outcomes.delete_many({})
db.scores.delete_many({})
print("✅ Existing data cleared")

# ============================================
# HELPER FUNCTIONS
# ============================================

def random_date(start, end):
    """Generate random date between start and end"""
    return start + timedelta(days=random.randint(0, (end - start).days))

def random_blood_group():
    return random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

def random_donor_type():
    return random.choice(["Living Related", "Living Unrelated", "Deceased Donor", "Cadaveric"])

def random_nephropathy():
    return random.choice(["Diabetic", "Glomerular", "Vascular", "NTIC", "Hereditary", "NI"])

def random_eer_modality():
    return random.choice(["Preemptive", "DP", "HD", "DP_HD"])

def random_clinical_status():
    return random.choice(["Stable", "Improving", "Worsening", "Critical"])

def random_mental_status():
    return random.choice(["Alert", "Confused", "Lethargic", "Unresponsive"])

def random_visit_type():
    return random.choice(["Scheduled", "Emergency", "Follow-up"])

# ============================================
# CREATE PATIENTS
# ============================================

print("\n" + "="*50)
print("Creating Patients...")
print("="*50)

# Recipients (5 patients)
recipients = [
    {
        "firstName": "Ahmed",
        "lastName": "Ben Ali",
        "medicalRecordNumber": 1001,
        "sex": "M",
        "bloodGroup": "A+",
        "foreignPatient": False,
        "heightCm": 175,
        "weightKg": 78,
        "patientRole": "recipient",
        "birthDate": datetime(1975, 6, 15),
        "clinicalData": {
            "age_at_transplant": 48,
            "blood_group": "A+",
            "primary_nephropathy": "Diabetic",
            "dialysis_type": "Hemodialysis",
            "dialysis_duration": 24,
            "comorbidities": "Hypertension",
            "transplant_rank": 1
        },
        "hlaTyping": {
            "hlaA1": "A*01:01",
            "hlaA2": "A*02:01",
            "hlaB1": "B*07:02",
            "hlaB2": "B*08:01",
            "hlaDR1": "DRB1*11:04",
            "hlaDR2": "DRB1*15:01",
            "hlaDQ1": "DQB1*03:01",
            "hlaDQ2": "DQB1*02:01"
        },
        "administrativeData": {}
    },
    {
        "firstName": "Fatima",
        "lastName": "Zahra",
        "medicalRecordNumber": 1002,
        "sex": "F",
        "bloodGroup": "O+",
        "foreignPatient": False,
        "heightCm": 162,
        "weightKg": 65,
        "patientRole": "recipient",
        "birthDate": datetime(1980, 3, 22),
        "clinicalData": {
            "age_at_transplant": 43,
            "blood_group": "O+",
            "primary_nephropathy": "Glomerular",
            "dialysis_type": "Peritoneal Dialysis",
            "dialysis_duration": 18,
            "comorbidities": "",
            "transplant_rank": 1
        },
        "hlaTyping": {
            "hlaA1": "A*03:01",
            "hlaA2": "A*11:01",
            "hlaB1": "B*35:01",
            "hlaB2": "B*44:02",
            "hlaDR1": "DRB1*01:01",
            "hlaDR2": "DRB1*04:01",
            "hlaDQ1": "DQB1*05:01",
            "hlaDQ2": "DQB1*06:02"
        },
        "administrativeData": {}
    },
    {
        "firstName": "Mohamed",
        "lastName": "Said",
        "medicalRecordNumber": 1003,
        "sex": "M",
        "bloodGroup": "B+",
        "foreignPatient": True,
        "heightCm": 180,
        "weightKg": 85,
        "patientRole": "recipient",
        "birthDate": datetime(1968, 11, 5),
        "clinicalData": {
            "age_at_transplant": 55,
            "blood_group": "B+",
            "primary_nephropathy": "Vascular",
            "dialysis_type": "Hemodialysis",
            "dialysis_duration": 36,
            "comorbidities": "Hypertension, Diabetes",
            "transplant_rank": 2
        },
        "hlaTyping": {
            "hlaA1": "A*24:02",
            "hlaA2": "A*32:01",
            "hlaB1": "B*15:01",
            "hlaB2": "B*27:05",
            "hlaDR1": "DRB1*07:01",
            "hlaDR2": "DRB1*13:01",
            "hlaDQ1": "DQB1*02:01",
            "hlaDQ2": "DQB1*06:03"
        },
        "administrativeData": {}
    },
    {
        "firstName": "Nadia",
        "lastName": "Khalil",
        "medicalRecordNumber": 1004,
        "sex": "F",
        "bloodGroup": "AB-",
        "foreignPatient": False,
        "heightCm": 168,
        "weightKg": 72,
        "patientRole": "recipient",
        "birthDate": datetime(1985, 7, 30),
        "clinicalData": {
            "age_at_transplant": 38,
            "blood_group": "AB-",
            "primary_nephropathy": "Hereditary",
            "dialysis_type": "Preemptive",
            "dialysis_duration": 0,
            "comorbidities": "",
            "transplant_rank": 1
        },
        "hlaTyping": {
            "hlaA1": "A*02:01",
            "hlaA2": "A*03:01",
            "hlaB1": "B*07:02",
            "hlaB2": "B*14:02",
            "hlaDR1": "DRB1*04:04",
            "hlaDR2": "DRB1*08:01",
            "hlaDQ1": "DQB1*03:02",
            "hlaDQ2": "DQB1*04:02"
        },
        "administrativeData": {}
    },
    {
        "firstName": "Karim",
        "lastName": "Mansour",
        "medicalRecordNumber": 1005,
        "sex": "M",
        "bloodGroup": "O-",
        "foreignPatient": False,
        "heightCm": 172,
        "weightKg": 90,
        "patientRole": "recipient",
        "birthDate": datetime(1960, 1, 10),
        "clinicalData": {
            "age_at_transplant": 63,
            "blood_group": "O-",
            "primary_nephropathy": "Diabetic",
            "dialysis_type": "Hemodialysis",
            "dialysis_duration": 48,
            "comorbidities": "Hypertension, Cardiovascular Disease",
            "transplant_rank": 1
        },
        "hlaTyping": {
            "hlaA1": "A*01:01",
            "hlaA2": "A*68:01",
            "hlaB1": "B*08:01",
            "hlaB2": "B*44:03",
            "hlaDR1": "DRB1*03:01",
            "hlaDR2": "DRB1*11:01",
            "hlaDQ1": "DQB1*02:01",
            "hlaDQ2": "DQB1*03:01"
        },
        "administrativeData": {}
    }
]

# Donors (5 patients)
donors = [
    {
        "firstName": "Sami",
        "lastName": "Ben Ali",
        "medicalRecordNumber": 2001,
        "sex": "M",
        "bloodGroup": "A+",
        "foreignPatient": False,
        "heightCm": 178,
        "weightKg": 80,
        "patientRole": "donor",
        "donorType": "Living Related",
        "ageAtDonation": 35,
        "hlaTyping": {
            "hlaA1": "A*01:01",
            "hlaA2": "A*02:01",
            "hlaB1": "B*07:02",
            "hlaB2": "B*08:01",
            "hlaDR1": "DRB1*11:04",
            "hlaDR2": "DRB1*15:01",
            "hlaDQ1": "DQB1*03:01",
            "hlaDQ2": "DQB1*02:01"
        },
        "administrativeData": {}
    },
    {
        "firstName": "Leila",
        "lastName": "Zahra",
        "medicalRecordNumber": 2002,
        "sex": "F",
        "bloodGroup": "O+",
        "foreignPatient": False,
        "heightCm": 165,
        "weightKg": 68,
        "patientRole": "donor",
        "donorType": "Living Unrelated",
        "ageAtDonation": 42,
        "hlaTyping": {
            "hlaA1": "A*03:01",
            "hlaA2": "A*11:01",
            "hlaB1": "B*35:01",
            "hlaB2": "B*44:02",
            "hlaDR1": "DRB1*01:01",
            "hlaDR2": "DRB1*04:01",
            "hlaDQ1": "DQB1*05:01",
            "hlaDQ2": "DQB1*06:02"
        },
        "administrativeData": {}
    },
    {
        "firstName": "Omar",
        "lastName": "Said",
        "medicalRecordNumber": 2003,
        "sex": "M",
        "bloodGroup": "B+",
        "foreignPatient": False,
        "heightCm": 175,
        "weightKg": 82,
        "patientRole": "donor",
        "donorType": "Deceased Donor",
        "ageAtDonation": 28,
        "hlaTyping": {
            "hlaA1": "A*24:02",
            "hlaA2": "A*32:01",
            "hlaB1": "B*15:01",
            "hlaB2": "B*27:05",
            "hlaDR1": "DRB1*07:01",
            "hlaDR2": "DRB1*13:01",
            "hlaDQ1": "DQB1*02:01",
            "hlaDQ2": "DQB1*06:03"
        },
        "administrativeData": {}
    },
    {
        "firstName": "Sarah",
        "lastName": "Khalil",
        "medicalRecordNumber": 2004,
        "sex": "F",
        "bloodGroup": "AB-",
        "foreignPatient": False,
        "heightCm": 170,
        "weightKg": 70,
        "patientRole": "donor",
        "donorType": "Living Related",
        "ageAtDonation": 36,
        "hlaTyping": {
            "hlaA1": "A*02:01",
            "hlaA2": "A*03:01",
            "hlaB1": "B*07:02",
            "hlaB2": "B*14:02",
            "hlaDR1": "DRB1*04:04",
            "hlaDR2": "DRB1*08:01",
            "hlaDQ1": "DQB1*03:02",
            "hlaDQ2": "DQB1*04:02"
        },
        "administrativeData": {}
    },
    {
        "firstName": "Youssef",
        "lastName": "Mansour",
        "medicalRecordNumber": 2005,
        "sex": "M",
        "bloodGroup": "O-",
        "foreignPatient": False,
        "heightCm": 180,
        "weightKg": 85,
        "patientRole": "donor",
        "donorType": "Cadaveric",
        "ageAtDonation": 45,
        "hlaTyping": {
            "hlaA1": "A*01:01",
            "hlaA2": "A*68:01",
            "hlaB1": "B*08:01",
            "hlaB2": "B*44:03",
            "hlaDR1": "DRB1*03:01",
            "hlaDR2": "DRB1*11:01",
            "hlaDQ1": "DQB1*02:01",
            "hlaDQ2": "DQB1*03:01"
        },
        "administrativeData": {}
    }
]

# Insert recipients
recipient_ids = {}
for recipient in recipients:
    result = db.patients.insert_one(recipient)
    recipient_ids[recipient["lastName"]] = result.inserted_id
    print(f"✓ Created recipient: {recipient['firstName']} {recipient['lastName']}")

# Insert donors
donor_ids = {}
for donor in donors:
    result = db.patients.insert_one(donor)
    donor_ids[donor["lastName"]] = result.inserted_id
    print(f"✓ Created donor: {donor['firstName']} {donor['lastName']}")

# ============================================
# CREATE TRANSPLANTATIONS
# ============================================

print("\n" + "="*50)
print("Creating Transplantations...")
print("="*50)

# Pair recipients with donors
transplant_pairs = [
    (recipient_ids["Ben Ali"], donor_ids["Ben Ali"], "TX-2024-001", datetime(2024, 1, 15)),
    (recipient_ids["Zahra"], donor_ids["Zahra"], "TX-2024-002", datetime(2024, 2, 20)),
    (recipient_ids["Said"], donor_ids["Said"], "TX-2024-003", datetime(2024, 3, 10)),
    (recipient_ids["Khalil"], donor_ids["Khalil"], "TX-2024-004", datetime(2024, 4, 5)),
    (recipient_ids["Mansour"], donor_ids["Mansour"], "TX-2024-005", datetime(2024, 5, 25)),
]

transplantations = []
transplant_dates = {}

for recipient_id, donor_id, tx_number, tx_date in transplant_pairs:
    # Get recipient to access clinical data
    recipient = db.patients.find_one({"_id": recipient_id})
    
    pre_transplant_assessment = {
        "ageAtTransplant": recipient["clinicalData"]["age_at_transplant"],
        "diabetes": "Diabetes" in recipient["clinicalData"].get("comorbidities", ""),
        "hypertension": "Hypertension" in recipient["clinicalData"].get("comorbidities", ""),
        "hbsAg": False,
        "antiHCV": False,
        "transfusion": recipient["clinicalData"].get("transfusion", False),
        "acc": "Cardiovascular" in recipient["clinicalData"].get("comorbidities", ""),
        "nephropathyType": recipient["clinicalData"]["primary_nephropathy"],
        "etiologyIRC": recipient["clinicalData"]["primary_nephropathy"],
        "eerModality": recipient["clinicalData"]["dialysis_type"],
        "eerStartDate": tx_date - timedelta(days=recipient["clinicalData"]["dialysis_duration"] * 30),
        "trDelayMonths": recipient["clinicalData"]["dialysis_duration"],
        "numberOfPreviousTransplants": recipient["clinicalData"]["transplant_rank"] - 1,
        "serumCreatinine": random.choice([1.2, 1.5, 2.0, 2.8, 3.5])
    }
    
    transplantation = {
        "transplantNumber": tx_number,
        "transplantDate": tx_date,
        "transplantLocation": random.choice(["HCN", "RABTA", "HMPIT", "MONASTIR", "SOUSSE", "SFAX"]),
        "serviceOrigin": random.choice(["Nephrology_HCN", "Pediatrics_HCN", "RABTA", "MONASTIR", "SOUSSE"]),
        "coldIschemiaHours": random.choice([6, 8, 10, 12, 15, 18, 22]),
        "warmIschemiaMinutes": random.choice([25, 30, 35, 40, 45, 50, 55, 60]),
        "recipient_id": recipient_id,
        "donor_id": donor_id,
        "preTransplantAssessment": pre_transplant_assessment,
        "status": "APPROVED"
    }
    
    result = db.transplantations.insert_one(transplantation)
    transplantations.append(result.inserted_id)
    transplant_dates[result.inserted_id] = tx_date
    print(f"✓ Created transplantation: {tx_number}")

# ============================================
# CREATE CROSSMATCH TESTS
# ============================================

print("\n" + "="*50)
print("Creating Crossmatch Tests...")
print("="*50)

for tx_id in transplantations:
    tx_date = transplant_dates[tx_id]
    # Create 1-2 crossmatch tests per transplantation
    for i in range(random.randint(1, 2)):
        crossmatch = {
            "testDate": tx_date - timedelta(days=random.randint(5, 30)),
            "methode": random.choice(["CDC", "FlowCytometry", "Virtual"]),
            "result": random.choice(["Negative", "Negative", "Negative", "Positive"]),  # Mostly negative
            "comment": None,
            "transplantation_id": tx_id
        }
        db.crossmatch_tests.insert_one(crossmatch)
    print(f"✓ Created crossmatch tests for transplantation")

# ============================================
# CREATE FOLLOW-UPS AND CLINICAL DATA
# ============================================

print("\n" + "="*50)
print("Creating Follow-ups and Clinical Data...")
print("="*50)

for tx_id in transplantations:
    tx_date = transplant_dates[tx_id]
    recipient = db.patients.find_one({"_id": db.transplantations.find_one({"_id": tx_id})["recipient_id"]})
    
    # Create 3-5 follow-ups per transplantation
    num_followups = random.randint(3, 5)
    
    for i in range(num_followups):
        months_post = i + 1
        visit_date = tx_date + timedelta(days=months_post * 30)
        
        # Calculate post-transplant day
        post_transplant_day = (visit_date - tx_date).days
        
        # Create follow-up
        followup = {
            "visitDate": visit_date,
            "postTransplantDay": post_transplant_day,
            "postTransplantMonth": months_post,
            "visitType": random_visit_type(),
            "clinicalStatus": random_clinical_status(),
            "comment": None,
            "nephropathyRecurrence": random.choice(["None", "None", "None", "Mild", "Moderate"]),
            "transplantation_id": tx_id
        }
        
        followup_result = db.followups.insert_one(followup)
        followup_id = followup_result.inserted_id
        
        # Create Vital Signs
        vital_signs = {
            "dateTime": visit_date,
            "heartRate": random.randint(65, 110),
            "temperature": round(random.uniform(36.5, 38.5), 1),
            "oxygenSaturation": random.randint(92, 99),
            "urineOutputMl": random.randint(800, 2500),
            "mentalStatus": random_mental_status(),
            "bloodPressure": random.randint(110, 160),
            "graftUltraSound": random.choice([None, "Normal", "Normal", "Mild prominence", "Increased RI"]),
            "followup_id": followup_id
        }
        db.vitals.insert_one(vital_signs)
        
        # Create Biological Measurements (deteriorating over time for some patients)
        if months_post <= 2:
            creatinine = round(random.uniform(0.8, 1.5), 1)
            gfr = random.randint(55, 75)
            proteinuria = random.randint(50, 200)
        elif months_post <= 6:
            creatinine = round(random.uniform(1.2, 2.2), 1)
            gfr = random.randint(40, 60)
            proteinuria = random.randint(100, 400)
        else:
            creatinine = round(random.uniform(1.5, 3.5), 1)
            gfr = random.randint(25, 50)
            proteinuria = random.randint(200, 800)
        
        biological = {
            "date": visit_date,
            "creatinine": creatinine,
            "urea": round(random.uniform(20, 60), 1),
            "gfr": gfr,
            "hemoglobin": round(random.uniform(10, 14), 1),
            "crp": round(random.uniform(2, 25), 1),
            "tsh": round(random.uniform(0.5, 4.0), 1),
            "proteinuria": proteinuria,
            "otherBioMarker1": None,
            "otherBioMarker2": None,
            "followup_id": followup_id
        }
        db.biological_measurements.insert_one(biological)
        
        # Create Immunological Markers
        immunological = {
            "markerType": random.choice(["Anti-HLA Class I", "Anti-HLA Class II", "DSA - Donor Specific Antibodies"]),
            "timePoint": f"Month {months_post}",
            "value": round(random.uniform(500, 5000), 0),
            "unit": "MFI",
            "followup_id": followup_id
        }
        db.immunological_markers.insert_one(immunological)
        
        # Create Immunosuppression Regimen
        immunosuppression = {
            "startDate": visit_date,
            "endDate": None,
            "corticosteroids": True,
            "mmf": random.choice([True, False]),
            "azathioprine": random.choice([True, False]),
            "tacrolimus": True,
            "ciclosporine": random.choice([True, False]),
            "sirolimus": random.choice([True, False]),
            "followup_id": followup_id
        }
        db.immunosuppression_regimens.insert_one(immunosuppression)
        
        # Create Therapeutic Treatment
        treatment = {
            "drugName": random.choice(["Tacrolimus (Prograf)", "Mycophenolate Mofetil (CellCept)", "Prednisone"]),
            "dosage": round(random.uniform(2, 10), 1),
            "dosageUnit": "mg",
            "route": "Oral",
            "startDate": visit_date,
            "endDate": None,
            "bloodLevel": round(random.uniform(5, 15), 1),
            "interpretation": None,
            "followup_id": followup_id
        }
        db.treatments.insert_one(treatment)
        
        # Create Adherence Assessment
        adherence = {
            "date": visit_date,
            "adherencePercent": random.randint(75, 100),
            "method": random.choice(["Patient Self-Report", "Pill Count", "Electronic Monitoring"]),
            "followup_id": followup_id
        }
        db.adherence.insert_one(adherence)
        
        # Create Rejection Episodes (for some follow-ups)
        if random.random() < 0.2:  # 20% chance of rejection
            rejection = {
                "date": visit_date,
                "type": random.choice(["Cellular", "AntibodyMediated", "Mixed"]),
                "grade": random.choice(["Borderline", "IA", "IB", "IIA"]),
                "biopsyProven": random.choice([True, False]),
                "treatment": random.choice(["IV Methylprednisolone", "Thymoglobulin", "Rituximab"]),
                "resolved": random.choice([True, False]),
                "followup_id": followup_id
            }
            db.rejections.insert_one(rejection)
        
        # Create Adverse Events (for some follow-ups)
        if random.random() < 0.15:  # 15% chance of adverse event
            adverse_event = {
                "eventType": random.choice(["Infection", "Surgical Complication", "Metabolic Disorder", "Drug Toxicity"]),
                "severity": random.choice(["Mild", "Moderate", "Severe"]),
                "date": visit_date,
                "comment": "Event occurred and was managed appropriately",
                "infectionSeverity": None,
                "infectionType": None,
                "followup_id": followup_id
            }
            db.adverse_events.insert_one(adverse_event)
        
        print(f"  ✓ Created follow-up {months_post} for transplantation")

# ============================================
# CREATE OUTCOMES
# ============================================

print("\n" + "="*50)
print("Creating Outcomes...")
print("="*50)

for tx_id in transplantations:
    tx_date = transplant_dates[tx_id]
    last_news_date = tx_date + timedelta(days=random.randint(180, 365))
    
    outcome = {
        "lastNewsDate": last_news_date,
        "aliveWithFunctioningGraft": random.choice([True, True, True, True, False]),  # 80% success
        "returnToDialysis": False,
        "deathWithFunctioningGraft": False,
        "lostToFollowUp": False,
        "delayedGraftFunction": random.choice([True, False, False, False]),
        "transplantation_id": tx_id
    }
    db.outcomes.insert_one(outcome)
    print(f"✓ Created outcome for transplantation")

# ============================================
# CREATE TRANSFUSION EVENTS
# ============================================

print("\n" + "="*50)
print("Creating Transfusion Events...")
print("="*50)

for recipient_id in recipient_ids.values():
    if random.random() < 0.3:  # 30% of recipients had transfusions
        transfusion = {
            "transfusionDate": datetime(2023, random.randint(6, 12), random.randint(1, 28)),
            "units": random.randint(1, 4),
            "aboType": db.patients.find_one({"_id": recipient_id})["bloodGroup"],
            "indication": random.choice(["Anemia", "Bleeding", "Surgery"]),
            "patient_id": recipient_id
        }
        db.transfusions.insert_one(transfusion)
        print(f"✓ Created transfusion event for recipient")

# ============================================
# SUMMARY
# ============================================

print("\n" + "="*50)
print("DATABASE SEEDING COMPLETE!")
print("="*50)
print(f"\n📊 Summary:")
print(f"  • Patients: {db.patients.count_documents({})} (5 recipients, 5 donors)")
print(f"  • Transplantations: {db.transplantations.count_documents({})}")
print(f"  • Follow-ups: {db.followups.count_documents({})}")
print(f"  • Biological Measurements: {db.biological_measurements.count_documents({})}")
print(f"  • Vital Signs: {db.vitals.count_documents({})}")
print(f"  • Immunological Markers: {db.immunological_markers.count_documents({})}")
print(f"  • Rejection Episodes: {db.rejections.count_documents({})}")
print(f"  • Adverse Events: {db.adverse_events.count_documents({})}")
print(f"  • Treatments: {db.treatments.count_documents({})}")
print(f"  • Immunosuppression Regimens: {db.immunosuppression_regimens.count_documents({})}")
print(f"  • Crossmatch Tests: {db.crossmatch_tests.count_documents({})}")
print(f"  • Outcomes: {db.outcomes.count_documents({})}")
print(f"  • Transfusions: {db.transfusions.count_documents({})}")
print(f"  • Adherence: {db.adherence.count_documents({})}")

print("\n✅ You can now test the scoring system!")
print("   Navigate to:")
print("   • /transplantations - View transplantations and calculate SCORE 1 & 3")
print("   • /followups - View follow-ups and calculate SCORE 2")
print("   • /scores - View all scores with breakdowns")