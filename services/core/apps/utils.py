"""utilitys for core"""

from rest_framework import status as http_status


def build_response(success: bool, message: str, body=None, status_code=None):
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