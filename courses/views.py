from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from .models import Course, CourseContent, CourseSubscription, Category
from .forms import CourseForm, CourseContentForm, CourseSearchForm
# Teacher views
@login_required
def create_course(request):
    if not request.user.is_teacher:
        messages.error(request, "Only teachers can create courses")
        return redirect('home')
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, "Course created successfully")
            return redirect('course_detail', slug=course.slug)
    else:
        form = CourseForm()
    
    return render(request, 'courses/create_course.html', {'form': form})

@login_required
def edit_course(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully")
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
def add_course_content(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    
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

# Student views
def course_list(request):
    form = CourseSearchForm(request.GET)
    courses = Course.objects.all()
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        price_min = form.cleaned_data.get('price_min')
        price_max = form.cleaned_data.get('price_max')
        
        if query:
            courses = courses.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
        
        if category:
            courses = courses.filter(category=category)
            
        if price_min:
            courses = courses.filter(price__gte=price_min)
            
        if price_max:
            courses = courses.filter(price__lte=price_max)
    
    paginator = Paginator(courses, 12)
    page = request.GET.get('page')
    courses = paginator.get_page(page)
    
    return render(request, 'courses/course_list.html', {
        'form': form,
        'courses': courses
    })

@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    is_subscribed = False
    paypal_dict = None
    
    if request.user.is_student:
        is_subscribed = CourseSubscription.objects.filter(
            student=request.user,
            course=course
        ).exists()
        
        if not is_subscribed:
            # PayPal payment setup
            paypal_dict = {
                "business": settings.PAYPAL_RECEIVER_EMAIL,
                "amount": course.price,
                "item_name": course.title,
                "invoice": f"{request.user.id}-{course.id}",
                "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
                "return": request.build_absolute_uri(reverse('payment_success')),
                "cancel_return": request.build_absolute_uri(reverse('payment_cancelled')),
                "custom": f"{request.user.id}:{course.id}"
            }
            
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'is_subscribed': is_subscribed,
        'paypal_form': PayPalPaymentsForm(initial=paypal_dict) if paypal_dict else None
    })

# Add these new views to your existing views.py

@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher:
        messages.error(request, "Access denied. Teachers only.")
        return redirect('home')
    
    courses = Course.objects.filter(instructor=request.user)
    
    # Get statistics for each course
    course_stats = []
    for course in courses:
        stats = {
            'course': course,
            'student_count': CourseSubscription.objects.filter(course=course).count(),
            'content_count': CourseContent.objects.filter(course=course).count(),
            'revenue': CourseSubscription.objects.filter(course=course).count() * course.price
        }
        course_stats.append(stats)
    
    return render(request, 'courses/teacher_dashboard.html', {
        'course_stats': course_stats,
        'total_courses': len(courses),
        'total_revenue': sum(stat['revenue'] for stat in course_stats)
    })

@login_required
def student_dashboard(request):
    if not request.user.is_student:
        messages.error(request, "Access denied. Students only.")
        return redirect('home')
    
    subscriptions = CourseSubscription.objects.filter(student=request.user)
    
    # Track progress for each course
    course_progress = []
    for subscription in subscriptions:
        total_content = CourseContent.objects.filter(course=subscription.course).count()
        progress = {
            'subscription': subscription,
            'total_content': total_content,
            'last_accessed': subscription.course.contents.first()  # You might want to track this separately
        }
        course_progress.append(progress)
    
    return render(request, 'courses/student_dashboard.html', {
        'course_progress': course_progress
    })

@login_required
def manage_course_content(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    contents = CourseContent.objects.filter(course=course).order_by('order')
    
    if request.method == 'POST':
        # Handle content reordering via AJAX
        new_order = request.POST.get('new_order').split(',')
        for index, content_id in enumerate(new_order):
            CourseContent.objects.filter(id=content_id).update(order=index)
        return JsonResponse({'status': 'success'})
    
    return render(request, 'courses/manage_content.html', {
        'course': course,
        'contents': contents
    })

@login_required
def edit_course_content(request, content_id):
    content = get_object_or_404(CourseContent, id=content_id)
    
    if content.course.instructor != request.user:
        messages.error(request, "You don't have permission to edit this content.")
        return redirect('course_detail', slug=content.course.slug)
    
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
        'content': content
    })

@login_required
def dashboard_redirect(request):
    if request.user.is_teacher:
        return redirect('teacher_dashboard')
    elif request.user.is_student:
        return redirect('student_dashboard')
    else:
        return redirect('home')
# Payment handling views
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver

@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == "Completed":
        # Payment was successful
        user_id, course_id = ipn_obj.custom.split(':')
        
        # Create subscription
        subscription = CourseSubscription.objects.create(
            student_id=user_id,
            course_id=course_id,
            payment_id=ipn_obj.txn_id
        )
        
        # Send confirmation email
        course = Course.objects.get(id=course_id)
        student = subscription.student
        send_mail(
            'Course Purchase Confirmation',
            f'Thank you for purchasing {course.title}. You now have full access to the course content.',
            settings.EMAIL_HOST_USER,
            [student.email],
            fail_silently=True,
        )

def payment_success(request):
    messages.success(request, "Payment successful! You now have access to the course.")
    return redirect('student_dashboard')

def payment_cancelled(request):
    messages.error(request, "Payment cancelled.")
    return redirect('course_list')