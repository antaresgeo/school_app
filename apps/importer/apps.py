from django.apps import AppConfig


class ImporterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.importer'

    def ready(self):
        import apps.importer.templatetags.importer_extras
        import apps.importer.signals
