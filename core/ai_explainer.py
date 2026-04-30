def generate_insight(disease, parameters):

    insights = []

    if disease == "diabetes":

        if parameters.get("HbA1c_level", 0) > 6.5:
            insights.append("Elevated HbA1c level detected")

        if parameters.get("blood_glucose_level", 0) > 140:
            insights.append("High blood glucose level")

        if parameters.get("bmi", 0) > 30:
            insights.append("BMI indicates obesity")

    if disease == "kidney":

        if parameters.get("sc", 0) > 1.3:
            insights.append("High serum creatinine")

        if parameters.get("hemo", 100) < 12:
            insights.append("Low hemoglobin level")

    if disease == "liver":

        if parameters.get("Total_Bilirubin", 0) > 1.2:
            insights.append("Elevated bilirubin")

    if disease == "heart":

        if parameters.get("chol", 0) > 240:
            insights.append("High cholesterol")

    if disease == "lung":

        if parameters.get("wt.loss", 0) > 5:
            insights.append("Significant weight loss")

    return insights