from telegram import Update
from telegram.ext import CallbackContext

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Я твой бот. Как дела?")

def echo(update: Update, context: CallbackContext):
    user_message = update.message.text
    update.message.reply_text(f"Вы сказали: {user_message}")