"""this is exceptions."""

from rest_framework.views import exception_handler
from rest_framework import status as http_status

from .utils import build_response


def standard_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        payload = build_response(
            success=False,
            message="Error interno del servidor.",
            body=[],
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        from rest_framework.response import Response

        return Response(payload, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)

    status_code = response.status_code
    detail = response.data

    payload = build_response(
        success=False,
        message="Error en la solicitud.",
        body=detail,
        status_code=status_code,
    )
    response.data = payload
    return response