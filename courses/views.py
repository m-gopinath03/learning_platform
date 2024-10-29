from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import Course, CourseContent, CourseSubscription, Category
from .forms import CourseForm, CourseContentForm, CourseSearchForm
import logging
import uuid
import time
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.views.generic import ListView, DetailView

logger = logging.getLogger(__name__)

# Teacher views
@login_required
def create_course(request):
    if not hasattr(request.user, 'is_teacher') or not request.user.is_teacher:
        messages.error(request, "Access denied. Teacher privileges required.")
        return redirect('home')

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, 'Course created successfully!')
            return redirect('course_detail', slug=course.slug)
    else:
        form = CourseForm()
    
    return render(request, 'courses/create_course.html', {'form': form})

@login_required
def edit_course(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    
    if not hasattr(request.user, 'is_teacher') or not request.user.is_teacher:
        messages.error(request, "Access denied. Teacher privileges required.")
        return redirect('home')

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('course_detail', slug=course.slug)
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'courses/edit_course.html', {'form': form, 'course': course})

@login_required
def delete_course(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    
    if request.method == 'POST':
        course.delete()
        messages.success(request, "Course deleted successfully")
        return redirect('teacher_dashboard')
    
    return render(request, 'courses/delete_course.html', {'course': course})

@login_required
def add_course_content(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    
    if request.method == 'POST':
        form = CourseContentForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.course = course
            content.save()
            
            # Send notification to subscribed students
            subscribers = CourseSubscription.objects.filter(course=course)
            for subscription in subscribers:
                send_mail(
                    f'New content added to {course.title}',
                    f'A new topic "{content.title}" has been added to the course.',
                    settings.EMAIL_HOST_USER,
                    [subscription.student.email],
                    fail_silently=True,
                )
            
            messages.success(request, "Content added successfully")
            return redirect('course_detail', slug=course.slug)
    else:
        form = CourseContentForm()
    
    return render(request, 'courses/add_content.html', {'form': form, 'course': course})

@login_required
def delete_course_content(request, content_id):
    content = get_object_or_404(CourseContent, id=content_id, course__instructor=request.user)
    
    if request.method == 'POST':
        content.delete()
        messages.success(request, "Content deleted successfully")
        return redirect('manage_course_content', slug=content.course.slug)
    
    return render(request, 'courses/delete_content.html', {'content': content})

@login_required
def edit_course_content(request, content_id):
    content = get_object_or_404(CourseContent, id=content_id, course__instructor=request.user)
    
    if request.method == 'POST':
        form = CourseContentForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, "Content updated successfully")
            return redirect('manage_course_content', slug=content.course.slug)
    else:
        form = CourseContentForm(instance=content)
    
    return render(request, 'courses/edit_content.html', {
        'form': form,
        'content': content,
        'course': content.course
    })

# Student views
class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 6  # Number of courses per page

    def get_queryset(self):
        queryset = Course.objects.all().order_by('-created_at')  # Show all courses, newest first
        
        # Filter by category if specified
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Search functionality
        search_query = self.request.GET.get('query')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        # Add search query to context if it exists
        context['search_query'] = self.request.GET.get('query', '')
        return context

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

@login_required
def dashboard_redirect(request):
    if request.user.is_teacher:
        return redirect('teacher_dashboard')
    elif request.user.is_student:
        return redirect('student_dashboard')
    else:
        return redirect('home')

@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher:
        messages.error(request, "Access denied. Teacher privileges required.")
        return redirect('home')
        
    courses = Course.objects.filter(instructor=request.user)
    
    # Calculate statistics
    total_students = sum(course.student_count for course in courses)
    total_earnings = sum(course.total_revenue for course in courses)
    total_courses = courses.count()
    
    # Get recent enrollments
    recent_enrollments = CourseSubscription.objects.filter(
        course__instructor=request.user,
        status='active'
    ).select_related('student', 'course').order_by('-created_at')[:10]  # Changed from enrollment_date to created_at
    # Get monthly enrollment statistics
    monthly_enrollments = CourseSubscription.objects.filter(
        course__instructor=request.user,
        status='active'
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id'),
        revenue=Sum('amount_paid')  # Add revenue calculation
    ).order_by('-month')

    # Get per-course statistics
    course_statistics = []
    for course in courses:
        course_stats = {
            'course': course,
            'student_count': course.student_count,
            'revenue': course.total_revenue,
            'recent_students': CourseSubscription.objects.filter(
                course=course,
                status='active'
            ).select_related('student').order_by('-created_at')[:5]
        }
        course_statistics.append(course_stats)
        
    context = {
        'courses': courses,
        'total_students': total_students,
        'total_earnings': total_earnings,
        'total_courses': total_courses,
        'recent_enrollments': recent_enrollments,
        'monthly_enrollments': monthly_enrollments,
        'course_statistics': course_statistics  
    }
    
    return render(request, 'courses/teacher_dashboard.html', context)

@login_required
def student_dashboard(request):
    if not request.user.is_student:
        messages.error(request, "Access denied. Student privileges required.")
        return redirect('home')
        
    subscriptions = CourseSubscription.objects.filter(
        student=request.user,
        status='active'
    ).select_related('course')
    
    total_spent = subscriptions.aggregate(
        total=models.Sum('amount_paid')
    )['total'] or 0
    
    context = {
        'subscriptions': subscriptions,
        'total_spent': total_spent
    }
    
    return render(request, 'courses/student_dashboard.html', context)

@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    is_enrolled = CourseSubscription.objects.filter(
        student=request.user,
        course=course,
        status='active'
    ).exists() if request.user.is_authenticated else False
    
    is_instructor = course.instructor == request.user if request.user.is_authenticated else False
    
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'is_instructor': is_instructor,
        'show_enroll_button': not (is_enrolled or is_instructor)
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def manage_course_content(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    content_list = CourseContent.objects.filter(course=course).order_by('order')
    
    context = {
        'course': course,
        'content_list': content_list
    }
    return render(request, 'courses/manage_content.html', context)

def home_view(request):
    context = {
        'categories': Category.objects.all(),
    }
    return render(request, 'home.html', context)
