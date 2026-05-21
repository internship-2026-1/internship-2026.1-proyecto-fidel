"""Rutas internas de apps."""
from django.urls import include, path
from .views import health_check, TestConnection, CoreOdooProductsViews


urlpatterns = [
    #salud
    path('health-check/', health_check),
    path('test-db/', TestConnection.as_view(), name='test-db'),
    #Odoo
    path('products-odoo/sinformat/', CoreOdooProductsViews.as_view(), name='odoo-products-sinformato'),
    
    #Apps
    path("catalogs/", include("apps.catalog.urls")),
    path("orders/", include("apps.orders.urls")),
    path("products/", include("apps.products.urls")),
    path("transactions/", include('apps.transactions.urls'))
]