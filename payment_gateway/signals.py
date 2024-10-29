from django.dispatch import receiver
from paypal.standard.ipn.signals import valid_ipn_received
from courses.models import CourseSubscription
from .models import Payment
import logging

logger = logging.getLogger(__name__)

@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    ipn_obj = sender
    logger.info(f"Received PayPal IPN: {ipn_obj.payment_status}")
    
    if ipn_obj.payment_status == "Completed":
        try:
            custom_data = ipn_obj.custom
            course_id, user_id, payment_id = custom_data.split('_')
            
            payment = Payment.objects.get(id=payment_id)
            payment.status = 'completed'
            payment.transaction_id = ipn_obj.txn_id
            payment.save()
            
            logger.info(f"Updated payment {payment_id} status to completed via IPN")
            
            subscription, created = CourseSubscription.objects.get_or_create(
                student_id=user_id,
                course_id=course_id,
                defaults={
                    'payment': payment,
                    'amount_paid': payment.amount,
                    'status': 'active'
                }
            )
            
            logger.info(f"{'Created' if created else 'Updated'} subscription {subscription.id}")
            
        except Exception as e:
            logger.error(f"Error processing PayPal IPN: {str(e)}")
