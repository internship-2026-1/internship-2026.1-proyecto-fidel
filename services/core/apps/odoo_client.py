"""Listo se puede eliminar"""
# utility
import xmlrpc.client
# django
from django.conf import settings


class OdooConfigurationError(Exception):
    pass


class OdooAuthenticationError(Exception):
    pass


def validate_odoo_settings() -> None:
    required = {
        "ODOO_URL": getattr(settings, "ODOO_URL", None),
        "ODOO_DB": getattr(settings, "ODOO_DB", None),
        "ODOO_USERNAME": getattr(settings, "ODOO_USERNAME", None),
        "ODOO_API_KEY": getattr(settings, "ODOO_API_KEY", None),
    }

    missing = [key for key, value in required.items() if not value]
    if missing:
        raise OdooConfigurationError(
            f"Faltan variables Odoo: {', '.join(missing)}."
        )


def get_odoo_common_client():
    validate_odoo_settings()
    return xmlrpc.client.ServerProxy(f"{settings.ODOO_URL}/xmlrpc/2/common")


def get_odoo_models_client():
    validate_odoo_settings()
    return xmlrpc.client.ServerProxy(f"{settings.ODOO_URL}/xmlrpc/2/object")


def authenticate_odoo() -> int:
    common = get_odoo_common_client()
    uid = common.authenticate(
        settings.ODOO_DB,
        settings.ODOO_USERNAME,
        settings.ODOO_API_KEY,
        {},
    )
    if not uid:
        raise OdooAuthenticationError("Credenciales Odoo inválidas.")
    return uid


def get_odoo_session():
    uid = authenticate_odoo()
    models = get_odoo_models_client()
    return uid, models
