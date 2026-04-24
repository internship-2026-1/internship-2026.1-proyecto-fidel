"""para inicializar"""

# Django
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework import serializers

#models
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    """Created users."""
    password = serializers.CharField(write_only=True, min_length=8)
    phone = serializers.CharField(write_only=True)
    role = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password', 
            'first_name', 
            'last_name', 
            'phone', 
            'created_at',
            'role'
            )
    
    def validate_username(self, value):
        if len(value) < 3 or len(value) > 30:
            raise serializers.ValidationError('username debe tener entre 3 y 30 caracteres.')
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('este nombre de usuario ya existe.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('este correo ya existe.')
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_phone(self, value):
        if len(value) < 7:
            raise serializers.ValidationError('numero de telefono invelido.')
        return value

    def create(self, validated_data):
        phone = validated_data.pop('phone')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            password = password,
            phone_number = phone,
            **validated_data
            )
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    """For login users."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError('Credenciales inválidas.')

        if not user.is_active:
            raise serializers.ValidationError('Usuario inactivo.')

        attrs['user'] = user
        return attrs


class UserListSerializer(serializers.ModelSerializer):
    """list user"""
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'address',
            'phone_number',
            'country',
            'date_joined',
        )

class PasswordResetRequestSerializer(serializers.Serializer):
    """reset request"""
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """reset confirmation"""
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_new_password(self, value):
        validate_password(value)
        return value


#corrigiendo serializer de update to profile ()
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Defino que campos actualizar y que no"""
    class Meta:
        model = User
        fields = (
            'email',
            'role',
            'first_name',
            'last_name',
            'address',
            'phone_number',
            'country'
        )
        read_only = (
            'username',
            'email',
            'role',
        )
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'address': {'required': False, 'allow_blank': True},
            'phone_number': {'required': False, 'allow_blank': True},
            'country': {'required': False, 'allow_blank': True},
        }

        # para un update tengo que obtener los campos 
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.address = validated_data.get('address', instance.address)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.country = validated_data.get('country', instance.country)
        instance.save()
        return instance