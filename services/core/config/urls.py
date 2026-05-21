"""Rutas principales del proyecto."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    #Django admin y apps
    path("admin/", admin.site.urls),
    path("apps/", include("apps.urls")),
]