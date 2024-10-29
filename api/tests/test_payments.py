from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser
from courses.models import Course, CourseSubscription
from payment_gateway.models import Payment
from decimal import Decimal
import time

class PaymentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student = CustomUser.objects.create_user(
            username='student',
            email='student@example.com',
            password='studentpass123',
            is_student=True
        )
        self.teacher = CustomUser.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='teacherpass123',
            is_teacher=True
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            price=99.99,
            instructor=self.teacher
        )
        self.process_url = reverse('api-payment-process', kwargs={'course_id': self.course.id})
        self.verify_url = reverse('api-payment-verify')

    def test_process_payment_unauthenticated(self):
        data = {
            'amount': str(self.course.price),
            'payment_method': 'paypal'
        }
        response = self.client.post(self.process_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_process_payment_success(self):
        self.client.force_authenticate(user=self.student)
        data = {
            'amount': str(self.course.price),
            'payment_method': 'paypal'
        }
        response = self.client.post(self.process_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['payment_status'], 'pending')
        self.assertIn('paypal_data', response.data)
        
        # Verify payment record
        payment = Payment.objects.get(id=response.data['payment_id'])
        self.assertEqual(payment.status, 'pending')
        self.assertEqual(Decimal(str(payment.amount)), self.course.price)

    def test_process_payment_already_enrolled(self):
        self.client.force_authenticate(user=self.student)
        # Create existing subscription
        CourseSubscription.objects.create(
            student=self.student,
            course=self.course,
            amount_paid=self.course.price,
            status='active'
        )
        
        data = {
            'amount': str(self.course.price),
            'payment_method': 'paypal'
        }
        response = self.client.post(self.process_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Already enrolled in this course')

    def test_verify_payment_success(self):
        self.client.force_authenticate(user=self.student)
        payment = Payment.objects.create(
            user=self.student,
            course=self.course,
            amount=self.course.price,
            payment_method='paypal',
            status='pending'
        )
        
        response = self.client.post(
            self.verify_url,
            {'payment_id': payment.id},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['payment_status'], 'completed')
        
        # Verify payment and subscription
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'completed')
        subscription = CourseSubscription.objects.get(
            student=self.student,
            course=self.course
        )
        self.assertEqual(subscription.status, 'active')

    def test_verify_payment_invalid_id(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            self.verify_url,
            {'payment_id': 99999},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_verify_payment_wrong_user(self):
        other_student = CustomUser.objects.create_user(
            username='other_student',
            email='other@example.com',
            password='pass123',
            is_student=True
        )
        
        payment = Payment.objects.create(
            user=other_student,
            course=self.course,
            amount=self.course.price,
            payment_method='paypal',
            status='pending'
        )
        
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            self.verify_url,
            {'payment_id': payment.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_payment_status_check(self):
        self.client.force_authenticate(user=self.student)
        payment = Payment.objects.create(
            user=self.student,
            course=self.course,
            amount=self.course.price,
            payment_method='paypal',
            status='completed'
        )
        
        status_url = reverse('api-payment-status', kwargs={'payment_id': payment.id})
        response = self.client.get(status_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')

    def test_payment_flow(self):
        # Create initial payment
        process_response = self.client.post(reverse('payment-process', kwargs={'course_id': self.course.id}))
        self.assertEqual(process_response.status_code, status.HTTP_201_CREATED)
        
        payment_id = process_response.data['payment_id']
        
        # Verify payment
        verify_data = {'payment_id': payment_id}
        verify_response = self.client.post(reverse('payment-verify'), verify_data, format='json')
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)

    def test_complete_payment_flow(self):
        self.client.force_authenticate(user=self.student)
        
        # Step 1: Process Payment
        data = {
            'amount': str(self.course.price),
            'payment_method': 'paypal'
        }
        process_response = self.client.post(self.process_url, data, format='json')
        self.assertEqual(process_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(process_response.data['payment_status'], 'pending')
        payment_id = process_response.data['payment_id']
        
        # Step 2: Verify Payment
        verify_data = {'payment_id': payment_id}
        verify_response = self.client.post(self.verify_url, verify_data, format='json')
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.assertEqual(verify_response.data['payment_status'], 'completed')
        
        # Step 3: Check Subscription
        subscription = CourseSubscription.objects.get(
            student=self.student,
            course=self.course
        )
        self.assertEqual(subscription.status, 'active')

    def test_payment_status(self):
        self.client.force_authenticate(user=self.student)
        payment = Payment.objects.create(
            user=self.student,
            course=self.course,
            amount=self.course.price,
            payment_method='paypal',
            status='completed',
            transaction_id=f"TXN-{int(time.time())}"  # Add transaction_id
        )

