from rapidfuzz import fuzz

PARAMETER_MAP = {
    "HbA1c_level": ["hba1c", "glycated hemoglobin", "hb a1c"],
    "blood_glucose_level": ["glucose", "fasting blood sugar", "fbs"],
    "hemo": ["hemoglobin", "hb"],
    "sc": ["creatinine", "serum creatinine"],
    "Total_Bilirubin": ["total bilirubin"],
}


def map_parameters(extracted_dict):
    mapped = {}

    for model_key, aliases in PARAMETER_MAP.items():
        for extracted_key, value in extracted_dict.items():
            for alias in aliases:

                if alias in extracted_key:
                    mapped[model_key] = value
                    break

                score = fuzz.partial_ratio(alias, extracted_key)
                if score > 85:
                    mapped[model_key] = value
                    break

    return mapped