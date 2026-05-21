from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.utils import build_response
import traceback #quitar para manejar errores
from datetime import datetime, timezone
from .models import Product
from .serializers import ProductSerializers, SyncProductSerializers, EnrichProductSerializers
from django.conf import settings
from apps.permissions import HasGatewayApiKey
from apps.odoo_client import OdooConfigurationError, OdooAuthenticationError, get_odoo_session
from .OdooClient import fetch_products
from apps.catalog.models import Catalog
 
#listo listar-crear products
class ProductsCreatedListedViews(APIView):
    """Listar-Crear products"""
    def get(self, request):
        """obtener todos los productos"""
        productos = Product.objects.order_by('-created_at')
        serializer = ProductSerializers(productos, many=True)

        payload = build_response(
            success=True,
            message='producto listado: ',
            body=serializer.data,
            status_code=status.HTTP_200_OK,
        )
        return Response(payload, status=status.HTTP_200_OK)

    def post(self, request):
        """crear productos"""
        serializer = ProductSerializers(data=request.data)

        if not serializer.is_valid():
            payload = build_response(
                success=False,
                message='datos invalidos',
                body=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(created_at=datetime.now(timezone.utc))

        payload = build_response(
            success=True,
            message='Prodcuto  creado correctamente',
            body=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )
        return Response(payload, status=status.HTTP_201_CREATED)

#crud-Listo --falta post
class ProductsDetailsViews(APIView):
    """get producto por id"""
    def get(self, request, pk):
        producto = Product.objects(id=pk).first()

        if not producto:
            payload= build_response(
                success=False,
                message='Producto no encontrado',
                body={'Detail:':pk},
                status_code=status.HTTP_404_NOT_FOUND,
            )
            return Response(payload, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializers(producto)
        payload = build_response(
            success=True,
            message='tu producto',
            body=serializer.data,
            status_code=status.HTTP_200_OK,
        )
        return Response(payload, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """put producto por id"""
        producto = Product.objects(id=pk).first()

        if not producto:
            payload = build_response(
                success=False,
                message='producto no encontrado',
                body={'detail': pk},
                status_code=status.HTTP_404_NOT_FOUND,
            )
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializers(producto, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            payload = build_response(
                success=True,
                message='producto actualizado',
                body=serializer.data,
                status_code=status.HTTP_200_OK,
            )
            return Response(payload, status=status.HTTP_200_OK)

        payload = build_response(
            success=False,
            message='datos inválidos',
            body=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """delete producto por id"""
        producto = Product.objects(id=pk).first()

        if not producto:
            payload = build_response(
                success=False,
                message='producto no encontrado',
                body={'detail': pk},
                status_code=status.HTTP_404_NOT_FOUND,
            )
            return Response(payload, status=status.HTTP_404_NOT_FOUND)
        
        producto.delete()
        payload = build_response(
            success=True,
            message='producto eliminado',
            body=None, #{'detail': pk}
            status_code=status.HTTP_204_NO_CONTENT,
        )
        return Response(payload, status=status.HTTP_204_NO_CONTENT)

#listo ingration odo a mongodb
class IntegrateProductsFromOdooViews(APIView):
    """Trae los productos de odoo y crea o actualiza mongodb"""

    def post(self, request):
        try:
            limit = int(request.query_params.get('limit',100))
            offset = int(request.query_params.get('offset', 0))

            products = fetch_products(limit=limit, offset=offset)

            created_count = 0
            updated_count = 0
            synced_products = []

            for item in products:
                product = Product.objects(sku=item["sku"]).first()

                if product:
                    product.odoo_id = item.get("odoo_id")
                    product.name = item.get("name", product.name)
                    product.base_price = item.get("base_price", product.base_price)
                    product.stock = item.get("stock", product.stock)
                    product.images = item.get("images", product.images)
                    product.updated_at = datetime.utcnow()
                    product.save()

                    updated_count += 1
                else:
                    product = Product(
                        odoo_id=item.get("odoo_id"),
                        sku=item.get("sku"),
                        name=item.get("name", ""),
                        base_price=item.get("base_price", 0),
                        stock=item.get("stock", 0),
                        images=item.get("images", []),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    product.save()

                    created_count += 1

                synced_products.append(ProductSerializers(product).data)

            payload = build_response(
                success=True,
                message='productos sincronizados listos',
                body={
                    "synced": len(products),
                    "created": created_count,
                    "updated": updated_count,
                    "limit": limit,
                    "offset": offset,
                    "products": synced_products,
                },
                status_code=status.HTTP_200_OK,
            )
            return Response(payload, status=status.HTTP_200_OK)

        except OdooAuthenticationError as e:
            payload = build_response(
                success=False,
                message="error al autenticar en odoo",
                body={"detail": str(e)},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
            return Response(payload, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            print(traceback.format_exc())

            payload = build_response(
                success=False,
                message="eror interno al sincronizar productos desde Odoo",
                body={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#listo odoo sync -upsert
#Odoo → sync-products → MongoDB products
class SyncProductsFromJsonViews(APIView):
    """Recibe una lista Odoo/JSON de productos y crea o actualiza en MongoDB"""

    def post(self, request):
        serializer = SyncProductSerializers(data=request.data, many=True)

        if not serializer.is_valid():
            payload = build_response(
                success=False,
                message='Datos inválidos',
                body=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        try:
            created_count = 0
            updated_count = 0
            synced_products = []

            for data in serializer.validated_data:
                product = Product.objects(sku=data["sku"]).first()

                if product:
                    product.odoo_id = data["odoo_id"]
                    product.name = data["name"]
                    product.base_price = data.get("base_price", product.base_price)
                    product.stock = data.get("stock", product.stock)
                    product.updated_at = datetime.utcnow()
                    product.save()

                    updated_count += 1

                else:
                    product = Product(
                        odoo_id=data["odoo_id"],
                        sku=data["sku"],
                        name=data["name"],
                        base_price=data.get("base_price", 0),
                        stock=data.get("stock", 0),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    product.save()

                    created_count += 1

                synced_products.append(ProductSerializers(product).data)

            payload = build_response(
                success=True,
                message='Productos sincronizados correctamente',
                body={
                    "synced": len(synced_products),
                    "created": created_count,
                    "updated": updated_count,
                    "products": synced_products,
                },
                status_code=status.HTTP_200_OK,
            )
            return Response(payload, status=status.HTTP_200_OK)

        except Exception as e:
            print(traceback.format_exc())

            payload = build_response(
                success=False,
                message='Error interno al sincronizar productos',
                body={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#listo migrado
class EnrichProductViews(APIView):
    """----enriqueciendo solo campos permitidos description, images, specifications"""
    def patch(self, request, sku):
        serializers = EnrichProductSerializers(data=request.data)

        if not serializers.is_valid():
            payload = build_response(
                success=False,
                message='datos invalidos',
                body=serializers.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects(sku=sku).first()

            if not product:
                payload = build_response(
                    success=False,
                    message='producto no encontrado',
                    body={'sku': sku},
                    status_code=status.HTTP_404_NOT_FOUND,
                )
                return Response(payload, status=status.HTTP_404_NOT_FOUND)
            
            data = serializers.validated_data

            if "description" in data:
                product.description = data["description"]
            if "images" in data:
                product.images = data["images"]
            if "specifications" in data:
                product.specifications = data["specifications"]

            product.updated_at = datetime.utcnow()
            product.save()

            response_data = ProductSerializers(product).data

            payload = build_response(
                success=True,
                message='producto enriquecido correctamente',
                body={
                    "product": response_data
                },
                status_code=status.HTTP_200_OK,
            )
            return Response(payload, status.HTTP_200_OK)

        except Exception as e:
            print(traceback.format_exc())#quiero

            payload = build_response(
                success=False,
                message='error interno al enriquecer el producto',
                body={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            return Response(payload, status.HTTP_500_INTERNAL_SERVER_ERROR)

# adi
class ProductsByCatalogNameView(APIView):
    """listar productos por nombre de catalogo"""

    def post(self, request):
        catalog_name = request.data.get('name')

        if not catalog_name:
            payload = build_response(
                success=False,
                message='el campo name es requerido',
                body={"name": "enviar nombre del catalgo"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        catalog = Catalog.objects(name=catalog_name).first()

        if not catalog:
            payload = build_response(
                success=False,
                message="catalogo no encontrado",
                body={"name": catalog_name},
                status_code=status.HTTP_404_NOT_FOUND,
            )
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

        products = Product.objects(catalog=catalog).order_by("-created_at")
        serializer = ProductSerializers(products, many=True)

        payload = build_response(
            success=True,
            message="productos listados por cotalago corectamente",
            body={
                "catalog": {
                    "id": str(catalog.id),
                    "name": catalog.name,
                },
                "count": len(serializer.data),
                "products": serializer.data,
            },
            status_code=status.HTTP_200_OK,
        )
        return Response(payload, status=status.HTTP_200_OK)
