import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.impute import SimpleImputer

# -------------------------
# Load Dataset
# -------------------------

df = pd.read_csv("lung.csv")

# Drop hospital ID
df = df.drop("inst", axis=1)

# -------------------------
# Target (already binary)
# -------------------------

y = df["status"]  # 1 = death, 0 = alive
X = df.drop("status", axis=1)

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
    "feature_columns": X.columns.tolist()
}, "ml_models/lung_model.pkl")

print("\n✅ Lung model saved successfully.")