from django.shortcuts import render

from django.shortcuts import render, get_object_or_404

from .models import Post, PostImage

def blog_view(request):
    posts = Post.objects.all()
    categories = Post.objects.values_list('category', flat=True).distinct()
    return render(request, 'posts/blog.html', {
        'posts': posts,
        'categories': categories,
    })
         
    

def detail_view(request, id):
    post = get_object_or_404(Post, id=id)
    photos = PostImage.objects.filter(post=post)
    return render(request, 'posts/detail.html', {
        'post':post,
        'photos':photos,
    })

def category_list(request):
    categories = Post.objects.values_list('category', flat=True).distinct()
    return render(request, 'posts/category_list.html', {'categories': categories})

def category_detail(request, category):
    posts = Post.objects.filter(category=category)
    return render(request, 'posts/category_detail.html', {'posts': posts, 'category': category})
