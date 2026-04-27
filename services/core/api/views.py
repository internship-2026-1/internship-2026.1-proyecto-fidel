from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


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