"""servicios para ordenes """
import uuid #prueba
import logging
from decimal import Decimal
from django.db import transaction
from apps.products.models import Product
from .task import sync_order_stock_to_odoo_task
from .models import Order, OrderItem


logger = logging.getLogger(__name__)


class OrderService:
    """servicio para crear ordenes validando productos y stock."""

    @staticmethod
    @transaction.atomic
    def create_order_with_stock_check(customer_id, items_data):
        """valida productos en mongo crea la orden en PostgreSQL y descuenta stock local en MongoDB."""

        total_amount = Decimal("0.00")
        order_items_to_create = []

        for item in items_data:
            sku = item["product_sku"]
            quantity = item["quantity"]

            product = Product.objects(sku=sku).first()

            if not product:
                raise Exception(f"El producto con SKU {sku} no existe en MongoDB.")

            if product.stock < quantity:
                raise Exception(
                    f"stock insuficiente para {product.name}. "
                    f"Disponible: {product.stock}"
                )

            price = product.base_price or Decimal("0.00")
            total_amount += price * quantity

            order_items_to_create.append(
                {
                    "product_sku": sku,
                    "quantity": quantity,
                    "price_at_purchase": price,
                }
            )

        order = Order.objects.create(
            order_number=f"ORD-{uuid.uuid4().hex[:10].upper()}",
            customer_id=customer_id,
            total_amount=total_amount,
            #status="PENDING",
            status=Order.STATUS_PENDING, # solo para probar como va mi post de procesar pagos
        )

        for item_data in order_items_to_create:
            OrderItem.objects.create(
                order=order,
                product_sku=item_data["product_sku"],
                quantity=item_data["quantity"],
                price_at_purchase=item_data["price_at_purchase"],
            )

            #Product.objects(
            #    sku=item_data["product_sku"]
            #).update_one(
            #    dec__stock=item_data["quantity"]
            #)

            # baja el stock esto mi prueba 
            ##updated = Product.objects(
            ##    sku=item_data["product_sku"],
            ##    stock__gte=item_data["quantity"]
            ##).update_one(
            ##    __raw__={
            ##        "$inc": {
            ##            "stock": -item_data["quantity"]
            ##        }
            ##    }
            ##)

            ##if updated == 0:
            ##    raise Exception(
            ##        f"Stock insuficiente para {item_data['product_sku']} al descontar stock."
            ##    )

        # estoy haciendo pruebas en para procesar pago
        #transaction.on_commit(
        #    lambda: sync_order_stock_to_odoo_task.delay(str(order.id))
        #)

        logger.info(f"orden creada correctamente: {order.id}")

        return order

    @staticmethod
    @transaction.atomic
    def simulate_payment(order_id):
        """simulo pago exitoso para cambiar estatus a paid ademas mando ejecutar task apunta a odoo"""

        order = Order.objects.filter(id=order_id).first()

        if not order:
            raise Exception("orden no encontrada.")

        if order.status != Order.STATUS_PENDING:
            raise Exception(f"la orden no está en PENDING. Estado actual: {order.status}")

        items = order.items.all()

        for item in items:
            product = Product.objects(sku=item.product_sku).first()

            if not product:
                raise Exception(f"El producto con SKU {item.product_sku} no existe en MongoDB.")

            if product.stock < item.quantity:
                raise Exception(
                    f"Stock insuficiente para {item.product_sku}. "
                    f"Disponible: {product.stock}"
                )

        for item in items:
            updated = Product.objects(
                sku=item.product_sku,
                stock__gte=item.quantity
            ).update_one(
                __raw__={
                    "$inc": {
                        "stock": -item.quantity
                    }
                }
            )

            if updated == 0:
                raise Exception(
                    f"Stock insuficiente para {item.product_sku} al descontar stock."
                )

        order.status = Order.STATUS_PAID
        order.save(update_fields=["status", "updated_at"])

        transaction.on_commit(
            lambda: sync_order_stock_to_odoo_task.delay(str(order.id))
        )

        logger.info(f"pago simulado correctamente para orden: {order.id}")

        return order