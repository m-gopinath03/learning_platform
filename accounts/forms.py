from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class TeacherSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=255, required=False)  # Add the name field

    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'email', 'password1', 'password2')  # Include name in fields

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True
        user.email = self.cleaned_data['email']
        user.name = self.cleaned_data['name']  # Save the name field
        if commit:
            user.save()
        return user

class StudentSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=255, required=False)  # Add the name field

    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'email', 'password1', 'password2')  # Include name in fields

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        user.email = self.cleaned_data['email']
        user.name = self.cleaned_data['name']  # Save the name field
        if commit:
            user.save()
        return user

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True)