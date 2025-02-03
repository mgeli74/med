import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime
import requests
from .utils import send_to_telegram_channel  # Исправленный импорт
# Настройки подключения к MySQL (из Django)
MYSQL_CONFIG = {
    'host': 'localhost',          # Хост
    'user': 'cm72283_medoed',     # Пользователь
    'password': 'ujif1994',       # Пароль
    'database': 'cm72283_medoed', # База данных
    'port': 3306                  # Порт
}

# Функция для форматирования данных в HTML
def format_message_html(data):
    id_, title, description, specs, created_at, image_path, updated_at, author_id = data

    # Форматируем даты
    created_at_str = created_at.strftime("%d.%m.%Y %H:%M:%S")
    updated_at_str = updated_at.strftime("%d.%m.%Y %H:%M:%S")

    # Форматируем сообщение
    message = (
        f"<b>{title}</b>\n\n"  # Заголовок (жирный)
        f"<i>{description}</i>\n\n"  # Описание (курсив)
        f"<b>Технические характеристики:</b>\n{specs}\n\n"  # ТТХ
        f"<b>Дата создания:</b> {created_at_str}\n"  # Дата создания
        f"<b>Дата обновления:</b> {updated_at_str}\n"  # Дата обновления
        f"<b>ID автора:</b> {author_id}"  # ID автора
    )
    return message

# Пример использования
send_to_telegram_channel("Привет, это тестовое сообщение от бота!")


# Команда /getdata для получения данных из MySQL и отправки в Telegram
async def get_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Подключаемся к MySQL
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()

        # Выполняем SQL-запрос
        query = "SELECT * FROM news_news LIMIT 10"  # Замените news_news на имя вашей таблицы
        cursor.execute(query)
        results = cursor.fetchall()

        # Формируем сообщение с данными
        for row in results:
            formatted_message = format_message_html(row)  # Форматируем каждую строку
            await update.message.reply_text(formatted_message, parse_mode="HTML")  # Отправляем сообщение

        # Закрываем соединение с MySQL
        cursor.close()
        connection.close()

    except mysql.connector.Error as e:
        await update.message.reply_text(f"Ошибка MySQL: {e}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# Настройка бота
application = Application.builder().token("8083943011:AAEYzROqso2wqBWNIttlZ5To4bkKHzrduNg").build()

# Регистрация команды /getdata
application.add_handler(CommandHandler("getdata", get_data))

# Запуск бота
application.run_polling()



