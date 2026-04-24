"""This is permissions."""

from django.conf import settings
from rest_framework.permissions import BasePermission


class HasGatewayApiKey(BasePermission):
    message = 'API key inválida o ausente.'

    def has_permission(self, request, view):
        api_key = request.headers.get('x-api-key')
        origin = request.headers.get('x-origin')
        expected_key = getattr(settings, 'GATEWAY_API_KEY', None)
        expected_origin = getattr(settings, 'GATEWAY_ORIGIN', None)

        if not expected_key or not expected_origin:
            return False
        if not api_key or not origin:
            return False
        if api_key != expected_key:
            return False
        if origin != expected_origin:
            return False
        return True