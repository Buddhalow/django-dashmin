from importlib import import_module
from django.apps import AppConfig, apps

from django.utils.module_loading import autodiscover_modules


class DashminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashmin'

    def ready(self):
        dashboard_module = autodiscover_modules('dashboard')
        return super().ready()
