     
import requests

def send_to_telegram_channel(message, chat_id, bot_token):
	url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
	payload = {
		"chat_id": chat_id,
		"text": message,
		"parse_mode": "HTML"  # Для поддержки HTML-форматирования
	}
	response = requests.post(url, data=payload)
	if response.status_code != 200:
		print(f"Ошибка при отправке сообщения: {response.text}")