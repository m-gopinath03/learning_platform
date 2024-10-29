from django.urls import path, include
from . import views

app_name = 'payment_gateway'

urlpatterns = [
path('process/<int:course_id>/', views.PaymentProcessView.as_view(), name='payment-process'),
path('success/', views.PaymentSuccessView.as_view(), name='payment_success'),
path('cancelled/',views.PaymentCancelledView.as_view(), name='payment_cancelled'),
path('verify/', views.PaymentVerifyView.as_view(), name='payment-verify'),
]
