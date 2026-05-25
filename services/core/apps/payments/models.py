"""modelo para payments"""
import uuid
from django.db import models

class Payment(models.Model):
    """models payments"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.CharField(max_length=100)
    stripe_session_id = models.CharField(max_length=500, blank=True, null=True)
    stripe_checkout_url = models.URLField(max_length=1000, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default="gtq")
    status = models.CharField(max_length=30, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    stripe_event_id = models.CharField(max_length=255, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "payments"
