"""modelo para transaction"""
from django.db import models
import uuid
from apps.orders.models import Order

class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')  #uso para referenciar orders
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    #mantengo el log para postgres
    status_code = models.CharField(max_length=20, null=True)
    raw_response = models.TextField(null=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tx {self.id} - Order: {self.order.id}"