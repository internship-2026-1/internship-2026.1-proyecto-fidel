import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-key')
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',#cambio JWT
    'drf_spectacular',
    'apps', # Registrar la app de usuarios
    "corsheaders", #cors
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "corsheaders.middleware.CorsMiddleware",#cors
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
DB_ENGINE = os.environ.get("USERS_DB_ENGINE", os.environ.get("DB_ENGINE", "sqlite")).lower()
#inicio cambio
if DB_ENGINE == "postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("USERS_DB_NAME", os.environ.get("POSTGRES_DB", "users_db")),
            "USER": os.environ.get("USERS_DB_USER", os.environ.get("POSTGRES_USER", "users_user")),
            "PASSWORD": os.environ.get("USERS_DB_PASSWORD", os.environ.get("POSTGRES_PASSWORD", "users_pass")),
            "HOST": os.environ.get("USERS_DB_HOST", os.environ.get("POSTGRES_HOST", "users_db")),
            "PORT": os.environ.get("USERS_DB_PORT", os.environ.get("POSTGRES_PORT", "5432")),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
#fin cambio
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#realize cambios aqui despues de listar usaurios quiza afecte
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',        
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],   
    'EXCEPTION_HANDLER': 'apps.exceptions.standard_exception_handler',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Users Service API',
    'DESCRIPTION': 'API documentation for users microservice',
    'VERSION': '1.0.0',
    'SERVERS': [
        {
            'url': '/user/api/v1',
            'description': 'Gateway base URL',
        }
    ],
    'POSTPROCESSING_HOOKS': [
        'drf_spectacular.hooks.postprocess_schema_enums',
        'core.schema.inject_gateway_servers',
    ],
    'SECURITY': [{'BearerAuth': []}],
    'COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
                'description': 'Agregar el token en el header Authorization: Bearer <token>',
            }
        }
    },
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,
        'displayRequestDuration': True,
    },
}

AUTH_USER_MODEL = 'apps.User'

GATEWAY_API_KEY = os.environ.get('GATEWAY_API_KEY')
GATEWAY_ORIGIN = os.environ.get('GATEWAY_ORIGIN')

#resett and token
PASSWORD_RESET_TOKEN_MAX_AGE = int(os.environ.get('PASSWORD_RESET_TOKEN_MAX_AGE', '900'))
PASSWORD_RESET_CONFIRM_URL = os.environ.get(
    'PASSWORD_RESET_CONFIRM_URL',
    'http://localhost:8080/user/api/v1/auth/password-reset/confirm/'
)

# config cors
##CORS_ALLOWED_ORIGINS = [
##    "http://localhost:5173",
##    "http://127.0.0.1:5173",
##]
##
##CORS_ALLOW_CREDENTIALS = True


DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'no-reply@example.com')

EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', '1') == '1'