from django.contrib import admin
from django.urls import path
from .views import HelloWorldView #de la vista hello world
from apps.views import UserRegisterView, UserLoginView, UserListView, UserProfileUpdateView # Importar desde apps 
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    #admin
    path('admin/', admin.site.urls),
    #examples
    path('hello/', HelloWorldView.as_view(), name='hello-world'),
    #apps
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='user-profile-update'),

    #schema and docs
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('gateway-docs/', SpectacularSwaggerView.as_view(url='/user/api/v1/schema/'), name='gateway-swagger-ui'),    
]