from rest_framework import serializers
from apps.products.models import Product
from apps.catalog.models import Catalog

#listo
class ProductSerializers(serializers.Serializer):
    """serializers productos"""
    id = serializers.CharField(read_only=True)
    catalog = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    odoo_id = serializers.CharField(required=True)
    sku = serializers.CharField(max_length=100, required=True)
    name = serializers.CharField(required=True, max_length=100)
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    stock = serializers.IntegerField(required=False)
    description = serializers.CharField(default="")
    images = serializers.ListField(child=serializers.CharField(),required=False)
    specifications = serializers.DictField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        catalog_id = validated_data.pop("catalog", None)
        catalog = None

        if catalog_id:
            catalog = Catalog.objects(id=catalog_id).first()
            if not catalog:
                raise serializers.ValidationError({"catalog": 'catalogo no encontrado Fide'})
        product = Product(catalog=catalog, **validated_data)
        product.save()
        return product


    def update(self, instance, validated_data):
        if "catalog" in validated_data:
            catalog_id = validated_data.pop("catalog")
            if catalog_id:
                catalog = Catalog.objects(id=catalog_id).first()
                if not catalog:
                    raise serializers.ValidationError({"catalog": "catalogo no encontrado Fide 2."})
                instance.catalog = catalog
            else:
                instance.catalog = None

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

#listo
class SyncProductSerializers(serializers.Serializer):
    """syncroniza productos JSON a mongo"""
    odoo_id = serializers.CharField(required=True)
    sku = serializers.CharField(max_length=100, required=True)
    name = serializers.CharField(required=True)
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    stock = serializers.IntegerField(required=True)

#listo
class EnrichProductSerializers(serializers.Serializer):
    """Enriquece productos desde odoo"""
    description = serializers.CharField(required=False, allow_blank=True)
    images = serializers.ListField(child=serializers.CharField(), required=False)
    specifications = serializers.DictField(required=False)

    def validate(self, data):
        if not data:
            raise serializers.ValidationError("debe enviar un campo para enriquecer el producto")
        return data