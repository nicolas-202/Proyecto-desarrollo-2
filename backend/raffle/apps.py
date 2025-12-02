from django.apps import AppConfig


class RaffleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'raffle'
    
    def ready(self):
        """Conectar signals cuando la app esté lista"""
        import raffle.signals  # Esto registra los signals automáticamente
