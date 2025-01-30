
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import News
import telegram
import requests

def send_telegram_message(message):
    bot_token = '8083943011:AAEYzROqso2wqBWNIttlZ5To4bkKHzrduNg'
    chat_id = '-1002495838318'  # ID чата, куда будут отправляться сообщения
    bot = telegram.Bot(token=bot_token)
    bot.send_message(chat_id=chat_id, text=message)

@receiver(post_save, sender=News)
def news_created(sender, instance, created, **kwargs):
    if created:
        message = f"Новая новость: {instance.title}\n\n{instance.content[:100]}...\n\nЧитай полностью: https://медоеды.рф/events/news/{instance.id}/"
        send_telegram_message(message)        

@receiver(post_save, sender=News)
def notify_telegram_channel(sender, instance, created, **kwargs):
    if created:
        bot_token = '8083943011:AAEYzROqso2wqBWNIttlZ5To4bkKHzrduNg'
        chat_id = '-1002495838318'  # Замените на username вашего канала или группы
        message = f"Новая новость: {instance.title}\n\n{instance.content[:100]}...\n\nЧитать полностью: https://медоеды.рф/events/news/{instance.id}/"
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"Ошибка при отправке сообщения: {response.text}")

