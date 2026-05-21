# utility
import xmlrpc.client
# django
from django.conf import settings
from apps.odoo_client import get_odoo_session

# el inge dijo que podiamos usar claudinary

def fetch_products(limit=100, offset=0):
    uid, models = get_odoo_session()

    records = models.execute_kw(
        settings.ODOO_DB,
        uid,
        settings.ODOO_API_KEY,
        "product.product",
        "search_read",
        [[]],
        {
            "fields": [
                "id",
                "default_code",
                "name",
                "list_price",
                "qty_available",
                "image_1920",
            ],
            "limit": limit,
            "offset": offset,
        },
    )

    products = []

    for record in records:
        odoo_id = str(record.get("id"))
        sku = record.get("default_code") or f"ODOO-{odoo_id}"
        image = record.get("image_1920")

        products.append(
            {
                "odoo_id": odoo_id,
                "sku": sku,
                'name': record.get("name") or "",
                "base_price": record.get("list_price") or 0,
                "stock": int(record.get("qty_available") or 0),
                "images": [image] if image else [],
            }
        )

    return products