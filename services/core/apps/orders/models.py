"""modelo orders"""
from django.db import models
import uuid

# modelo de django orm
class Order(models.Model):
    """order principal va en postgres"""

    STATUS_PENDING = "PENDING"
    STATUS_SYNCED = "SYNCED"
    STATUS_FAILED = "FAILED"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_PAID = "PAID"

    OPC_STATUS = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "PAID"),
        (STATUS_SYNCED, "Synced to Odoo"),
        (STATUS_FAILED, "Failed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True)
    customer_id = models.UUIDField(db_index=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=OPC_STATUS, default=STATUS_PENDING)
    odoo_sale_order_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.order_number} - {self.status}"


class OrderItem(models.Model):
    """detalles de orders guardado en postgreSQL"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product_sku = models.CharField(max_length=100, db_index=True)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_items"

    def __str__(self):
        return f"{self.quantity} x {self.product_sku}"

class IntegrationLog(models.Model):
    order = models.ForeignKey(Order, related_name='logs', on_delete=models.CASCADE)
    status_code = models.CharField(max_length=20) # intento validar si mando un success='200' o erorr='500'
    raw_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'integration_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"Log Order {self.order.id} - {self.status_code}"