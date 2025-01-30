from store.views import index, store, basket_add, basket_remove, contact
from django.contrib import admin
from django.urls import path, include
from news.views import allnews, events, vote
from django.conf.urls.static import static
from django.conf import settings
from posts import views
from news import views


urlpatterns = [
    path('', index, name='index'),
    path('contact/', contact, name='contact'),
    path('gallery/', include('posts.urls')),
    path('admin/', admin.site.urls),
    path('store/', include('store.urls', namespace='store')),
    path('events/', include('news.urls', namespace='news')),
    path('users/', include('users.urls', namespace='users')),
    path('weather/', include('weather.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)