from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    )

    SPECIALIZATION_CHOICES = (
        ('cardio', 'Cardiologist'),
        ('pulmo', 'Pulmonologist'),
        ('nephro', 'Nephrologist'),
        ('hepato', 'Hepatologist'),
        ('endo', 'Endocrinologist'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    specialization = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


    from django.db import models
from django.contrib.auth.models import User


class Booking(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patient_bookings")
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="doctor_bookings")

    specialization = models.CharField(max_length=50)
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} → {self.doctor.username} ({self.status})"
    


from django.db import models
from django.contrib.auth.models import User


class AIReport(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    diabetes_risk = models.FloatField(null=True, blank=True)
    kidney_risk = models.FloatField(null=True, blank=True)
    liver_risk = models.FloatField(null=True, blank=True)
    heart_risk = models.FloatField(null=True, blank=True)
    lung_risk = models.FloatField(null=True, blank=True)

    diabetes_coverage = models.FloatField(null=True, blank=True)
    kidney_coverage = models.FloatField(null=True, blank=True)
    liver_coverage = models.FloatField(null=True, blank=True)
    heart_coverage = models.FloatField(null=True, blank=True)
    lung_coverage = models.FloatField(null=True, blank=True)