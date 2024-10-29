# api/permissions.py
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from courses.models import CourseSubscription



class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow teachers to create/edit courses.
    Read-only permissions are allowed for any request.
    """
    def has_permission(self, request, view):
        # Allow read-only for any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions only for teachers
        return request.user and request.user.is_authenticated and request.user.is_teacher

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed for the course instructor
        return obj.instructor == request.user

class IsEnrolledInCourse(permissions.BasePermission):
    message = "You must be enrolled in this course to access this content."

    def has_object_permission(self, request, view, obj):
        # Allow course instructors full access
        if obj.instructor == request.user:
            return True
            
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
            
        # Check if user is enrolled and subscription is active
        is_enrolled = CourseSubscription.objects.filter(
            student=request.user,
            course=obj,
            status='active'  # Only allow active subscriptions
        ).exists()
        
        if not is_enrolled:
            raise PermissionDenied(detail="You must be enrolled in this course to access this content.")
            
        return is_enrolled

    def has_permission(self, request, view):
        # Allow list views for authenticated users
        if request.method in permissions.SAFE_METHODS and not view.action == 'retrieve':
            return request.user.is_authenticated
        return True
