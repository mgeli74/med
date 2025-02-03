from users.models import User
from django.shortcuts import render, HttpResponseRedirect, redirect
from store.models import ProductCategory, Product, Basket, DeliveryRequest
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from store.forms import DeliveryRequestForm, DeliveryRequestStatusForm
from weather.views import get_weather_data
from users.views import profile
from django.urls import reverse
import requests
from django.conf import settings
from django.contrib import messages
from django.utils import timezone, url_has_allowed_host_and_scheme
from django.db.models import Sum, F





def get_weather_data(city):
    api_key = settings.OPENWEATHERMAP_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()

def get_wind_direction(degrees):
    """Преобразует градусы в направление ветра (северный, южный и т.д.)"""
    directions = ["северный", "северо-восточный", "восточный", "юго-восточный",
                  "южный", "юго-западный", "западный", "северо-западный"]
    index = round(degrees / 45) % 8
    return directions[index]

def translate_precipitation(description):
    """Переводит описание погоды на русский язык"""
    translations = {
        "clear sky": "ясно",
        "few clouds": "небольшая облачность",
        "scattered clouds": "рассеянные облака",
        "broken clouds": "облачно с прояснениями",
        "overcast clouds": "пасмурно",
        "light rain": "лёгкий дождь",
        "moderate rain": "умеренный дождь",
        "heavy rain": "сильный дождь",
        "thunderstorm": "гроза",
        "snow": "снег",
        "mist": "туман",
    }
    return translations.get(description, description)
    
def index(request):
    city = 'Chelyabinsk'  # Пример города
    weather_data = get_weather_data(city)

    if weather_data.get('cod') == 200:
        weather_info = {
            'city': weather_data['name'],
            'temperature': weather_data['main']['temp'],
            'wind_speed': weather_data['wind']['speed'],
            'wind_direction': weather_data['wind']['deg'],
            'humidity': weather_data['main']['humidity'],
            'pressure': weather_data['main']['pressure'],
            'precipitation': weather_data['weather'][0]['description'],
            'icon': weather_data['weather'][0]['icon'],
        }
    else:
        weather_info = None

    return render(request, 'store/index.html', {'weather_info': weather_info})


def store(request, category_id=None, page_number=1):
    per_page = 6
    products = Product.objects.filter(category_id=category_id) if category_id else Product.objects.all()
    paginator = Paginator(products, per_page)
    products_paginator = paginator.page(page_number)
    context = {
        'title': 'Каталог',
        'categories': ProductCategory.objects.all(),
        'products': products_paginator
    }
    return render(request, 'store/products.html', context)

@login_required
def basket_add(request, product_id):
    product = Product.objects.get(id=product_id)
    baskets = Basket.objects.filter(user=request.user, product=product)

    if not baskets.exists():
        Basket.objects.create(user=request.user, product=product, quantity=1)
    else:
        basket = baskets.first()
        basket.quantity += 1
        basket.save()

    return redirect(reverse('store:index')) 



@login_required
def basket_remove(request, basket_id):
    basket = Basket.objects.get(id=basket_id)
    basket.delete()
    referer = request.META.get('HTTP_REFERER', '/')
    if url_has_allowed_host_and_scheme(referer, allowed_hosts=None):
        return HttpResponseRedirect(referer)
    else:
        return redirect('/')

def contact(request):
    context = {
        'title': 'Медоеды Team'
    }
    return render(request, 'store/contact.html', context)
    
    
@staticmethod
def total_sum(user):
	return Basket.objects.filter(user=user).aggregate(total_sum=Sum(F('quantity') * F('product__price')))['total_sum'] or 0

@staticmethod
def total_quantity(user):
	return Basket.objects.filter(user=user).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0	


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Используем get_object_or_404 для безопасности
    return render(request, 'store/item.html', {'product': product})
    
    
@login_required
def basket_view(request):
    baskets = Basket.objects.filter(user=request.user)
    total_sum = baskets.total_sum()
    total_quantity = baskets.total_quantity()

    if request.method == 'POST':
        # Обработка изменения количества товара
        for basket in baskets:
            new_quantity = request.POST.get(f'quantity_{basket.id}')
            if new_quantity and new_quantity.isdigit():
                new_quantity = int(new_quantity)
                if new_quantity > 0:
                    basket.quantity = new_quantity
                    basket.save()
                else:
                    basket.delete()  # Удалить товар, если количество равно 0
        return redirect('store:basket')  # Перенаправляем на ту же страницу после обновления

    context = {
        'baskets': baskets,
        'total_sum': total_sum,
        'total_quantity': total_quantity,
        'title': 'Корзина'
    }
    return render(request, 'store/basket.html', context)
@login_required
def basket_update(request, basket_id, action):
    basket = Basket.objects.get(id=basket_id)
    
    if action == 'increase':
        basket.quantity += 1
    elif action == 'decrease':
        if basket.quantity > 1:
            basket.quantity -= 1
        else:
            basket.delete()
            return redirect(reverse('store:basket'))  # или другой URL
    elif action == 'remove':
        basket.delete()
        return redirect(reverse('store:basket'))  # или другой URL
    
    basket.save()
    return redirect(reverse('store:basket'))

@login_required
def checkout(request):
    baskets = Basket.objects.filter(user=request.user)
    total_sum = baskets.total_sum()
    total_quantity = baskets.total_quantity()
    
    context = {
        'baskets': baskets,
        'total_sum': total_sum,
        'total_quantity': total_quantity,
        'title': 'Оформление заказа'
    }
    return render(request, 'store/checkout.html', context)
    
@login_required
def edit_order(request):
    baskets = Basket.objects.filter(user=request.user)
    total_sum = baskets.total_sum()
    total_quantity = baskets.total_quantity()

    if request.method == 'POST':
        # Обработка изменения количества товара
        for basket in baskets:
            new_quantity = request.POST.get(f'quantity_{basket.id}')
            if new_quantity and new_quantity.isdigit():
                new_quantity = int(new_quantity)
                if new_quantity > 0:
                    basket.quantity = new_quantity
                    basket.save()
                else:
                    basket.delete()  # Удалить товар, если количество равно 0
        return redirect('edit_order')  # Перенаправляем на ту же страницу после обновления

    context = {
        'baskets': baskets,
        'total_sum': total_sum,
        'total_quantity': total_quantity,
        'title': 'Изменение заказа'
    }
    return render(request, 'store/basket.html', context)

@login_required
def basket_clear(request):
    """Удаляет все товары из корзины текущего пользователя"""
    Basket.objects.filter(user=request.user).delete()
    return redirect('store:basket')  # Перенаправляем пользователя обратно в корзину
    
@login_required
def create_delivery_request(request):
    if request.method == 'POST':
        form = DeliveryRequestForm(request.POST)
        if form.is_valid():
            delivery_request = form.save(commit=False)
            delivery_request.user = request.user
            delivery_request.save()
            
            # Уменьшение количества товаров на складе
            product = delivery_request.product
            if product.quantity >= delivery_request.quantity:
                product.quantity -= delivery_request.quantity
                product.save()
                # Очистка корзины после создания заявки
                Basket.objects.filter(user=request.user, product=delivery_request.product).delete()
                # Добавление сообщения об успешном заказе
                messages.success(request, 'Ваш заказ успешно оформлен! Спасибо за покупку!')
            else:
                messages.error(request, 'Недостаточно товара на складе для выполнения заказа.')
                delivery_request.delete()
                return redirect('store:basket')
            
            return redirect('users:profile')
    else:
        baskets = Basket.objects.filter(user=request.user)
        if baskets.exists():
            basket = baskets.first()
            form = DeliveryRequestForm(initial={
                'product': basket.product,
                'quantity': basket.quantity
            })
        else:
            return redirect('store:basket')
    
    context = {
        'form': form,
        'title': 'Создание заявки на доставку'
    }
    return render(request, 'store/create_delivery_request.html', context)



@login_required
def orders(request):
    status_filter = request.GET.get('status', '')
    user_orders = DeliveryRequest.objects.filter(user=request.user)
    if status_filter:
        user_orders = user_orders.filter(status=status_filter)
    paginator = Paginator(user_orders, 5)  # 5 заказов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': 'Мои заказы'
    }
    return render(request, 'store/delivery.html', context)


    
# Функция для проверки, является ли пользователь модератором
def is_moderator(user):
    return user.is_staff  # или любое другое условие, определяющее модераторов
    
@login_required
@user_passes_test(is_moderator)
def update_delivery_request_status(request, pk):
    delivery_request = get_object_or_404(DeliveryRequest, pk=pk)
    
    if request.method == 'POST':
        form = DeliveryRequestStatusForm(request.POST, instance=delivery_request)
        if form.is_valid():
            form.save()
            return redirect('store:orders')
    else:
        form = DeliveryRequestStatusForm(instance=delivery_request)
    
    context = {
        'form': form,
        'delivery_request': delivery_request,
    }
    return render(request, 'store/update_delivery_request_status.html', context)



