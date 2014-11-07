from django.conf import settings

class DatabaseAppsRouter(object):
    """
    A router to control all database operations on models for different
    databases.

    In case an app is not set in settings.DATABASE_APPS_MAPPING, the router
    will fallback to the `default` database.

    Settings example:

    DATABASE_APPS_MAPPING = {'app1': 'db1', 'app2': 'db2'}
    """

    def db_for_read(self, model, **hints):
        """"Point all read operations to the specific database."""
        if model._meta.app_label in ['auth', 'contenttypes', 'sessions', 'sites', 'admin']:
            return settings.DATABASE_APPS_MAPPING.get(settings.BRAND)
        return settings.DATABASE_APPS_MAPPING.get(model._meta.app_label)

    def db_for_write(self, model, **hints):
        """Point all write operations to the specific database."""
        if model._meta.app_label in ['auth', 'contenttypes', 'sessions', 'sites', 'admin', 'djcelery']:
            return settings.DATABASE_APPS_MAPPING.get(settings.BRAND)
        return settings.DATABASE_APPS_MAPPING.get(model._meta.app_label)

    def allow_relation(self, obj1, obj2, **hints):
        """Allow any relation between apps that use the same database."""
        db_obj1 = settings.DATABASE_APPS_MAPPING.get(obj1._meta.app_label)
        db_obj2 = settings.DATABASE_APPS_MAPPING.get(obj2._meta.app_label)
        if db_obj1 and db_obj2:
            if db_obj1 == db_obj2:
                return True
            else:
                return False
        return None

    def allow_syncdb(self, db, model):
        """Make sure that apps only appear in the related database."""
        if model._meta.app_label in ['auth', 'contenttypes', 'sessions', 'sites', 'admin', 'djcelery']:
            return True

        if db in settings.DATABASE_APPS_MAPPING.values():
            return settings.DATABASE_APPS_MAPPING.get(model._meta.app_label) == db 
        elif settings.DATABASE_APPS_MAPPING.has_key(model._meta.app_label):
            # Here table will not be created 
            return False
        return None
    