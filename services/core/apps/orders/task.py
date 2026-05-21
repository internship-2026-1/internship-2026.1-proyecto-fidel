"""tarea asincronica para ordenes"""

import logging

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.odoo_client import (
    OdooConfigurationError,
    OdooAuthenticationError,
    get_odoo_session,
)
from apps.orders.models import Order, IntegrationLog


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def sync_order_stock_to_odoo_task(self, order_id):
    """sincroniza con Odoo el stock de los productos vendidos en una orden en postgres"""

    try:
        order = Order.objects.get(id=order_id)
        items = order.items.all()

        uid, models = get_odoo_session()

        detalles_log = []

        for item in items:
            odoo_products = models.execute_kw(
                settings.ODOO_DB,
                uid,
                settings.ODOO_API_KEY,
                "product.product",
                "search_read",
                [[["default_code", "=", item.product_sku]]],
                {
                    "fields": ["id", "default_code", "qty_available"],
                    "limit": 1,
                },
            )

            if not odoo_products:
                detalles_log.append(
                    f"SKU {item.product_sku}: no encontrado en Odoo"
                )
                continue

            odoo_product = odoo_products[0]
            current_stock = odoo_product.get("qty_available") or 0
            new_stock = max(current_stock - item.quantity, 0)

            stock_quants = models.execute_kw(
                settings.ODOO_DB,
                uid,
                settings.ODOO_API_KEY,
                "stock.quant",
                "search_read",
                [[
                    ["product_id", "=", odoo_product["id"]],
                    ["location_id.usage", "=", "internal"],
                ]],
                {
                    "fields": ["id", "quantity"],
                    "limit": 1,
                },
            )

            if not stock_quants:
                detalles_log.append(
                    f"SKU {item.product_sku}: sin ubicación interna de stock en Odoo"
                )
                continue

            stock_quant = stock_quants[0]

            models.execute_kw(
                settings.ODOO_DB,
                uid,
                settings.ODOO_API_KEY,
                "stock.quant",
                "write",
                [[stock_quant["id"]], {"quantity": float(new_stock)}],
            )

            detalles_log.append(
                f"SKU {item.product_sku}: stock {current_stock} -> {new_stock}"
            )

        IntegrationLog.objects.create(
            order=order,
            status_code="SUCCESS",
            raw_response=f"Sincronizado en {timezone.now()}: {'; '.join(detalles_log)}",
        )

        order.status = "SYNCED"
        order.save(update_fields=["status", "updated_at"])

        return {
            "order_id": str(order.id),
            "status": "SYNCED",
            "details": detalles_log,
        }

    except Order.DoesNotExist:
        logger.error(f"Orden no encontrada: {order_id}")
        raise

    except (OdooConfigurationError, OdooAuthenticationError) as exc:
        logger.error(f"Error de configuración/autenticación Odoo: {str(exc)}")

        try:
            order = Order.objects.get(id=order_id)

            IntegrationLog.objects.create(
                order=order,
                status_code="FAILED",
                raw_response=f"Error Odoo: {str(exc)}",
            )

            order.status = "FAILED"
            order.save(update_fields=["status", "updated_at"])

        except Exception as log_exc:
            logger.error(f"No se pudo guardar log de error: {str(log_exc)}")

        raise self.retry(exc=exc)

    except Exception as exc:
        logger.error(f"Error sincronizando orden {order_id}: {str(exc)}")

        try:
            order = Order.objects.get(id=order_id)

            IntegrationLog.objects.create(
                order=order,
                status_code="FAILED",
                raw_response=f"Error detectado: {str(exc)}",
            )

            order.status = "FAILED"
            order.save(update_fields=["status", "updated_at"])

        except Exception as log_exc:
            logger.error(f"No se pudo guardar log de falla: {str(log_exc)}")

        raise self.retry(exc=exc)