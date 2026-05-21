from django.urls import path
from .views import CatalogViews

urlpatterns = [
    path('catalogs/', CatalogViews.as_view(), name='catalogs')
]