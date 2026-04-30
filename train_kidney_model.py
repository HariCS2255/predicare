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

df = pd.read_csv("kidneynew.csv")

# Drop ID
df = df.drop("id", axis=1)

# Replace '?' with NaN
df.replace("?", np.nan, inplace=True)

# -------------------------
# Clean Target
# -------------------------

df["classification"] = df["classification"].astype(str).str.strip()

df["classification"] = df["classification"].map({
    "ckd": 1,
    "notckd": 0
})

df = df.dropna(subset=["classification"])

y = df["classification"]
X = df.drop("classification", axis=1)

# -------------------------
# Separate numeric & categorical
# -------------------------

numeric_cols = X.select_dtypes(include=["int64", "float64"]).columns
categorical_cols = X.select_dtypes(include=["object"]).columns

# -------------------------
# Impute numeric columns
# -------------------------

num_imputer = SimpleImputer(strategy="median")
X[numeric_cols] = num_imputer.fit_transform(X[numeric_cols])

# -------------------------
# Impute categorical columns
# -------------------------

cat_imputer = SimpleImputer(strategy="most_frequent")
X[categorical_cols] = cat_imputer.fit_transform(X[categorical_cols])

# -------------------------
# Encode categorical columns
# -------------------------

encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col])
    encoders[col] = le

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
    "encoders": encoders,
    "num_imputer": num_imputer,
    "cat_imputer": cat_imputer,
    "feature_columns": X.columns.tolist()
}, "ml_models/kidney_model.pkl")

print("\n✅ Kidney model saved successfully.")