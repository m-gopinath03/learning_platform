from django.conf import settings
import requests
import logging
import time
from django.urls import reverse

logger = logging.getLogger(__name__)

class PayPalService:
    def __init__(self):
        self.base_url = settings.PAYPAL_API_BASE
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET

    def get_access_token(self):
        try:
            url = f"{self.base_url}/v1/oauth2/token"
            auth = (self.client_id, self.client_secret)
            headers = {
                'Accept': 'application/json',
                'Accept-Language': 'en_US'
            }
            data = {
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(url, auth=auth, headers=headers, data=data)
            response.raise_for_status()
            return response.json()['access_token']
        except Exception as e:
            logger.error(f"PayPal token error: {str(e)}")
            raise

    def create_order(self, payment, request):
        try:
            access_token = self.get_access_token()
            url = f"{self.base_url}/v2/checkout/orders"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'intent': 'CAPTURE',
                'application_context': {
                    'return_url': request.build_absolute_uri(reverse('payment_gateway:payment_success')),
                    'cancel_url': request.build_absolute_uri(reverse('payment_gateway:payment_cancelled')),
                    'brand_name': 'Learning Platform',
                    'landing_page': 'BILLING',
                    'user_action': 'PAY_NOW',
                    'shipping_preference': 'NO_SHIPPING'
                },
                'purchase_units': [{
                    'amount': {
                        'currency_code': settings.PAYPAL_CURRENCY,
                        'value': str(payment.amount)
                    },
                    'description': payment.course.title,
                    'custom_id': f"{payment.course.id}_{payment.user.id}_{payment.id}"
                }]
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"PayPal order creation error: {str(e)}")
            raise
