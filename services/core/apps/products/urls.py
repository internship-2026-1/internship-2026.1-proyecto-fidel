from django.urls import path
from .views import (
    ProductsCreatedListedViews, 
    ProductsDetailsViews, 
    IntegrateProductsFromOdooViews, 
    SyncProductsFromJsonViews, 
    EnrichProductViews, 
    ProductsByCatalogNameView
    )

urlpatterns = [
    path('products/', ProductsCreatedListedViews.as_view(), name='products'),
    path("products/by-catalog/", ProductsByCatalogNameView.as_view(), name="products-by-catalog"),

    path('products/<str:pk>/', ProductsDetailsViews.as_view(), name='products-detail'),
    path('internal/sync-odoo-products/', IntegrateProductsFromOdooViews.as_view(), name='syn-odoo-products'),
    path('internal/sync-products/', SyncProductsFromJsonViews.as_view(), name='syn-products-json'),
    path('products/<str:sku>/enrich/', EnrichProductViews.as_view(), name='enrich-products'),
]
