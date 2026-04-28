from django.urls import path 
from .views import health_check, testDbConection

urlpatterns = [
    path('health/', health_check),
    path('testdb/', testDbConection, name='test_db'),
]