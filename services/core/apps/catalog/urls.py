from django.urls import path
from .views import CatalogViews, CatalogDetailViews

urlpatterns = [
    path('catalogs/', CatalogViews.as_view(), name='catalogs'),
    path("catalogs/<str:pk>/", CatalogDetailViews.as_view(), name="catalogos-detail")
]