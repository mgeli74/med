import requests
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from store.models import DeliveryRequest
import logging
from retrying import retry
from decouple import config

logger = logging.getLogger(__name__)

@retry(stop_max_attempt_number=3, wait_fixed=2000)
def send_telegram_message(url, payload):
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        logger.info(f"Сообщение успешно отправлено: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")

# Сохраняем старое значение статуса перед сохранением
@receiver(pre_save, sender=DeliveryRequest)
def save_old_status(sender, instance, **kwargs):
    if not instance.pk:
        instance._old_status = None
    else:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except sender.DoesNotExist:
            instance._old_status = None

@receiver(post_save, sender=DeliveryRequest)
def delivery_request_created(sender, instance, created, **kwargs):
    bot_token = config('TELEGRAM_BOT_TOKEN')
    chat_id = config('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    logger.debug(f"Bot Token: {bot_token}")
    logger.debug(f"Chat ID: {chat_id}")

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
            logger.debug("Статус не изменился, уведомление не отправлено.")
            return

        message = (
            f"*Изменен статус заказа {instance.id}:*\n\n"
            f"👤 *Пользователь:* {instance.user.username}\n"
            f"📦 *Продукт:* {instance.product.name}\n"
            f"🔢 *Количество:* {instance.quantity}\n"
            f"🏠 *Адрес:* {instance.address}\n"
            f"📊 *Старый статус:* {old_status}\n"
            f"📊 *Новый статус:* {instance.status}"
        )

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    send_telegram_message(url, payload)