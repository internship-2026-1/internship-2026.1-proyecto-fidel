from rest_framework import serializers
from .models import Order, OrderItem

#serializers basado en modelo
class OrderItemSerializers(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product_sku', 'quantity']



class OrderSerializers(serializers.ModelSerializer):
    customer_id = serializers.UUIDField()
    items = OrderItemSerializers(many=True)

    class Meta:
        model = Order

        fields = [
            'id', 'customer_id', 'total_amount', 'status',
            'odoo_sale_order_id', 'created_at', 'items', 'updated_at'
        ]

        read_only_fields = ['id', 'created_at', 'odoo_sale_order_id', 'total_amount', 'status']


