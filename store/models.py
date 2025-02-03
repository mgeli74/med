from django.db import models
from django.db import models
from django.contrib.auth.models import User
from store.models import Product

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Отзыв от {self.user.username} на {self.product.name}'
from users.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import telegram
import logging

logger = logging.getLogger(__name__)

class ProductCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products_images', blank=True)  # Основное изображение
    category = models.ForeignKey(to=ProductCategory, on_delete=models.PROTECT)

    def __str__(self):
        return f'Товар: {self.name} | Категория: {self.category.name}'

class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products_images/')

    def __str__(self):
        return f'Изображение для {self.product.name}'

class BasketQuerySet(models.QuerySet):
    def total_sum(self):
        return sum(basket.sum() for basket in self)

    def total_quantity(self):
        return sum(basket.quantity for basket in self)

class Basket(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    created_timestamp = models.DateTimeField(auto_now_add=True)

    objects = BasketQuerySet.as_manager()

    def __str__(self):
        return f'Корзина для {self.user.username} | Продукт: {self.product.name}'

    def sum(self):
        return self.product.price * self.quantity

class DeliveryRequest(models.Model):
    STATUS_CHOICES = [
        ('В обработке', 'В обработке'),
        ('В пути', 'В пути'),
        ('Доставлено', 'Доставлено'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='В обработке')

    def __str__(self):
        return f"Заказ {self.id} для {self.user.username}"

    def save(self, *args, **kwargs):
        # Отслеживание изменения статуса
        old_status = None
        if self.pk:
            old_instance = DeliveryRequest.objects.get(pk=self.pk)
            old_status = old_instance.status

        super().save(*args, **kwargs)

        # Логирование изменений статуса (не через сигнал)
        if old_status != self.status:
            logger.info(f"Статус заказа {self.id} изменен с {old_status} на {self.status}")

        # Уменьшение количества товаров на складе и удаление из корзины после успешного заказа
        if self.status == 'Доставлено':
            self.update_stock_and_clear_basket()

    def update_stock_and_clear_basket(self):
        # Уменьшение количества товаров на складе
        self.product.quantity -= self.quantity
        self.product.save()

        # Удаление продуктов из корзины пользователя
        Basket.objects.filter(user=self.user, product=self.product).delete()

