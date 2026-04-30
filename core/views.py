from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Profile
from .models import AIReport

# -----------------------
# HOME
# -----------------------

def home(request):
    return render(request, 'core/index.html')


# -----------------------
# REGISTER (PATIENT)
# -----------------------

def register_view(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('register')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "Account created successfully. Please login.")
        return redirect('login')

    return render(request, 'core/register.html')


# -----------------------
# LOGIN (ADMIN / DOCTOR / PATIENT)
# -----------------------

def login_view(request):
    if request.method == "POST":
        identifier = request.POST['username']
        password = request.POST['password']

        user = None

        # Try username login
        user = authenticate(request, username=identifier, password=password)

        # If failed, try email login
        if user is None:
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user is not None:
            login(request, user)

            # 👑 ADMIN
            if user.is_superuser:
                return redirect('admin_home')

            # 👨‍⚕️ DOCTOR
            elif user.profile.role == 'doctor':
                return redirect('doctor_home')

            # 👤 PATIENT
            else:
                return redirect('user_home')

        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'core/login.html')


# -----------------------
# LOGOUT
# -----------------------

def logout_view(request):
    logout(request)
    return redirect('home')


# -----------------------
# DASHBOARDS
# -----------------------

@login_required
def admin_home(request):
    if not request.user.is_superuser:
        return redirect('home')
    return render(request, 'core/adminhome.html')


from .models import Booking

@login_required
def user_home(request):
    bookings = Booking.objects.filter(patient=request.user).order_by('-created_at')

    return render(request, 'core/userhome.html', {
        'bookings': bookings
    })


@login_required
def doctor_home(request):
    if request.user.profile.role != 'doctor':
        return redirect('home')
    return render(request, 'core/doctorhome.html')


# -----------------------
# DOCTOR MANAGEMENT (ADMIN ONLY)
# -----------------------

def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin)
def manage_doctors(request):

    if request.method == "POST":
        first_name = request.POST['first_name']
        email = request.POST['email']
        password = request.POST['password']
        specialization = request.POST['specialization']
        phone = request.POST['phone']

        if User.objects.filter(email=email).exists():
            messages.error(request, "Doctor with this email already exists.")
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name
            )

            user.profile.role = "doctor"
            user.profile.specialization = specialization
            user.profile.phone = phone
            user.profile.save()

            messages.success(request, "Doctor created successfully.")

    doctors = Profile.objects.filter(role='doctor')

    return render(request, 'core/manage_doctors.html', {
        'doctors': doctors
    })


from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404

@user_passes_test(is_admin)
def delete_doctor(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user.profile.role == "doctor":
        user.delete()

    return redirect('manage_doctors')


@user_passes_test(is_admin)
def manage_users(request):
    users = Profile.objects.filter(role='patient')
    return render(request, 'core/manage_users.html', {
        'users': users
    })


@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Prevent deleting superuser or doctor accidentally
    if not user.is_superuser and user.profile.role == "patient":
        user.delete()

    return redirect('manage_users')

from datetime import datetime, time, date
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Booking, Profile


@login_required
def book_appointment(request):

    doctors = Profile.objects.filter(role='doctor')

    if request.method == "POST":
        doctor_id = request.POST.get('doctor')
        booking_date_str = request.POST.get('date')
        booking_time_str = request.POST.get('time')
        reason = request.POST.get('reason')

        doctor_user = User.objects.get(id=doctor_id)

        booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
        booking_time = datetime.strptime(booking_time_str, "%H:%M").time()

        # ❌ Prevent past date
        if booking_date < date.today():
            messages.error(request, "You cannot book a past date.")
            return redirect('book_appointment')

        # ❌ Restrict time between 9AM – 7PM
        if booking_time < time(9, 0) or booking_time > time(19, 0):
            messages.error(request, "Booking time must be between 9AM and 7PM.")
            return redirect('book_appointment')

        # ❌ Prevent double booking
        if Booking.objects.filter(
            doctor=doctor_user,
            date=booking_date,
            time=booking_time
        ).exists():
            messages.error(request, "This time slot is already booked.")
            return redirect('book_appointment')

        # ✅ Create booking
        Booking.objects.create(
            patient=request.user,
            doctor=doctor_user,
            specialization=doctor_user.profile.specialization,
            date=booking_date,
            time=booking_time,
            reason=reason
        )

        messages.success(request, "Appointment booked successfully.")
        return redirect('user_home')

    return render(request, 'core/book_appointment.html', {
        'doctors': doctors,
        'today': date.today()   # 🔥 IMPORTANT FIX
    })


@login_required
def doctor_bookings(request):

    # Ensure only doctors can access
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'doctor':
        return redirect('home')

    bookings = Booking.objects.filter(
        doctor=request.user
    ).order_by('-created_at')

    return render(request, 'core/doctor_bookings.html', {
        'bookings': bookings
    })


from django.shortcuts import get_object_or_404


@login_required
def approve_booking(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id, doctor=request.user)

    booking.status = 'approved'
    booking.save()

    return redirect('doctor_bookings')


@login_required
def reject_booking(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id, doctor=request.user)

    booking.status = 'rejected'
    booking.save()

    return redirect('doctor_bookings')


@login_required
def cancel_booking(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        patient=request.user
    )

    if booking.status == 'pending':
        booking.delete()

    return redirect('user_home')



# -----------------------
# HEART DISEASE PREDICTION
# -----------------------

import joblib
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
heart_model_path = os.path.join(BASE_DIR, "ml_models", "heart_model.pkl")

# Load model safely
if os.path.exists(heart_model_path):
    heart_model = joblib.load(heart_model_path)
else:
    heart_model = None


@login_required
def predict_heart(request):

    prediction = None

    if request.method == "POST" and heart_model is not None:

        try:
            features = [
                float(request.POST["age"]),
                float(request.POST["sex"]),
                float(request.POST["cp"]),
                float(request.POST["trestbps"]),
                float(request.POST["chol"]),
                float(request.POST["fbs"]),
                float(request.POST["restecg"]),
                float(request.POST["thalach"]),
                float(request.POST["exang"]),
                float(request.POST["oldpeak"]),
                float(request.POST["slope"]),
                float(request.POST["ca"]),
                float(request.POST["thal"]),
            ]

            prediction = heart_model.predict([features])[0]

        except Exception as e:
            prediction = None

    return render(request, "core/predict_heart.html", {
        "prediction": prediction
    })



@login_required
def prediction_hub(request):
    return render(request, 'core/prediction_hub.html')



# -----------------------
# DIABETES PREDICTION
# -----------------------

diabetes_model_path = os.path.join(BASE_DIR, "ml_models", "diabetes_model.pkl")

if os.path.exists(diabetes_model_path):
    diabetes_bundle = joblib.load(diabetes_model_path)
    diabetes_model = diabetes_bundle["model"]
    gender_encoder = diabetes_bundle["gender_encoder"]
    smoking_encoder = diabetes_bundle["smoking_encoder"]
else:
    diabetes_model = None


@login_required
def predict_diabetes(request):

    prediction = None

    if request.method == "POST" and diabetes_model is not None:
        try:
            gender = gender_encoder.transform([request.POST["gender"]])[0]
            smoking = smoking_encoder.transform([request.POST["smoking_history"]])[0]

            features = [
                gender,
                float(request.POST["age"]),
                int(request.POST["hypertension"]),
                int(request.POST["heart_disease"]),
                smoking,
                float(request.POST["bmi"]),
                float(request.POST["HbA1c_level"]),
                float(request.POST["blood_glucose_level"]),
            ]

            prediction = diabetes_model["model"].predict([features])[0]

        except Exception as e:
            return render(request, "core/predict_diabetes.html", {
        "prediction": None,
        "error": str(e)
    })

    return render(request, "core/predict_diabetes.html", {
        "prediction": prediction
    })


# -----------------------
# LOAD ALL ML MODELS
# -----------------------

import joblib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "ml_models")

def load_model(filename):
    path = os.path.join(MODEL_DIR, filename)
    if os.path.exists(path):
        return joblib.load(path)
    return None

heart_model = load_model("heart_model.pkl")
diabetes_model = load_model("diabetes_model.pkl")
kidney_model = load_model("kidney_model.pkl")
liver_model = load_model("liver_model.pkl")
lung_model = load_model("lung_model.pkl")

# @login_required
# def predict_diabetes(request):

#     prediction = None

#     if request.method == "POST" and diabetes_model:

#         try:
#             features = [
#                 float(request.POST.get("age")),
#                 float(request.POST.get("hypertension")),
#                 float(request.POST.get("heart_disease")),
#                 float(request.POST.get("bmi")),
#                 float(request.POST.get("HbA1c_level")),
#                 float(request.POST.get("blood_glucose_level")),
#             ]

#             # IMPORTANT FIX HERE
#             prediction = diabetes_model.predict([features])[0]

#         except Exception as e:
#             print("Diabetes Prediction Error:", e)
#             prediction = None

#     return render(request, "core/predict_diabetes.html", {
#         "prediction": prediction
#     })



@login_required
def predict_kidney(request):

    prediction = None

    if request.method == "POST" and kidney_model:

        model = kidney_model["model"]
        num_imputer = kidney_model["num_imputer"]
        cat_imputer = kidney_model["cat_imputer"]
        encoders = kidney_model["encoders"]
        feature_cols = kidney_model["feature_columns"]

        import pandas as pd
        import numpy as np

        # Create dataframe with ALL original columns
        df = pd.DataFrame(columns=feature_cols)

        row = {}

        for col in feature_cols:
            row[col] = np.nan

        # Fill numeric fields
        row["age"] = float(request.POST.get("age"))
        row["bp"] = float(request.POST.get("bp"))
        row["bgr"] = float(request.POST.get("bgr"))
        row["sc"] = float(request.POST.get("sc"))
        row["hemo"] = float(request.POST.get("hemo"))

        # Fill categorical
        row["htn"] = request.POST.get("htn")
        row["dm"] = request.POST.get("dm")

        df = pd.DataFrame([row])

        # IMPORTANT: split columns EXACTLY like training

        numeric_cols = num_imputer.feature_names_in_
        categorical_cols = cat_imputer.feature_names_in_

        df[numeric_cols] = num_imputer.transform(df[numeric_cols])
        df[categorical_cols] = cat_imputer.transform(df[categorical_cols])

        for col in categorical_cols:
            df[col] = encoders[col].transform(df[col])

        prediction = model.predict(df)[0]

    return render(request, "core/predict_kidney.html", {
        "prediction": prediction
    })



@login_required
def predict_liver(request):

    prediction = None

    if request.method == "POST" and liver_model:

        model = liver_model["model"]
        imputer = liver_model["imputer"]
        gender_encoder = liver_model["gender_encoder"]
        feature_cols = liver_model["feature_columns"]

        import pandas as pd
        import numpy as np

        row = {}

        # Fill all expected columns
        for col in feature_cols:
            row[col] = np.nan

        # Numeric inputs
        row["Age"] = float(request.POST.get("Age"))
        row["Total_Bilirubin"] = float(request.POST.get("Total_Bilirubin"))
        row["Direct_Bilirubin"] = float(request.POST.get("Direct_Bilirubin"))
        row["Alkaline_Phosphotase"] = float(request.POST.get("Alkaline_Phosphotase"))
        row["Alamine_Aminotransferase"] = float(request.POST.get("Alamine_Aminotransferase"))
        row["Aspartate_Aminotransferase"] = float(request.POST.get("Aspartate_Aminotransferase"))
        row["Total_Protiens"] = float(request.POST.get("Total_Protiens"))
        row["Albumin"] = float(request.POST.get("Albumin"))
        row["Albumin_and_Globulin_Ratio"] = float(request.POST.get("Albumin_and_Globulin_Ratio"))

        # If Gender exists in model
        if gender_encoder is not None:
            gender_value = request.POST.get("Gender")
            row["Gender"] = gender_encoder.transform([gender_value])[0]

        df = pd.DataFrame([row])

        # Apply imputer EXACTLY like training
        df = pd.DataFrame(imputer.transform(df), columns=feature_cols)

        prediction = model.predict(df)[0]

    return render(request, "core/predict_liver.html", {
        "prediction": prediction
    })



@login_required
def predict_lung(request):

    prediction = None

    if request.method == "POST" and lung_model:

        model = lung_model["model"]
        imputer = lung_model["imputer"]
        feature_cols = lung_model["feature_columns"]

        import pandas as pd
        import numpy as np

        # Create full row with all training columns
        row = {}

        for col in feature_cols:
            row[col] = np.nan

        # Fill only fields user provides
        row["age"] = float(request.POST.get("age"))
        row["ph.ecog"] = float(request.POST.get("ph.ecog"))
        row["ph.karno"] = float(request.POST.get("ph.karno"))
        row["wt.loss"] = float(request.POST.get("wt.loss"))
        row["meal.cal"] = float(request.POST.get("meal.cal"))

        df = pd.DataFrame([row])

        # Apply imputer EXACTLY like training
        df = pd.DataFrame(imputer.transform(df), columns=feature_cols)

        prediction = model.predict(df)[0]

    return render(request, "core/predict_lung.html", {
        "prediction": prediction
    })   










from .pdf_processor import extract_parameters_from_pdf, map_parameters
from .disease_engine import evaluate_model
from .ai_explainer import generate_insight
from .models import AIReport


@login_required
def upload_report(request):

    if request.method == "POST":

        uploaded_files = request.FILES.getlist("reports")

        extracted_data = {}

        # read all PDFs
        for pdf in uploaded_files:

            params = extract_parameters_from_pdf(pdf)

            for k, v in params.items():
                extracted_data[k] = v

        # map to model feature names
        mapped = map_parameters(extracted_data)

        results = {}

        results["diabetes"] = evaluate_model(diabetes_model, mapped)
        results["kidney"] = evaluate_model(kidney_model, mapped)
        results["liver"] = evaluate_model(liver_model, mapped)
        results["lung"] = evaluate_model(lung_model, mapped)
        results["heart"] = evaluate_model(heart_model, mapped)

        # Generate AI insights
        for disease in results:
            results[disease]["insight"] = generate_insight(disease, mapped)

        # Save report
        AIReport.objects.create(
            user=request.user,

            diabetes_risk=results["diabetes"]["probability"],
            kidney_risk=results["kidney"]["probability"],
            liver_risk=results["liver"]["probability"],
            heart_risk=results["heart"]["probability"],
            lung_risk=results["lung"]["probability"],

            diabetes_coverage=results["diabetes"]["coverage"],
            kidney_coverage=results["kidney"]["coverage"],
            liver_coverage=results["liver"]["coverage"],
            heart_coverage=results["heart"]["coverage"],
            lung_coverage=results["lung"]["coverage"]
        )

        return render(request, "core/report_results.html", {
            "results": results,
            "extracted": mapped
        })

    return render(request, "core/upload_report.html")   



@login_required
def view_reports(request):

    reports = AIReport.objects.filter(user=request.user).order_by("-uploaded_at")

    return render(request, "core/view_reports.html", {
        "reports": reports
    })