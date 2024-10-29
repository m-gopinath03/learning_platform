from rest_framework import serializers
from courses.models import Course, CourseContent, CourseSubscription

class CourseContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseContent
        fields = ['id', 'title', 'content', 'file', 'order', 'created_at']

class CourseSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    instructor = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'price', 'instructor', 
                'thumbnail', 'thumbnail_url', 'created_at', 'updated_at']
        read_only_fields = ['instructor']

    def get_thumbnail_url(self, obj):
        return obj.get_thumbnail_url()
