from django.contrib import admin
from django.urls import path
from .views import HelloWorldView #de la vista hello world
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

#imports the aviews
from apps.views import (
    UserRegisterView,
    UserLoginView,
    UserListView,
    UserProfileUpdateView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    UserRoleStatusPatchView,
    UpdateProfileView
)


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
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('users/<uuid:pk>/', UserRoleStatusPatchView.as_view(), name="users-patch"),
    #tem
    path('profile/', UpdateProfileView.as_view(), name="user-profile"),

    #schema and docs
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('gateway-docs/', SpectacularSwaggerView.as_view(url='/user/api/v1/schema/'), name='gateway-swagger-ui'),    
]