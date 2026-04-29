from django.contrib import admin 
from django.urls import path
from apps.views import health_check, TestConnection

"""agregando url de admin"""

urlpatterns = [
    #admin
    path('admin/', admin.site.urls),
    #check
    path('health/',health_check),
    path('test-db/',TestConnection.as_view(), name='test_db')
]