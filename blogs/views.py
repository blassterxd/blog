from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BlogPostForm
from .models import BlogPost


def index(request):
    """Главная страница: все публикации, новые первыми."""
    posts = BlogPost.objects.select_related('owner').order_by('-date_added')
    return render(request, 'blogs/index.html', {'posts': posts})


@login_required
def post_create(request):
    """Создание публикации: автор назначается здесь, а не в форме."""
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.owner = request.user
            post.save()
            messages.success(request, 'Публикация создана.')
            return redirect('blogs:index')
    else:
        form = BlogPostForm()
    context = {
        'form': form,
        'title': 'Новая публикация',
        'button': 'Опубликовать',
    }
    return render(request, 'blogs/post_form.html', context)


@login_required
def post_edit(request, post_id):
    """Редактирование: запись берётся только вместе с проверкой автора."""
    post = get_object_or_404(BlogPost, id=post_id, owner=request.user)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Изменения сохранены.')
            return redirect('blogs:index')
    else:
        form = BlogPostForm(instance=post)
    context = {
        'form': form,
        'title': 'Редактирование публикации',
        'button': 'Сохранить',
    }
    return render(request, 'blogs/post_form.html', context)