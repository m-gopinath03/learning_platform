from django.urls import path
from . import views
from .views import CourseListView

urlpatterns = [
    # Course list and detail views
    path('', CourseListView.as_view(), name='course_list'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    
    # Dashboard URLs
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),  # Smart redirect based on user type
    
    # Teacher management URLs
    path('create/', views.create_course, name='create_course'),
    path('course/<slug:slug>/edit/', views.edit_course, name='edit_course'),
    path('course/<slug:slug>/delete/', views.delete_course, name='delete_course'),
    path('course/<slug:slug>/content/manage/', views.manage_course_content, name='manage_course_content'),
    path('course/<slug:slug>/content/add/', views.add_course_content, name='add_course_content'),
    path('content/<int:content_id>/edit/', views.edit_course_content, name='edit_course_content'),
    path('content/<int:content_id>/delete/', views.delete_course_content, name='delete_course_content'),
]
