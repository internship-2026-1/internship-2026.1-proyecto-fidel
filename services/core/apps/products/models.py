import uuid
from django.db import models
from mongoengine import Document
from mongoengine import StringField, IntField, DecimalField, DateTimeField, ListField, DictField, ReferenceField, UUIDField
from datetime import datetime, timezone
from apps.catalog.models import Catalog

class Product(Document):
    """modelo para productos"""
    #en clase dijo usar uuid
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    catalog = ReferenceField(Catalog, required=False, null=True)
    # campos que recibo desde odoo
    odoo_id = StringField(required=True)
    sku = StringField(required=True, unique=True, max_length=100)
    base_price = DecimalField(min_value=0, precision=2, default=0)
    stock = IntField(min_value=0, default=0)
    # campos que el admin pueda enriquecer
    name = StringField(required=True, max_length=100)
    description = StringField(default="")
    images = ListField(StringField(), default=lambda: [])
    specifications = DictField(default=lambda: {})
    # fechas interno
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    status = StringField(default="activo", choices=("activo", "inactivo", "agotado"))

    meta = {
        "collection": "products",
        "indexes": [
            "sku",
            "odoo_id",
        ]
        }

    def __str__(self):
        return self.sku