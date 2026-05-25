"this is views"

from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .permissions import HasGatewayApiKey

from .utils import build_response, generate_password_reset_token, verify_password_reset_token
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


# imports the apps
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserListSerializer,
    UserProfileUpdateSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserRoleStatusPatchSerializer,
)

from django.conf import settings
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired
#model
from .models import User
# capturar error
import traceback

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

        try:
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
        
        except Exception as e:
            print("ERROR REAL:", type(e).__name__, str(e))
            traceback.print_exc()
            raise e


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
                    'user': {
                        'id': str(user.id),
                        'email': user.email,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': user.role,
                    }                    
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

# en esta class actualiza mediante usuario autenticado
class UserProfileUpdateView(APIView):
    """Update authenticated user profile."""
    permission_classes = [IsAuthenticated, HasGatewayApiKey]

    def patch(self, request):
        data = request.data.copy()

        #ignoro estos camopos
        data.pop('email', None)
        data.pop('username', None)
        data.pop('role', None)

        serializer = UserProfileUpdateSerializer(
            request.user,
            data=data,
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




class PasswordResetRequestView(APIView):
    """Views reset request"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)

        if not serializer.is_valid():
            payload = build_response(
                success=False,
                message='Errors validation',
                body=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()

        if user:
            token = generate_password_reset_token(user)
            reset_link = f"{settings.PASSWORD_RESET_CONFIRM_URL}?token={token}"

            send_mail(
                subject='recuperación de contraseña',
                message=(
                    'se solicito un restablecimiento de contraseña.\n\n'
                    f'usa este enlace o token para continuar:\n{reset_link}\n\n'
                    f'Token: {token}'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

        payload = build_response(
            success=True,
            message='Se ha enviado un correo con las instrucciones.',
            body={'token: ':token}, #recordar eliminar la vista del token
            status_code=status.HTTP_200_OK,
        )
        return Response(payload, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """Views reset confirmation."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if not serializer.is_valid():
            payload = build_response(
                success=False,
                message='Errors validation',
                body=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            data = verify_password_reset_token(
                token,
                max_age=settings.PASSWORD_RESET_TOKEN_MAX_AGE
            )
        except SignatureExpired:
            payload = build_response(
                success=False,
                message='token expirado',
                body={'detail': 'el token ha expirado.'},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        except BadSignature:
            payload = build_response(
                success=False,
                message='token invalido',
                body={'detail': 'al token no es valido.'},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(
            id=data['user_id'],
            email=data['email']
        ).first()

        if not user:
            payload = build_response(
                success=False,
                message='usuario no encontrado',
                body={'detail': 'no se encontro el usuario asociado al token.'},
                status_code=status.HTTP_404_NOT_FOUND,
            )
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()

        payload = build_response(
            success=True,
            message='la contraseña ha sido actualizada exitosamente.',
            body={},
            status_code=status.HTTP_200_OK,
        )
        return Response(payload, status=status.HTTP_200_OK)

# cambios definidos por metodo patch
class UserRoleStatusPatchView(APIView):
    def patch(self, request, pk):
        user = User.objects.filter(id=pk).first()

        if not user:
            payload = build_response(
                success=False,
                message='Usuario no encontrado',
                body={'id': pk},
                status_code=status.HTTP_404_NOT_FOUND,
            )
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

        serializer = UserRoleStatusPatchSerializer(
            user,
            data=request.data,
            partial=True
        )

        if not serializer.is_valid():
            payload = build_response(
                success=False,
                message='Datos invalidos',
                body=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        payload = build_response(
            success=True,
            message='Usuario actualizado correctamente',
            body=serializer.data,
            status_code=status.HTTP_200_OK,
        )

        return Response(payload, status=status.HTTP_200_OK)

#deje este para un endpoint rapido y no destruir el update patch anterior
class UpdateProfileView(APIView):
    """ver y actualizar perfil del usuario autenticado"""
    permission_classes = [IsAuthenticated, HasGatewayApiKey]

    def get(self, request):
        user = request.user

        payload = build_response(
            success=True,
            message='Perfil obtenido correctamente',
            body={
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'address': user.address,
                'phone_number': user.phone_number,
                'country': user.country,
                'role': user.role,
                'status': user.status,
            },
            status_code=status.HTTP_200_OK,
        )

        return Response(payload, status=status.HTTP_200_OK)

    def put(self, request):
        data = request.data.copy()

        data.pop('id', None)
        data.pop('username', None)
        data.pop('email', None)
        data.pop('role', None)
        data.pop('status', None)
        data.pop('password', None)

        serializer = UserProfileUpdateSerializer(
            request.user,
            data=data,
            partial=True
        )

        if serializer.is_valid():
            user = serializer.save()

            payload = build_response(
                success=True,
                message='Perfil actualizado correctamente',
                body={
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'address': user.address,
                    'phone_number': user.phone_number,
                    'country': user.country,
                    'role': user.role,
                    'status': user.status,
                },
                status_code=status.HTTP_200_OK,
            )

            return Response(payload, status=status.HTTP_200_OK)

        payload = build_response(
            success=False,
            message='Datos inválidos',
            body=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

        return Response(payload, status=status.HTTP_400_BAD_REQUEST)