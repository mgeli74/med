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
    logger.debug(f"URL: {url}")
    logger.debug(f"Payload: {payload}")
    response = requests.post(url, data=payload)
    logger.debug(f"Response: {response.status_code} - {response.text}")
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
        logger.debug(f"Old Status: {old_status}")
        logger.debug(f"New Status: {instance.status}")
        if old_status is None or old_status == instance.status:
            logger.debug("Статус не изменился, уведомление не отправлено.")
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