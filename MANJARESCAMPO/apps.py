from django.apps import AppConfig

class ManjarescampoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'MANJARESCAMPO'
    
    def ready(self):
        # Cargar datos de prueba al iniciar
        try:
            from .mock_data import load_mock_data
            load_mock_data()
        except Exception as e:
            pass  # Silenciar errores si la BD no está lista