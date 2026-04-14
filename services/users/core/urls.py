from django.contrib import admin
from django.urls import path
from .views import HelloWorldView #de la vista hello world
from apps.views import UserRegisterView  # Importar desde apps ejemplo 1
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', HelloWorldView.as_view(), name='hello-world'), #ejmplo nada mas
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('gateway-docs/', SpectacularSwaggerView.as_view(url='/user/api/v1/schema/'), name='gateway-swagger-ui'),    
]