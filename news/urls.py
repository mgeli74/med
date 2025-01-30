from django.urls import path
from . import views
from news.views import allnews, events, post, vote

app_name = 'news'

urlpatterns = [
    path('', events, name='events'),
    path('category/<int:category_id>/', events, name='newscategory'),
    path('page/<int:page_number>/', events, name='paginator'),
    path('news/<int:post_id>/', post, name='post'),
    path('news/<int:news_id>/vote/', vote, name='vote'),
]
