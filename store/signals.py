import requests
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from store.models import DeliveryRequest
import logging
from retrying import retry

logger = logging.getLogger(__name__)

@retry(stop_max_attempt_number=3, wait_fixed=2000)
def send_telegram_message(url, payload):
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        raise Exception(f"Ошибка при отправке сообщения: {response.text}")

# Сохраняем старое значение статуса перед сохранением
@receiver(pre_save, sender=DeliveryRequest)
def save_old_status(sender, instance, **kwargs):
    if not instance.pk:  # Если объект создается впервые
        instance._old_status = None
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        instance._old_status = old_instance.status
    except sender.DoesNotExist:
        instance._old_status = None

@receiver(post_save, sender=DeliveryRequest)
def delivery_request_created(sender, instance, created, **kwargs):
    bot_token = 'TELEGRAM_BOT_TOKEN'
    chat_id = '-1002495838318'  # ID чата
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    if created:
        message = (
            f"*Новая заявка на доставку:*\n\n"
            f"👤 *Пользователь:* {instance.user.username}\n"
            f"📦 *Продукт:* {instance.product.name}\n"
            f"🔢 *Количество:* {instance.quantity}\n"
            f"🏠 *Адрес:* {instance.address}\n"
            f"📊 *Статус:* {instance.status}"
        )
    else:
        old_status = getattr(instance, '_old_status', None)
        if old_status is None or old_status == instance.status:
            return  # Если статус не изменился, ничего не делаем

        message = (
            f"*Изменен статус заказа {instance.id}:*\n\n"
            f"👤 *Пользователь:* {instance.user.username}\n"
            f"📦 *Продукт:* {instance.product.name}\n"
            f"🔢 *Количество:* {instance.quantity}\n"
            f"🏠 *Адрес:* {instance.address}\n"
            f"📊 *Старый статус:* {old_status}\n"
            f"📊 *Новый статус:* {instance.status}"
        )

    if not created and instance.status == 'Доставлено':
        instance.update_stock_and_clear_basket()

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        logger.debug(f"Отправка сообщения в Telegram: {payload}")
        send_telegram_message(url, payload)
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в Telegram: {e}")
