"""Modelo catalogs"""
import uuid
from django.db import models
from mongoengine import Document
from mongoengine import UUIDField, StringField, DateTimeField
from datetime import datetime

class Catalog(Document):
    """definiendo modelo catalog"""
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = StringField(required=True)
    description = StringField(default="")
    status = StringField(default="activo", choices=("activo", "inactivo"))
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "catalog"}

    def __str__(self):
        return self.name