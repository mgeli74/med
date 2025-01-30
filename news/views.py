from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import title
from .forms import CommentForm
from django.views.decorators.csrf import csrf_exempt
from news.models import NewsCategory, News, Comment, Vote
from django.core.paginator import Paginator
from django.http import JsonResponse




def allnews(request):
    context = {
        'title': 'Новости и события'
    }
    return render(request, 'news/post.html', context)


def events(request, category_id=None, page_number=1):
    per_page = 6
    events = News.objects.filter(
        category_id=category_id) if category_id else News.objects.all()
    paginator = Paginator(events, per_page)
    events_paginator = paginator.page(page_number)

    context = {
        'title': 'События',
        'newscategories': NewsCategory.objects.all(),
        'events': events_paginator,

    }
    return render(request, 'news/events.html', context)


def post(request, post_id=None):
    news = get_object_or_404(News, id=post_id)
    comments = news.comments.all()
    form = CommentForm()
    likes = news.votes.filter(value=1).count()
    dislikes = news.votes.filter(value=-1).count()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.news = news
            comment.author = request.user
            comment.save()
            return redirect('news:post', post_id=post_id)

    context = {
        'title': events,
        'news': news,
        'post': post,
        'events': News.objects.all(),
        'comments': comments,
        'form': form,
        'likes': likes,
        'dislikes': dislikes,
    }
    return render(request, 'news/news.html', context)


def item(request, item_id=None):
    if item_id:
        news = News.objects.all(id=item_id)
        item = News.objects.filter(category=item)
    else:
        item = News.objects.all()

    context = {
        'title': title,
    }
    return render(request, 'news/news.html', context)



def vote(request, news_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged in to vote.'}, status=403)

    news = get_object_or_404(News, id=news_id)
    value = request.POST.get('value')

    if value is None:
        return JsonResponse({'error': 'Value is required.'}, status=400)

    value = int(value)  # 1 - Like, -1 - Dislike

    # Проверяем, голосовал ли пользователь уже за эту новость
    vote, created = Vote.objects.get_or_create(
        user=request.user, news=news, defaults={'value': value}
    )

    if not created:
        if vote.value == value:
            # Если пользователь повторно голосует тем же значением, удаляем голос
            vote.delete()
        else:
            # Если пользователь меняет голос, обновляем значение
            vote.value = value
            vote.save()

    # Возвращаем общее количество лайков и дизлайков
    likes = news.votes.filter(value=1).count()
    dislikes = news.votes.filter(value=-1).count()

    return JsonResponse({
        'likes': likes,
        'dislikes': dislikes,
    })
