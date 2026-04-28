import uuid
from django.db import models

class Transaction(models.Model):
    """creando el modelo transaction para pruebas"""
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'transaction'

class Order(models.Model):
    """defino mi modelo nota: solo para pruebas luego pasar a uid"""
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'transaction'

