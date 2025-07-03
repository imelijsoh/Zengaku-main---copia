from django.apps import AppConfig


class GakuseiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gakusei'

    def ready(self):
        import gakusei.signals