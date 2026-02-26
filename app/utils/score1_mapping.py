# Each attribute defined in the medical document
# is mapped to where we fetch it in MongoDB.

SCORE1_MAPPING = {

    # ---------- Patient ----------
    "recipient_age": ("patients", "recipient_id", "age"),
    "donor_age": ("patients", "donor_id", "age"),

    "bmi": ("patients", "recipient_id", "bmi"),
    "nephropathy": ("patients", "recipient_id", "nephropathyType"),

    # ---------- Assessment ----------
    "diabetes": ("assessment", None, "diabetes"),
    "hypertension": ("assessment", None, "hypertension"),
    "acc": ("assessment", None, "acc"),
    "previous_transplants": ("assessment", None, "previousTransplants"),
    "transfusion_history": ("assessment", None, "transfusionUnits"),

    "hbsag": ("assessment", None, "hbsag"),
    "anti_hcv": ("assessment", None, "antiHcv"),
    "eer_modality": ("assessment", None, "eerModality"),

    # ---------- Transplant ----------
    "cold_ischemia": ("transplantation", None, "coldIschemiaHours"),
    "warm_ischemia": ("transplantation", None, "warmIschemiaMinutes"),
    "donor_type": ("transplantation", None, "donorType"),

    # ---------- Immunology ----------
    "hla_matching": ("immunology", None, "hlaMismatch"),
    "crossmatch": ("immunology", None, "crossmatchResult"),

    # ---------- Blood Compatibility ----------
    "abo_compatibility": ("transplantation", None, "aboCompatibility"),
}