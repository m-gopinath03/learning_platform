from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..permissions import IsTeacherOrReadOnly
from ..serializers.course_serializers import CourseSerializer
from courses.models import Course, CourseSubscription, CourseContent
from rest_framework.views import APIView
from ..permissions import IsEnrolledInCourse

class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(instructor=request.user)  # Set instructor automatically
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseEnrollmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            subscription, created = CourseSubscription.objects.get_or_create(
                student=request.user,
                course=course,
                defaults={'amount_paid': course.price}
            )
            return Response({'status': 'enrolled'}, status=status.HTTP_201_CREATED)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

class UserCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscriptions = CourseSubscription.objects.filter(
            student=request.user,
            status='active'
        )
        courses = [sub.course for sub in subscriptions]
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

class CourseContentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsEnrolledInCourse]
    
    def get_queryset(self):
        return CourseContent.objects.filter(course_id=self.kwargs['course_pk'])
