"""Creando vistas para odoo"""

import xmlrpc.client

#django
from django.conf import settings

#apps
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.decorators import api_view
from transaction.models import Order
from catalog.mongo_client import products_collection

#ejemplo: @api_view = vista simple basada en funcion
@api_view(['GET'])
def health_check(request):
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
    def post(self, request):
        try:
            #aguardo en postgre mediante orm
            orden = Order.objects.create(total=50.00)
            #aguardo en mongo median pymongo
            producto = {
                "name": request.data.get("product_name"),
                "category": "test"
            }
            products_collection.insert_one(producto)
            #retorno payload como responce
            return Response({
                "message": "Dato distribuido con exito Fidel",
                "postgres_status": f"orden {orden.order_id} guardado",
                "mongo_status": "producto guardado como documento"
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error: ": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
