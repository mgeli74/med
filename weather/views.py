import requests
from django.shortcuts import render
from django.conf import settings


def get_weather_data(city):
    api_key = settings.OPENWEATHERMAP_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()


def weather_detail(request, city):
    weather_data = get_weather_data(city)

    if weather_data.get('cod') != 200:
        return render(request, 'weather/error.html', {'message': 'Город не найден'})

    context = {
        'city': weather_data['name'],
        'temperature': weather_data['main']['temp'],
        'precipitation': weather_data['weather'][0]['description'],
        'wind_direction': weather_data['wind']['deg'],
        'icon': weather_data['weather'][0]['icon'],
    }
    return render(request, 'weather/weather_detail.html', context)


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


def weather_index(request):
    cities = ['Челябинск', 'Аргаяш', 'Kutaisi']  # Пример списка городов
    weather_list = []

    for city in cities:
        weather_data = get_weather_data(city)
        if weather_data.get('cod') == 200:
            weather_list.append({
                'city': weather_data['name'],
                'temperature': weather_data['main']['temp'],
                'wind_speed': weather_data['wind']['speed'],
                'wind_direction': get_wind_direction(weather_data['wind']['deg']),  # Направление ветра словами
                'humidity': weather_data['main']['humidity'],
                'pressure': weather_data['main']['pressure'],
                'precipitation': translate_precipitation(weather_data['weather'][0]['description']),  # Перевод описания
                'icon': weather_data['weather'][0]['icon'],
            })

    # Определяем, какой шаблон использовать
    if request.path == '/weather/':
        template_name = 'weather/index.html'
    else:
        template_name = 'store/index.html'

    return render(request, template_name, {'weather_list': weather_list})