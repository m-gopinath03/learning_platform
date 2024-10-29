from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from courses.models import Course, CourseSubscription
from .models import Payment
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
import time
import logging
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.renderers import TemplateHTMLRenderer
from .services import PayPalService

logger = logging.getLogger(__name__)
class PaymentProcessView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'payment_gateway/process.html'

    def get(self, request, course_id=None):
        try:
            if course_id:
                course = get_object_or_404(Course, id=course_id)
                return Response({
                    'course': course
                })
            else:
                # Handle PayPal return
                payment_id = request.GET.get('paymentId')
                payment = get_object_or_404(Payment, transaction_id=payment_id)
                return Response({
                    'payment': payment,
                    'course': payment.course
                })
            
        except Exception as e:
            logger.error(f"Error in payment process: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, course_id):
        try:
            course = get_object_or_404(Course, id=course_id)
            
            # Check if already enrolled
            if CourseSubscription.objects.filter(student=request.user, course=course).exists():
                return Response(
                    {"error": "Already enrolled in this course"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                course=course,
                amount=course.price,
                status='pending',
                payment_method='paypal',
                transaction_id=f"TXN-{int(time.time())}"
            )
            
            # Initialize PayPal service with sandbox URL
            paypal_service = PayPalService()
            order_response = paypal_service.create_order(payment, request)
            
            # Get the approval URL from the response and redirect
            for link in order_response['links']:
                if link['rel'] == 'approve':
                    return redirect(link['href'])
            
            raise Exception("PayPal approval URL not found")
            
        except Exception as e:
            logger.error(f"Error in payment process: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class PaymentVerifyView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'payment_gateway/verify.html'
    
    def get(self, request):
        try:
            # Handle PayPal cancel return
            payment_id = request.GET.get('paymentId')
            if payment_id:
                payment = get_object_or_404(Payment, transaction_id=payment_id)
                payment.status = 'cancelled'
                payment.save()
                return Response({
                    'message': 'Payment was cancelled',
                    'payment': payment
                })
            
        except Exception as e:
            logger.error(f"Error in payment verify: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class PaymentSuccessView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'payment_gateway/success.html'

    def get(self, request):
        try:
            payment_token = request.GET.get('token')
            payer_id = request.GET.get('PayerID')
            
            # Find the latest pending payment for this user
            payment = Payment.objects.filter(
                user=request.user,
                status='pending'
            ).latest('created_at')
            
            if payment:
                payment.status = 'completed'
                payment.transaction_id = f"PP-{payment_token}"
                payment.save()
                
                # Create course subscription
                CourseSubscription.objects.create(
                    student=request.user,
                    course=payment.course,
                    payment=payment,
                    amount_paid=payment.amount,
                    status='active'
                )
                
                messages.success(request, 'Payment successful! You are now enrolled in the course.')
                return redirect('student_dashboard')
            
            messages.error(request, 'No pending payment found')
            return redirect('home')
            
        except Exception as e:
            logger.error(f"Error processing payment success: {str(e)}")
            messages.error(request, 'Error processing payment')
            return redirect('home')

class PaymentCancelledView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_id = request.data.get('payment_id')
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        
        payment.status = 'cancelled'
        payment.save()
        
        return Response({
            'status': 'cancelled',
            'message': 'Payment was cancelled'
        }, status=status.HTTP_200_OK)
