from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    name = models.CharField(max_length=255, blank=True, null=True)  # Add this line
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email