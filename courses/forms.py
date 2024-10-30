from django import forms
from .models import Course, CourseContent, Category
from django.utils.text import slugify

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'thumbnail', 'category', 'is_published']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'min': 0, 'step': '1'}),
        }

    def generate_unique_slug(self, title):
        slug = slugify(title)
        unique_slug = slug
        num = 1
        while Course.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{slug}-{num}"
            num += 1
        return unique_slug

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = self.generate_unique_slug(instance.title)
        if commit:
            instance.save()
        return instance

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
