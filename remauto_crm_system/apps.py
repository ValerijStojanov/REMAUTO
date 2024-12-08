from django.apps import AppConfig


class RemautoCrmSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'remauto_crm_system'
    
    def ready(self):
        import remauto_crm_system.signals
