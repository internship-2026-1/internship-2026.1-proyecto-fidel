"""serializer para payments"""

from rest_framework import serializers


class CreateCheckoutSessionSerializer(serializers.Serializer):
    """sesion para checkout"""
    order_id = serializers.CharField(required=True)

class StripeWebhookSerializer(serializers.Serializer):
    """no hace nada solo por verificar error"""
    pass