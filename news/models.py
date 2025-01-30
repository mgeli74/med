from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import telegram
from django.db.models.signals import post_save
from django.dispatch import receiver

class NewsCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    fulltext = models.TextField()
    data = models.DateTimeField(default=timezone.now)  # Установка текущей даты по умолчанию
    image = models.ImageField(upload_to='news_image')
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

class Comment(models.Model):
    news = models.ForeignKey('News', related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Используем AUTH_USER_MODEL
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} - {self.created_date}'
        
class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    news = models.ForeignKey('News', related_name='votes', on_delete=models.CASCADE)
    value = models.IntegerField(choices=[(1, 'Like'), (-1, 'Dislike')])  # 1 - Like, -1 - Dislike

    class Meta:
        unique_together = ('user', 'news')  # Один пользователь может голосовать за новость только один раз

    def __str__(self):
        return f'{self.user.username} - {self.news.name} - {self.value}'

# Функция для отправки сообщения в Telegram
def send_telegram_message(message):
    bot_token = '8083943011:AAEYzROqso2wqBWNIttlZ5To4bkKHzrduNg'
    chat_id = '-1002495838318'  # ID чата, куда будут отправляться сообщения
    bot = telegram.Bot(token=bot_token)
    bot.send_message(chat_id=chat_id, text=message)

# Сигнал для отправки сообщения в Telegram при создании новой новости
@receiver(post_save, sender=News)
def news_created(sender, instance, created, **kwargs):
    if created:
        message = f"Новая новость:\n\n{instance.title}\n\n{instance.content}"
        send_telegram_message(message)
