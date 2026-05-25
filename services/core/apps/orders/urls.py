"""rutas para orders"""

from django.urls import path
from .views import OrderCreateListViews, OrderDetailViews, SimulandoPago, OrderByCustomerViews


urlpatterns = [
    path('orders/', OrderCreateListViews.as_view(), name='orders'),
    path('orders/<str:pk>/', OrderDetailViews.as_view(), name='orders-detail'),
    path("orders/<uuid:pk>/simularPago/", SimulandoPago.as_view(), name="simulate-payment"),
    path('orders/customer/<uuid:customer_id>/', OrderByCustomerViews.as_view(), name="orders-by-customer")
]