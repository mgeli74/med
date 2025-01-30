from django.core.management.base import BaseCommand
from telegram_bot.bot import setup_bot
import threading

class Command(BaseCommand):
    help = 'Запускает Telegram-бота'

    def handle(self, *args, **kwargs):
        self.stdout.write("Запуск Telegram-бота...")
        bot_thread = threading.Thread(target=setup_bot)
        bot_thread.daemon = True
        bot_thread.start()
        self.stdout.write("Telegram-бот запущен.")