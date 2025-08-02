"""
Exports app configuration for Propter-Optimis Sports Analytics Platform.
"""
from django.apps import AppConfig


class ExportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.exports'
    verbose_name = 'Exports'
