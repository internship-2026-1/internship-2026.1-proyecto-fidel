from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.utils import build_response
from datetime import datetime, timezone
from .models import Catalog
from .serializers import CatalogSerializers

#verificar si quito esto aqui 
class CatalogViews(APIView):
    """Listar y crear catalgo"""
    def get(self, request):
        """lista todos los catalogos"""
        catalogs = Catalog.objects.order_by('-created_at')
        serializer = CatalogSerializers(catalogs, many=True)

        payload = build_response(
            success=True,
            message='catalogos listados correctamente',
            body=serializer.data,
            status_code=status.HTTP_200_OK,
        )
        return Response(payload, status=status.HTTP_200_OK)
    
    def post(self, request):
        """crea un nuevo catalogo"""
        serializer = CatalogSerializers(data=request.data)

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
            message='Catalogo creado correctamente',
            body=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )
        return Response(payload, status=status.HTTP_201_CREATED)















