from rest_framework import serializers
from apps.catalog.models import Catalog
from datetime import datetime

#listo
class CatalogSerializers(serializers.Serializer):
    """serializers catalog"""
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=["activo", "inactivo"], default="activo", required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        catalog = Catalog(**validated_data)
        catalog.save()
        return catalog
    
    def update(self, instance, validated_data):
        allowed_fields = ["name", "description", "status"]
        for key, value in validated_data.items():
            setattr(instance, key, value)
        
        instance.updated_at = datetime.utcnow()
        instance.save()
        return instance

    meta = {"collection": "catalog"}

    def __str__(self):
        return self.name