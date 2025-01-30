import telebot
from telebot import types
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Инициализация бота
bot = telebot.TeleBot('8083943011:AAEYzROqso2wqBWNIttlZ5To4bkKHzrduNg')



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
        
        
        
# Функция для создания Inline-кнопки
def create_inline_button(text, url):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text=text, url=url)
    markup.add(button)
    return markup

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def main(message):
    try:
        # Создаем Reply-клавиатуру
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Открыть сайт')
        button2 = types.KeyboardButton('Магазин')
        button3 = types.KeyboardButton('Новости')
        markup.row(button1)
        markup.row(button2, button3)

        # Отправляем сообщение с клавиатурой
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Выберите действие:', reply_markup=markup)
    except Exception as e:
        logger.error(f"Ошибка в обработчике /start: {e}")

# Обработчик команды /site или /website
@bot.message_handler(commands=['site', 'website'])
def site(message):
    try:
        markup = create_inline_button("Открыть сайт", 'https://медоеды.рф')
        bot.send_message(message.chat.id, "Нажмите кнопку, чтобы открыть сайт:", reply_markup=markup)
    except Exception as e:
        logger.error(f"Ошибка в обработчике /site: {e}")

# Обработчик текстовых сообщений
@bot.message_handler()
def info(message):
    try:
        if message.text.lower() == 'привет':
            bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!')
        elif message.text.lower() == 'id':
            bot.reply_to(message, f'ID: {message.from_user.id}')
        elif message.text.lower() == 'открыть сайт':
            markup = create_inline_button("Открыть сайт", 'https://медоеды.рф')
            bot.send_message(message.chat.id, "Нажмите кнопку, чтобы открыть сайт:", reply_markup=markup)
        elif message.text.lower() == 'магазин':
            markup = create_inline_button("Перейти в магазин", 'https://медоеды.рф/store/')
            bot.send_message(message.chat.id, "Нажмите кнопку, чтобы перейти в магазин:", reply_markup=markup)
        elif message.text.lower() == 'новости':
            markup = create_inline_button("Читать новости", 'https://медоеды.рф/events')
            bot.send_message(message.chat.id, "Нажмите кнопку, чтобы читать новости:", reply_markup=markup)
    except Exception as e:
        logger.error(f"Ошибка в обработчике текстовых сообщений: {e}")

# Запуск бота
if __name__ == '__main__':
    logger.info("Бот запущен")
    bot.polling(none_stop=True)