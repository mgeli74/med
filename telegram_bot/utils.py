# telegram_bot/utils.py
import requests

def send_to_telegram_channel(message, chat_id, bot_token):
    """
    Отправляет сообщение в Telegram-канал.
    
    :param message: Текст сообщения.
    :param chat_id: ID чата или канала.
    :param bot_token: Токен вашего бота.
    :return: Ответ от Telegram API.
    """
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'  # Поддержка HTML-разметки
    }
    response = requests.post(url, data=payload)
    return response.json()
    
    