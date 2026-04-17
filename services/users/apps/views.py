"this is views"

from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .permissions import HasGatewayApiKey
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserListSerializer
from .utils import build_response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework_simplejwt.tokens import RefreshToken

class UserRegisterView(APIView):
    """created users view."""
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserRegisterSerializer,
        responses={201: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT, 401: OpenApiTypes.OBJECT},
        parameters=[
            OpenApiParameter(
                name='x-api-key',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=False,
                description='API key requerida por el gateway.',
            ),
            OpenApiParameter(
                name='x-origin',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=False,
                description='Origen requerido por el gateway.',
            ),
        ],
    )

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            payload = build_response(
                success=True,
                message='Users created successfully',
                body={
                    'id': str(user.id),
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                status_code=status.HTTP_201_CREATED
            )
            return Response(payload, status=status.HTTP_201_CREATED)
        payload = build_response(
            success=False,
            message='Errors validation',
            body=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """User login view."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)

            payload = build_response(
                success=True,
                message='Login successful',
                body={
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
                status_code=status.HTTP_200_OK
            )
            return Response(payload, status=status.HTTP_200_OK)
        payload = build_response(
            success=False,
            message="Invalid credentials",
            body=serializer.errors,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

        return Response(payload, status=status.HTTP_401_UNAUTHORIZED)