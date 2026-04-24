"""This is utilities"""

from rest_framework import status as http_status
from django.core import signing


def build_response(*, success, message, body=None, status_code=None):
    if body is None:
        body = []
    if status_code is None:
        status_code = http_status.HTTP_200_OK if success else http_status.HTTP_400_BAD_REQUEST

    payload = {
        "success": success,
        "message": message,
        "body": body,
        "status": status_code,
    }
    return payload


def generate_password_reset_token(user):
    payload = {
        'user_id': str(user.id),
        'email': user.email,
    }
    return signing.dumps(payload, salt='password-reset')


def verify_password_reset_token(token, max_age=900):
    return signing.loads(token, salt='password-reset', max_age=max_age)