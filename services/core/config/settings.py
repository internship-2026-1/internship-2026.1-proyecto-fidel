import os
from pathlib import Path
from mongoengine import connect
#import cloudinary #new

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-core-key')
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # terceros
    'rest_framework',
    'drf_spectacular',
    #falta
    'apps',# muesta toda la app de core

    #apps propios
    'apps.catalog',
    'apps.orders',
    'apps.products',
    'apps.transactions',
    'apps.payments',
    'transaction.apps.TransactionConfig',

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

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# config para usar postgres
DB_ENGINE = os.environ.get("CORES_DB_ENGINE", os.environ.get("DB_ENGINE", "sqlite")).lower()

#configurando  DATABASES con postgresql y mongodb.
if DB_ENGINE == "postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("CORE_DB_NAME", os.environ.get("CORE_POSTGRES_DB", "core_db")),
            "USER": os.environ.get("CORE_DB_USER", os.environ.get("CORE_POSTGRES_USER", "core_user")),
            "PASSWORD": os.environ.get("CORE_DB_PASSWORD", os.environ.get("CORE_POSTGRES_PASSWORD", "core_pass")),
            "HOST": os.environ.get("CORE_DB_HOST", os.environ.get("CORE_POSTGRES_HOST", "core_db")),
            "PORT": os.environ.get("CORE_DB_PORT", os.environ.get("CORE_POSTGRES_PORT", "5432")),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    #drf entiende que use drf-spectacular para generar el esquema OpenAPI/Swagger
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    #para que las respuestas respondan en JSON
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],   
}

# config drf-spectacular doc para swagger
SPECTACULAR_SETTINGS = {
    'TITLE': 'Core Service API',
    'DESCRIPTION': 'API documentation for core microservice',
    'VERSION': '1.0.0',
    'SERVERS': [
        {
            'url': '/core/api/v1',
            'description': 'Gateway base URL',
        }
    ],
}

#gate keys
GATEWAY_API_KEY = os.environ.get('GATEWAY_API_KEY')
GATEWAY_ORIGIN = os.environ.get('GATEWAY_ORIGIN')

#ODOO
ODOO_URL = os.environ.get('ODOO_URL')
ODOO_DB = os.environ.get('ODOO_DB')
ODOO_USERNAME = os.environ.get('ODOO_USERNAME')
ODOO_API_KEY = os.environ.get('ODOO_API_KEY')

#mongo engine
connect(
    db=os.getenv("MONGO_DB", "core_catalog"),
    username=os.getenv("MONGO_USER", "core_mongo_user"),
    password=os.getenv("MONGO_PASSWORD", "core_mongo_pass"),
    host=f'mongodb://{os.getenv("MONGO_HOST", "mongodb")}:{os.getenv("MONGO_PORT", "27017")}/{os.getenv("MONGO_DB", "core_catalog")}',
    authentication_source=os.getenv("MONGO_AUTH_SOURCE", "admin"),
    alias="default",
)

# config celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')

#config de cloudinary
#cloudinary.config(
#    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
#    api_key=os.environ.get('CLOUDINARY_API_KEY'),
#    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
#    secure=True
#)

# config cors
##CORS_ALLOWED_ORIGINS = [
##    "http://localhost:5173",
##    "http://127.0.0.1:5173",
##]
##
##CORS_ALLOW_CREDENTIALS = True