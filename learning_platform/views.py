from django.shortcuts import render
from courses.models import Course, Category

def home(request):
    featured_courses = Course.objects.all()[:6]  # Get first 6 courses
    categories = Category.objects.all()
    
    context = {
        'featured_courses': featured_courses,
        'categories': categories,
    }
    return render(request, 'home.html', context)
