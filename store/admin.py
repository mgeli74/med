from django.contrib import admin
from .models import DeliveryRequest
from store.models import ProductCategory, Product, Basket, ProductImage
from .forms import DeliveryRequestStatusForm

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

admin.site.register(DeliveryRequest, DeliveryRequestAdmin)   
