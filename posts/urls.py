from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from posts import views
from posts.views import blog_view, detail_view, category_list, category_detail

urlpatterns = [
    path('post/<int:post_id>/', blog_view, name='post'),
    path('', blog_view, name='gallery'),
    path('', views.blog_view, name='blog'),
    path('<int:id>/', views.detail_view, name='detail'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<str:category>/', views.category_detail, name='category_detail'),
]