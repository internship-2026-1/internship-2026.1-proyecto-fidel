"""Comprobando estado salud de apps."""

# Django
from django.conf import settings

# DRF
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

# Apps
from transaction.models import Order
#from .mongo_client import products_collection
from .mongo_client import health_collection

# utils
from .utils import build_response

# permissions
from .permissions import HasGatewayApiKey

# Odoo
from .odoo_client import (
    OdooConfigurationError,
    OdooAuthenticationError,
    get_odoo_session,
)

#ejemplo: @api_view = vista simple basada en funcion
@api_view(['GET'])
def health_check(request):
    """estado de salud core-service"""
    return Response({
        "sucess": True,
        "message": "core service healty.",
        "data":{
            "service": "core",
            "health": "ok"
        },
        "status": 200
    }, status=status.HTTP_200_OK)


#ejemplo principal: APIView = vista basada en clase
class TestConnection(APIView):
    """estado de salud distribucion de DB"""
    def post(self, request):
        try:
            #aguardo en postgre mediante orm
            orden = Order.objects.create(total=50.00)
            #aguardo en mongo median pymongo
            producto = {
                "name": request.data.get("product_name"),
                "category": "test"
            }
            health_collection.insert_one(producto)
            #retorno payload como responce
            return Response({
                "message": "Dato distribuido con exito",
                "postgres_status": f"orden {orden.order_id} guardado",
                "mongo_status": "producto guardado como documento"
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error: ": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# obtengo los productos de odoo sin formato
class CoreOdooProductsViews(APIView):
    """ejemplo dado por el inge"""
    authentication_classes = []
    permission_classes = [HasGatewayApiKey]

    def get(self, request):
        try:
            limit = int(request.query_params.get("limit", 100))
            offset = int(request.query_params.get("offset", 0))

            uid, models = get_odoo_session()

            fields_meta = models.execute_kw(
                settings.ODOO_DB,
                uid,
                settings.ODOO_API_KEY,
                "product.product",
                "fields_get",
                [],
                {"attributes": ["string", "type"]},
            )
            field_names = list(fields_meta.keys())

            records = models.execute_kw(
                settings.ODOO_DB,
                uid,
                settings.ODOO_API_KEY,
                "product.product",
                "search_read",
                [[]],
                {
                    "fields": field_names,
                    "limit": limit,
                    "offset": offset,
                },
            )

            total = models.execute_kw(
                settings.ODOO_DB,
                uid,
                settings.ODOO_API_KEY,
                "product.product",
                "search_count",
                [[]],
            )

            payload = build_response(
                success=True,
                message="productos Odoo obtenidos correctamente. ",
                body={
                    "count": total,
                    "limit": limit,
                    "offset": offset,
                    "fields": field_names,
                    "results": records,
                },
                status_code=status.HTTP_200_OK
            )
            return Response(payload, status=status.HTTP_200_OK)

        except OdooConfigurationError as e:
            payload = build_response(
                success=False,
                message='configuracion odoo incompleto',
                body={'detail: ': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ),
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except OdooAuthenticationError as e:
            payload = build_response(
                success=False,
                message='credenciales de odoo invalidas',
                body={'detail: ': str(e)},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
            return Response(payload, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            payload = build_response(
                success=False,
                message='Error interno del servidor.',
                body={'detail: ': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            return Response(payload, status.HTTP_500_INTERNAL_SERVER_ERROR)

