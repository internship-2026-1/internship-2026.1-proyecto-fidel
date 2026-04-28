#import uuid
#transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

class Product:
    """Model productos"""
    @staticmethod
    def create(name, price, metadata={}):
        from .mongo_client import products_collection
        product = {
            "name": name,
            "price": price,
            "metadata":metadata
        }
        return products_collection.insert_one(product)