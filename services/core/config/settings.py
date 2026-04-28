import os
from pathlib import Path

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
    'rest_framework',
    'api',# muesta toda la app de core

    #empezar a definir mis apps
    'catalog.apps.CatalogConfig',
    'transaction.apps.TransactionConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
        },
        "postgresql_db": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("CORE_DB_NAME", os.environ.get("CORE_POSTGRES_DB", "core_db")),
            "USER": os.environ.get("CORE_DB_USER", os.environ.get("CORE_POSTGRES_USER", "core_user")),
            "PASSWORD": os.environ.get("CORE_DB_PASSWORD", os.environ.get("CORE_POSTGRES_PASSWORD", "core_pass")),
            "HOST": os.environ.get("CORE_DB_HOST", os.environ.get("CORE_POSTGRES_HOST", "core_db")),
            "PORT": os.environ.get("CORE_DB_PORT", os.environ.get("CORE_POSTGRES_PORT", "5432")),
        },
        "mongodb": {
            "ENGINE": "django_mongodb_backend",
            "NAME": os.environ.get("MONGO_DB", "core_catalog"),
            "HOST": os.environ.get("MONGO_HOST", "mongodb"),
            "PORT": int(os.environ.get("MONGO_PORT", "27017")),
            "USER": os.environ.get("MONGO_USER", "core_mongo_user"),
            "PASSWORD": os.environ.get("MONGO_PASSWORD", "core_mongo_pass"),
            "OPTIONS": {
                "authSource": os.environ.get("MONGO_AUTH_SOURCE", "admin"),
            },
        },            
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

DATABASE_ROUTER= ['config.db_routers.DatabaseRouter']

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