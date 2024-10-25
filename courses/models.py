from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Course(models.Model):
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    thumbnail = models.ImageField(upload_to='course_thumbnails/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class CourseContent(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)
    content = models.TextField()
    file = models.FileField(upload_to='course_contents/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class CourseSubscription(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subscriptions')
    purchased_at = models.DateTimeField(auto_now_add=True)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"