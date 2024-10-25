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

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    subject = 'Your OTP for verification'
    message = f'Your OTP is: {otp}. Valid for 10 minutes.'
    from_email = 'mgopinath032398@gmail.com'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def teacher_signup(request):
    if request.method == 'POST':
        form = TeacherSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            otp = generate_otp()
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()
            send_otp_email(user.email, otp)
            return redirect('verify_otp', user_id=user.id)
    else:
        form = TeacherSignUpForm()
    return render(request, 'accounts/signup.html', {'form': form, 'user_type': 'Teacher'})

def student_signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            otp = generate_otp()
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()
            send_otp_email(user.email, otp)
            return redirect('verify_otp', user_id=user.id)
    else:
        form = StudentSignUpForm()
    return render(request, 'accounts/signup.html', {'form': form, 'user_type': 'Student'})

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
                        
                        # Specify the backend
                        backend = get_backends()[0]  # Use the first backend
                        user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
                        
                        login(request, user)
                        messages.success(request, 'Email verified successfully')
                        
                        # Redirect to the appropriate dashboard
                        if user.is_teacher:
                            return redirect('teacher_dashboard')
                        elif user.is_student:
                            return redirect('student_dashboard')
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