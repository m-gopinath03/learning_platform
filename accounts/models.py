from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    name = models.CharField(max_length=255, blank=True, default='')  # Added default=''
    email_verified = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    
    # Add related_name to avoid conflicts
    enrolled_courses = models.ManyToManyField(
        'courses.Course',
        through='courses.CourseSubscription',
        related_name='enrolled_users',  # Changed from enrolled_students
        blank=True
    )
    teaching_courses = models.ManyToManyField(
        'courses.Course',
        related_name='teachers',
        blank=True
    )
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email

    def is_otp_valid(self):
        if not self.otp_created_at:
            return False
        return timezone.now() <= self.otp_created_at + timedelta(minutes=10)
