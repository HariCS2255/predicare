import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer

# -------------------------
# Load Dataset
# -------------------------

df = pd.read_csv("liver.csv")

# -------------------------
# Clean Target Column
# -------------------------

# Convert Dataset column to binary
df["Dataset"] = df["Dataset"].map({
    1: 1,   # Liver Disease
    2: 0    # No Liver Disease
})

y = df["Dataset"]
X = df.drop("Dataset", axis=1)

# -------------------------
# Encode Gender
# -------------------------

if "Gender" in X.columns:
    le = LabelEncoder()
    X["Gender"] = le.fit_transform(X["Gender"])
    gender_encoder = le
else:
    gender_encoder = None

# -------------------------
# Handle Missing Values
# -------------------------

imputer = SimpleImputer(strategy="median")
X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

# -------------------------
# Train/Test Split
# -------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------
# Train Model
# -------------------------

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

# -------------------------
# Evaluate
# -------------------------

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# -------------------------
# Save Model
# -------------------------

os.makedirs("ml_models", exist_ok=True)

joblib.dump({
    "model": model,
    "imputer": imputer,
    "gender_encoder": gender_encoder,
    "feature_columns": X.columns.tolist()
}, "ml_models/liver_model.pkl")

print("\n✅ Liver model saved successfully.")