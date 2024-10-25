from django.urls import path, include
from accounts import views

urlpatterns = [
    path('signup/teacher/', views.teacher_signup, name='teacher_signup'),
    path('signup/student/', views.student_signup, name='student_signup'),
    path('verify-otp/<int:user_id>/', views.verify_otp, name='verify_otp'),
    path('', include('django.contrib.auth.urls')),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
]
