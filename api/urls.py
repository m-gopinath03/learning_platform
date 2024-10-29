from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import account_views, course_views, payment_views
from payment_gateway import views as payment_gateway_views

router = DefaultRouter()
router.register(r'users', account_views.UserViewSet)
router.register(r'courses', course_views.CourseViewSet)
router.register(r'payments', payment_views.PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include([
        path('login/', account_views.LoginView.as_view(), name='api-login'),
        path('logout/', account_views.LogoutView.as_view(), name='api-logout'),
        path('register/', account_views.RegistrationView.as_view(), name='api-register'),
    ])),
    path('courses/', include([
        path('<int:course_id>/enroll/', course_views.CourseEnrollmentView.as_view(), name='course-enroll'),
        path('my-courses/', course_views.UserCoursesView.as_view(), name='my-courses'),
    ])),
    path('payments/', include([
        # API Payment endpoints
        path('process/<int:course_id>/', payment_views.PaymentProcessView.as_view(), name='api-payment-process'),
        path('verify/', payment_views.PaymentVerificationView.as_view(), name='api-payment-verify'),
        path('status/<int:payment_id>/', payment_views.PaymentStatusView.as_view(), name='api-payment-status'),
        
        # PayPal callback endpoints
        path('success/', payment_gateway_views.PaymentSuccessView.as_view(), name='payment_success'),
        path('cancelled/', payment_gateway_views.PaymentCancelledView.as_view(), name='payment_cancelled'),
        path('ipn/', include('paypal.standard.ipn.urls')),
    ])),
]
