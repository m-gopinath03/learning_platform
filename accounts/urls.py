from django.urls import path, include
from django.contrib.auth import views as auth_views
from accounts import views
from courses import views as course_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/student/', course_views.student_dashboard, name='student_dashboard'),
    path('dashboard/teacher/', course_views.teacher_dashboard, name='teacher_dashboard'),
]
