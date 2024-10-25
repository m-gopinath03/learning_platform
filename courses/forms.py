from django import forms
from .models import Course, CourseContent, Category

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['category', 'title', 'description', 'price', 'thumbnail']

class CourseContentForm(forms.ModelForm):
    class Meta:
        model = CourseContent
        fields = ['title', 'content', 'file', 'order']

class CourseSearchForm(forms.Form):
    query = forms.CharField(required=False)
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories"
    )
    price_min = forms.DecimalField(required=False, min_value=0)
    price_max = forms.DecimalField(required=False, min_value=0)