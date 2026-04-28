class DatabaseRouter:
    """aqui voy a controlar que datos van las db segun mi app"""

    # mongo
    mongo_apps = {'catalog'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.mongo_apps:
            return 'mongodb'
        return 'default' # mi default ahora es postgres

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.mongo_apps:
            return 'mongodb'
        return 'default' # siempre cae en postgres

    def allow_relation(self, obj1, obj2, **hints):
        """permite la relacion si ambas estan en la misma base de datos"""
        if obj1._meta.app_label in self.mongo_apps or \
           obj2._meta.app_label in self.mongo_apps:
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.mongo_apps:
            return db == 'mongodb'
        return db == 'default'
        