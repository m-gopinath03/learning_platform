from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from payment_gateway.models import Payment
from ..serializers.payment_serializers import PaymentSerializer
from courses.models import Course, CourseSubscription
import logging
import time
from django.conf import settings
from django.urls import reverse
from django.shortcuts import get_object_or_404
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from ..permissions import IsTeacherOrReadOnly  
from rest_framework.exceptions import PermissionDenied
from ..serializers.course_serializers import CourseSerializer


logger = logging.getLogger(__name__)

class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

class PaymentProcessView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        
        if CourseSubscription.objects.filter(student=request.user, course=course).exists():
            return Response(
                {"error": "Already enrolled in this course"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment = Payment.objects.create(
            user=request.user,
            course=course,
            amount=course.price,
            status='pending',
            payment_method='paypal',
            transaction_id=f"TXN-{int(time.time())}"
        )
        
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': str(course.price),
            'item_name': course.title,
            'invoice': str(payment.id),
            'currency_code': settings.PAYPAL_CURRENCY,
            'return': request.build_absolute_uri(
                reverse('payment_success')
            ),
            'cancel_return': request.build_absolute_uri(
                reverse('payment_cancelled')
            ),
            'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
        }
        
        return Response({
            'payment_id': payment.id,
            'payment_status': 'pending',
            'paypal_data': paypal_dict
        }, status=status.HTTP_201_CREATED)

class PaymentVerificationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        payment_id = request.data.get('payment_id')
        try:
            payment = Payment.objects.get(
                id=payment_id,
                user=request.user
            )
            payment.status = 'completed'
            payment.save()
            
            # Create subscription with amount_paid
            subscription = CourseSubscription.objects.create(
                student=request.user,
                course=payment.course,
                amount_paid=payment.amount,
                status='active'
            )
            
            return Response({
                'status': 'success',
                'payment_status': 'completed'
            }, status=status.HTTP_200_OK)
            
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(
                id=payment_id,
                user=request.user
            )
            
            # Get subscription if exists
            subscription = CourseSubscription.objects.filter(
                student=request.user,
                payment=payment
            ).first()
            
            response_data = {
                'status': payment.status,
                'payment_id': payment.id,
                'amount': str(payment.amount),
                'created_at': payment.created_at
            }
            
            if subscription:
                response_data['subscription_status'] = subscription.status
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        request.auth.delete()
        return Response({"detail": "Successfully logged out."})

class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsTeacherOrReadOnly]
    
    def perform_create(self, serializer):
        if not self.request.user.is_teacher:
            raise PermissionDenied("Only teachers can create courses")
        serializer.save(instructor=self.request.user)

    # Add this method to filter courses for user
    def get_queryset(self):
        if self.action == 'list' and not self.request.user.is_staff:
            if self.request.user.is_teacher:
                return Course.objects.filter(instructor=self.request.user)
            else:
                # Use the correct related name from Course to CourseSubscription
                return Course.objects.filter(subscriptions__student=self.request.user)
        return super().get_queryset()