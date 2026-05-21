from rest_framework import serializers
from .models import Transaction

class TransactionSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = Transaction

        fields = [
            'id',
            'order',
            'amount',
            'status_code',
            'raw_response',
            'created_at'
        ]

        read_only_fields = ['id', 'created_at']