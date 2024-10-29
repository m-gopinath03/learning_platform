from rest_framework import serializers
from payment_gateway.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'course', 'amount', 'status', 
                 'payment_method', 'transaction_id', 'created_at']
        read_only_fields = ['transaction_id', 'status']
