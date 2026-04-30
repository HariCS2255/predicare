import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# 1️⃣ Load dataset
df = pd.read_csv("heart.csv")

# 2️⃣ Separate features and target
X = df.drop("target", axis=1)
y = df["target"]

# 3️⃣ Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4️⃣ Build pipeline
pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="mean")),  # handles future missing values
    ("model", RandomForestClassifier(
        n_estimators=200,
        random_state=42
    ))
])

# 5️⃣ Train model
pipeline.fit(X_train, y_train)

# 6️⃣ Evaluate
y_pred = pipeline.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# 7️⃣ Save model
joblib.dump(pipeline, "heart_model.pkl")

print("\n✅ Heart model saved successfully.")