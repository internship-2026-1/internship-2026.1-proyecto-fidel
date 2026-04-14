"""para inicializar"""

# Django
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    phone = serializers.CharField(write_only=True)
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
            'created_at'
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