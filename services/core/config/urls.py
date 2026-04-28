from django.contrib import admin 
from django.urls import path, include

"""agregando url de admin"""

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
]