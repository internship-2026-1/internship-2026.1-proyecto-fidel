from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
#duda

class HelloWorldView(APIView):
    """esto es para ver la vista de prueba"""
    def get(self, request):
        return Response({"message": "Hello, world si funciona o no?!"}, status=status.HTTP_200_OK)