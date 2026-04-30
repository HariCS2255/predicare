import pdfplumber
import re
from rapidfuzz import fuzz


def clean_value(value):

    value = value.strip().lower()

    # numeric extraction
    match = re.search(r"[-+]?\d*\.\d+|\d+", value)
    if match:
        return float(match.group())

    # categorical conversion
    if value in ["yes", "y", "true"]:
        return 1

    if value in ["no", "n", "false"]:
        return 0

    return None


# ------------------------------------
# VALID PARAMETERS
# prevents dates like 2026 being read
# ------------------------------------

VALID_PARAMETERS = [
    "age","sex","gender","cp","trestbps","chol","fbs","restecg",
    "thalach","exang","oldpeak","slope","ca","thal",
    "blood_glucose_level","glucose","hba1c","HbA1c_level",
    "creatinine","serum creatinine","hemoglobin","hb",
    "bilirubin","bmi","hypertension","heart_disease"
]


def extract_parameters_from_pdf(pdf_file):

    extracted = {}

    IGNORE_WORDS = [
        "reported on",
        "collected on",
        "report id",
        "patient name",
        "diagnostic",
        "laboratory"
    ]

    with pdfplumber.open(pdf_file) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            if not text:
                continue

            lines = text.split("\n")

            for line in lines:

                line_lower = line.lower()

                # Ignore metadata lines
                if any(word in line_lower for word in IGNORE_WORDS):
                    continue

                parts = line.split()

                # Expecting format like:
                # age 20 years 20-80
                if len(parts) >= 2:

                    param = parts[0].strip().lower()

                    # Actual test value is usually the second column
                    value = clean_value(parts[1])

                    if value is not None:
                        extracted[param] = value

    return extracted


# ------------------------------------
# PARAMETER MAPPING
# ------------------------------------

PARAMETER_MAP = {

    # ---------------- HEART ----------------
    "age": ["age"],
    "sex": ["sex"],
    "cp": ["cp", "chest pain"],
    "trestbps": ["trestbps", "resting blood pressure"],
    "chol": ["chol", "cholesterol"],
    "fbs": ["fbs", "fasting blood sugar"],
    "restecg": ["restecg"],
    "thalach": ["thalach", "max heart rate"],
    "exang": ["exang", "exercise angina"],
    "oldpeak": ["oldpeak", "st depression"],
    "slope": ["slope"],
    "ca": ["ca"],
    "thal": ["thal"],

    # ---------------- DIABETES ----------------
    "blood_glucose_level": ["glucose", "blood sugar", "blood_glucose_level"],
    "HbA1c_level": ["hba1c", "hba1c_level"],
    "gender": ["gender", "sex"],
    "hypertension": ["hypertension"],
    "heart_disease": ["heart_disease"],
    "smoking_history": ["smoking_history"],
    "bmi": ["bmi"],

    # ---------------- KIDNEY ----------------
    "bp": ["bp", "blood pressure"],
    "bgr": ["bgr", "blood glucose random"],
    "sc": ["sc", "serum creatinine", "creatinine"],
    "hemo": ["hemo", "hemoglobin"],
    "htn": ["htn", "hypertension"],
    "dm": ["dm", "diabetes"],

    # ---------------- LIVER ----------------
"Total_Bilirubin": ["total_bilirubin", "bilirubin"],
"Direct_Bilirubin": ["direct_bilirubin"],
"Alkaline_Phosphotase": ["alkaline_phosphotase", "alkaline_phosphotase", "alkaline"],
"Alamine_Aminotransferase": ["alamine_aminotransferase", "alt"],
"Aspartate_Aminotransferase": ["aspartate_aminotransferase", "ast"],
"Total_Protiens": ["total_protiens", "proteins"],
"Albumin": ["albumin"],
"Albumin_and_Globulin_Ratio": ["albumin_and_globulin_ratio", "a/g ratio"],

# ---------------- LUNG ----------------
"ph.ecog": ["ph.ecog", "ph ecog"],
"ph.karno": ["ph.karno", "ph karno"],
"wt.loss": ["wt.loss", "weight loss"],
"meal.cal": ["meal.cal", "meal cal", "calories"]
}

def map_parameters(extracted):

    mapped = {}

    for model_key, aliases in PARAMETER_MAP.items():

        for key, value in extracted.items():

            key = key.lower()

            for alias in aliases:

                alias = alias.lower()

                # exact match first
                if key == alias:
                    mapped[model_key] = value
                    break

                # contains match
                if alias in key:
                    mapped[model_key] = value
                    break

            if model_key in mapped:
                break

    return mapped