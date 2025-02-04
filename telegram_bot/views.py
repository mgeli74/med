from django.http import HttpResponse
from telegram import Update
from telegram.ext import Application
import os

# Инициализация приложения PTB с использованием переменной окружения
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
application = Application.builder().token(telegram_bot_token).build()

async def telegram_webhook(request):
    # Получаем данные из запроса
    data = await request.json()
    
    # Создаем объект Update
    update = Update.de_json(data, application.bot)
    
    # Обрабатываем обновление
    await application.update_queue.put(update)
    
    # Возвращаем HttpResponse
    return HttpResponse("Webhook received")