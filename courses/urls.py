from django.urls import path
from courses import views

urlpatterns = [
    # Teacher URLs
    path('create/', views.create_course, name='create_course'),
    path('edit/<slug:slug>/', views.edit_course, name='edit_course'),
    path('delete/<slug:slug>/', views.delete_course, name='delete_course'),
    path('content/add/<slug:course_slug>/', views.add_course_content, name='add_course_content'),
    path('content/<int:content_id>/delete/', views.delete_course_content, name='delete_course_content'),
    # Student URLs
    path('', views.course_list, name='course_list'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('course/<slug:slug>/manage-content/', views.manage_course_content, name='manage_course_content'),
    path('content/<int:content_id>/edit/', views.edit_course_content, name='edit_course_content'),
    
    
    # Payment URLs
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancelled/', views.payment_cancelled, name='payment_cancelled'),
]
