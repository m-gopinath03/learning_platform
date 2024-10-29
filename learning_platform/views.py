from django.shortcuts import render
from courses.models import Course, Category

def home(request):
    context = {
        'featured_courses': Course.objects.filter(is_published=True).order_by('-created_at')[:3],
        'categories': Category.objects.all()
    }
    return render(request, 'home.html', context)
