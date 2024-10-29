from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser
from courses.models import Course
from payment_gateway.models import Payment
from decimal import Decimal

class APIIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Clear all courses at the start of each test
        Course.objects.all().delete()
        
        # Create test users
        self.teacher = CustomUser.objects.create_user(
            username='teacher',
            password='password123',
            is_teacher=True
        )
        
        self.student = CustomUser.objects.create_user(
            username='student',
            password='password123',
            is_student=True
        )
        
        # Create exactly one test course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            price='99.99',
            instructor=self.teacher
        )

    def test_user_registration(self):
        url = reverse('api-register')
        data = {
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'is_student': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(email='newuser@test.com').exists())

    def test_user_login(self):
        url = reverse('api-login')
        data = {
            'username': 'teststudent',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_course_listing(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get(reverse('course-list'))
        self.assertEqual(len(response.data), 1)

    def test_course_creation_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse('course-list')
        data = {
            'title': 'New Unique Course',  # Changed title to be unique
            'description': 'Test Description',
            'price': '99.99',
            'instructor': self.teacher.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_course_creation_as_student(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('course-list')
        data = {
            'title': 'New Course',
            'description': 'New Description',
            'price': '149.99'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_complete_payment_flow(self):
        self.client.force_authenticate(user=self.student)
        
        # Process payment
        process_url = reverse('api-payment-process', kwargs={'course_id': self.course.id})
        data = {
            'amount': str(self.course.price),
            'payment_method': 'paypal',
            'course': self.course.id
        }
        response = self.client.post(process_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payment_id = response.data['payment_id']

        # Verify payment
        verify_url = reverse('api-payment-verify')
        verify_data = {'payment_id': payment_id}
        response = self.client.post(verify_url, verify_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_courses(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('user-courses')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
