import pandas as pd


def evaluate_model(bundle, data):

    # -----------------------------
    # Handle two model formats
    # -----------------------------

    if isinstance(bundle, dict):

        model = bundle["model"]
        feature_cols = bundle.get("feature_columns", [])
        imputer = bundle.get("imputer")

    else:
        # Model saved directly
        model = bundle
        imputer = None

        # Default feature sets for known models
        feature_cols = [
            "age","sex","cp","trestbps","chol",
            "fbs","restecg","thalach","exang",
            "oldpeak","slope","ca","thal"
        ]

    # -----------------------------
    # Build input vector
    # -----------------------------

    input_dict = {}
    available = 0

    for col in feature_cols:

        if col in data:
            input_dict[col] = data[col]
            available += 1
        else:
            input_dict[col] = None

    coverage = available / len(feature_cols)

    df = pd.DataFrame([input_dict])

    # -----------------------------
    # Apply imputer if exists
    # -----------------------------

    if imputer:
        df = pd.DataFrame(imputer.transform(df), columns=feature_cols)
    else:
        df = df.fillna(df.mean())


    # -----------------------------
    # Prediction
    # -----------------------------

    try:
        prob = model.predict_proba(df)[0][1]
    except:
        try:
            pred = model.predict(df)[0]
            prob = float(pred)
        except:
            prob = 0

    # -----------------------------
    # Reliability
    # -----------------------------

    if coverage > 0.6:
        reliability = "High"
    elif coverage > 0.2:
        reliability = "Moderate"
    else:
        reliability = "Limited Clinical Data"

    return {
        "probability": round(prob * 100, 2),
        "coverage": round(coverage * 100, 2),
        "reliability": reliability
    }