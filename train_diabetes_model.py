import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

# Load dataset
df = pd.read_csv("diabetes.csv")

# Encode categorical columns
le_gender = LabelEncoder()
le_smoking = LabelEncoder()

df["gender"] = le_gender.fit_transform(df["gender"])
df["smoking_history"] = le_smoking.fit_transform(df["smoking_history"])

# Separate features and target
X = df.drop("diabetes", axis=1)
y = df["diabetes"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# Save everything needed (model + encoders)
os.makedirs("ml_models", exist_ok=True)
joblib.dump({
    "model": model,
    "gender_encoder": le_gender,
    "smoking_encoder": le_smoking,
    "feature_columns": X.columns.tolist()
}, "ml_models/diabetes_model.pkl")
print("\n✅ Diabetes model saved successfully.")