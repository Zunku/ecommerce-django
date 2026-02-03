from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    # ready method is called when the app is ready
    def ready(self):
        # Importing signals when the app is inicialized
        import store.signals.receivers