from django.shortcuts import render, redirect
from django.contrib.auth import login, get_backends
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import random
import string
from .forms import TeacherSignUpForm, StudentSignUpForm, OTPVerificationForm
from .models import CustomUser
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    subject = 'Your OTP for verification'
    message = f'Your OTP is: {otp}. Valid for 10 minutes.'
    from_email = 'mgopinath032398@gmail.com'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def register(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        
        if user_type == 'teacher':
            form = TeacherSignUpForm(request.POST)
            template_user_type = 'Teacher'
        else:
            form = StudentSignUpForm(request.POST)
            template_user_type = 'Student'
            
        if form.is_valid():
            user = form.save()
            # Generate and send OTP
            otp = generate_otp()
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()
            send_otp_email(user.email, otp)
            verify_url = reverse('accounts:verify_otp', kwargs={'user_id': user.id})
            return redirect(verify_url)
    else:
        # Default to student registration form
        user_type = request.GET.get('type', 'student')
        if user_type == 'teacher':
            form = TeacherSignUpForm()
            template_user_type = 'Teacher'
        else:
            form = StudentSignUpForm()
            template_user_type = 'Student'
    
    return render(request, 'accounts/signup.html', {
        'form': form,
        'user_type': template_user_type,
        'is_teacher_form': user_type == 'teacher'
    })

def verify_otp(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        if user.email_verified:
            messages.info(request, 'Email already verified')
            return redirect('login')
            
        if request.method == 'POST':
            form = OTPVerificationForm(request.POST)
            if form.is_valid():
                otp = form.cleaned_data['otp']
                if user.otp == otp:
                    if user.otp_created_at + timedelta(minutes=10) >= timezone.now():
                        user.email_verified = True
                        user.save()
                        
                        backend = get_backends()[0]
                        user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
                        
                        login(request, user)
                        messages.success(request, 'Email verified successfully')
                        
                        if user.is_teacher:
                            return redirect('accounts:teacher_dashboard')
                        elif user.is_student:
                            return redirect('accounts:student_dashboard')
                    else:
                        messages.error(request, 'OTP expired')
                else:
                    messages.error(request, 'Invalid OTP')
        else:
            form = OTPVerificationForm()
        return render(request, 'accounts/verify_otp.html', {'form': form})
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('home')

@login_required
def dashboard_redirect(request):
    if request.user.is_teacher:
        return redirect('teacher_dashboard')
    elif request.user.is_student:
        return redirect('student_dashboard')
    else:
        return redirect('home')


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    if request.method == 'POST':
        # Handle profile update logic here
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'accounts/profile.html', {
        'user': request.user
    })

@login_required
def dashboard(request):
    if request.user.is_teacher:
        return redirect('teacher_dashboard')
    return redirect('student_dashboard')