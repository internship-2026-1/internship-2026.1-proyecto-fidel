"this is views"

from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .permissions import HasGatewayApiKey
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserListSerializer, UserProfileUpdateSerializer #
from .utils import build_response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

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


class UserListView(APIView):
    """View list user."""
    authentication_classes = []
    permission_classes = [HasGatewayApiKey]

    @extend_schema(
        responses={200: UserListSerializer(many=True)},
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
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Buscar por nombre, apellido o email.',
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Número de página.',
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Tamaño de página (por defecto 20).',
            ),
        ],
    )
    def get(self, request):
        queryset = UserListSerializer.Meta.model.objects.all().order_by('-date_joined')
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )

        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get('page_size', 20))
        page = paginator.paginate_queryset(queryset, request)
        serializer = UserListSerializer(page, many=True)
        payload = build_response(
            success=True,
            message='Usuarios obtenidos correctamente.',
            body={
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'results': serializer.data,
            },
            status_code=status.HTTP_200_OK,
        )
        return Response(payload, status=status.HTTP_200_OK)


class UserProfileUpdateView(APIView):
    """Update authenticated user profile."""
    permission_classes = [IsAuthenticated, HasGatewayApiKey]

    def patch(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            user = serializer.save()
            payload = build_response(
                success=True,
                message='Profile updated successfully',
                body={
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'address': user.address,
                    'phone_number': user.phone_number,
                    'country': user.country,
                    'role': user.role,
                },
                status_code=status.HTTP_200_OK
            )
            return Response(payload, status=status.HTTP_200_OK)

        payload = build_response(
            success=False,
            message='Errors validation',
            body=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)