from django.http import HttpResponse
from telegram import Update
from telegram.ext import Application

# Инициализация приложения PTB
application = Application.builder().token("8083943011:AAEYzROqso2wqBWNIttlZ5To4bkKHzrduNg").build()

async def telegram_webhook(request):
    # Получаем данные из запроса
    data = await request.json()
    
    # Создаем объект Update
    update = Update.de_json(data, application.bot)
    
    # Обрабатываем обновление
    await application.update_queue.put(update)
    
    # Возвращаем HttpResponse
    return HttpResponse("Webhook received")