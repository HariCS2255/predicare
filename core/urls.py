from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-home/', views.admin_home, name='admin_home'),
    path('user-home/', views.user_home, name='user_home'),
    path('manage-doctors/', views.manage_doctors, name='manage_doctors'),
    path('delete-doctor/<int:user_id>/', views.delete_doctor, name='delete_doctor'),
    path('doctor-home/', views.doctor_home, name='doctor_home'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('doctor-bookings/', views.doctor_bookings, name='doctor_bookings'),
    path('booking/<int:booking_id>/approve/', views.approve_booking, name='approve_booking'),
    path('booking/<int:booking_id>/reject/', views.reject_booking, name='reject_booking'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path("predict-heart/", views.predict_heart, name="predict_heart"),
    path("predict/", views.prediction_hub, name="prediction_hub"),
    path("predict-diabetes/", views.predict_diabetes, name="predict_diabetes"),
    path("predict-kidney/", views.predict_kidney, name="predict_kidney"),
    path("predict-liver/", views.predict_liver, name="predict_liver"),
    path("predict-lung/", views.predict_lung, name="predict_lung"),
    path("upload-report/", views.upload_report, name="upload_report"),
    path("reports/", views.view_reports, name="view_reports"),

]

