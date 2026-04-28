import os
from pymongo import MongoClient

# Configuración desde variables de entorno
MONGO_HOST = os.environ.get("MONGO_HOST", "mongodb")
MONGO_PORT = int(os.environ.get("MONGO_PORT", "27017"))
MONGO_NAME = os.environ.get("MONGO_DB", "core_catalog")
MONGO_USER = os.environ.get("MONGO_USER", "core_mongo_user")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", "core_mongo_pass")
MONGO_AUTH_SOURCE = os.environ.get("MONGO_AUTH_SOURCE", "admin")

# Cliente autenticado contra MongoDB
client = MongoClient(
    host=MONGO_HOST,
    port=MONGO_PORT,
    username=MONGO_USER,
    password=MONGO_PASSWORD,
    authSource=MONGO_AUTH_SOURCE,
)

# Base de datos
db = client[MONGO_NAME]

# Colección
products_collection = db["products"]