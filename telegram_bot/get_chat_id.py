import requests

def get_chat_id():
    # Токен вашего бота
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # URL API Telegram для получения обновлений
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    
    # Отправка GET-запроса
    response = requests.get(url)
    updates = response.json()
    
    # Извлекаем chat_id из первого обновления
    if updates["ok"] and updates["result"]:
        chat_id = updates["result"][0]["message"]["chat"]["id"]
        return chat_id
    else:
        return "Нет обновлений. Отправьте боту сообщение."

# Вызов функции и вывод результата
print(get_chat_id())