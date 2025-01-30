from django.apps import AppConfig

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_bot'

class NewsConfig(AppConfig):
    name = 'news'

    def ready(self):
        import news.signals  # Импортируем сигналы