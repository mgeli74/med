from django.contrib import admin

from news.models import NewsCategory, News, Post, Comment

admin.site.register(NewsCategory)
admin.site.register(News)
admin.site.register(Post)
admin.site.register(Comment)
