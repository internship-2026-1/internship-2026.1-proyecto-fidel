from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from transaction.models import Order
from catalog.mongo_client import products_collection



@api_view(['GET'])
def health_check(request):
    return Response({
        "success": True,
        "message": "Core service healthy.",
        "data": {
            "service": "core",
            "health": "ok"
        },
        "status": 200
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def testDbConection(request):
    """para verificar si funciona de manera hibrida luego cambiarlo"""
    try:
        #intento aguardarlo en postgre mendiante orm
        orden = Order.objects.create(total=50.00)
        #intento guardarlo en mongo mediante pyumongo
        producto = {
            "name": request.data.get("product_name"),
            "category": "test"
        }
        products_collection.insert_one(producto)

        #luego mandar este response en un payload
        return Response({

            #"message":"dato distribuido con exito"
            "message": "dato distribuido con exito",
            "postgres_status": f"orden {orden.order_id} guardado",
            "mongo_status": "producto guardado"
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error: ": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)