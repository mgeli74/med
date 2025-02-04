from django.contrib import admin
from .models import DeliveryRequest
from store.models import ProductCategory, Product, Basket, ProductImage
from .forms import DeliveryRequestStatusForm
from decouple import config
from telegram_bot.utils import send_to_telegram_channel

admin.site.register(ProductCategory)

class ProductImageInline(admin.TabularInline):  # или admin.StackedInline
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('name', 'price', 'quantity', 'category')
    fields = (('name', 'category'), 'description', ('price', 'quantity'), 'image')
    search_fields = ('name',)
    ordering = ('name',)

class BasketAdmin(admin.TabularInline):
    model = Basket
    fields = ('product', 'quantity', 'created_timestamp')
    extra = 1
    readonly_fields = ('created_timestamp',)

class DeliveryRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'address', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'product__name')
    form = DeliveryRequestStatusForm

    # Добавляем действия для массового изменения статуса
    actions = ['make_in_processing', 'make_in_transit', 'make_delivered']

    def make_in_processing(self, request, queryset):
        queryset.update(status='В обработке')
    make_in_processing.short_description = "Изменить статус на 'В обработке'"

    def make_in_transit(self, request, queryset):
        queryset.update(status='В пути')
    make_in_transit.short_description = "Изменить статус на 'В пути'"

    def make_delivered(self, request, queryset):
        queryset.update(status='Доставлено')
    make_delivered.short_description = "Изменить статус на 'Доставлено'"

    def save_model(self, request, obj, form, change):
        if change:  # Если это изменение существующего объекта
            old_obj = DeliveryRequest.objects.get(pk=obj.pk)
            if old_obj.status != obj.status:  # Если статус изменился
                bot_token = config('TELEGRAM_BOT_TOKEN')
                chat_id = config('TELEGRAM_CHAT_ID')
                message = (
                    f"*Изменен статус заказа {obj.id}:*\n\n"
                    f"👤 *Пользователь:* {obj.user.username}\n"
                    f"📦 *Продукт:* {obj.product.name}\n"
                    f"🔢 *Количество:* {obj.quantity}\n"
                    f"🏠 *Адрес:* {obj.address}\n"
                    f"📊 *Старый статус:* {old_obj.status}\n"
                    f"📊 *Новый статус:* {obj.status}"
                )
                send_to_telegram_channel(message, chat_id, bot_token)
        super().save_model(request, obj, form, change)

admin.site.register(DeliveryRequest, DeliveryRequestAdmin)