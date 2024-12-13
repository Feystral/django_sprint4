from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import Http404, HttpResponse

from .models import Category, Post, Comment
from .forms import PostForm, CommentForm


def error_404_or_object(request, model, *args, **kwargs):
    try:
        obj = get_object_or_404(model, *args, **kwargs)
        return obj
    except Http404:
        return render(request, 'pages/404.html', status=404)


def get_filtered_posts(manager):
    return manager.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).select_related('author', 'location', 'category')


def index(request):
    posts = Post.objects.filter(pub_date__lte=timezone.now(),
                                category__is_published=True,
                                is_published=True)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    post = error_404_or_object(request, Post, id=post_id)
    if isinstance(post, HttpResponse):
        return post

    if post.pub_date > timezone.now() and post.author != request.user:
        return render(request, 'pages/404.html', status=404)

    if not post.category.is_published and post.author != request.user:
        return render(request, 'pages/404.html', status=404)

    if not post.is_published and post.author != request.user:
        return render(request, 'pages/404.html', status=404)

    comments = post.comments.all().order_by('created_at')

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect('blog:post_detail', post_id=post.id)
        else:
            form = CommentForm()
    else:
        form = CommentForm()

    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'user': request.user,
    })


def category_posts(request, category_slug):
    category = error_404_or_object(request, Category, slug=category_slug,
                                   is_published=True)

    if isinstance(category, HttpResponse):
        return category

    try:
        posts = (category.posts.filter(is_published=True,
                                       pub_date__lte=timezone.now())
                 .select_related('author',
                                 'category').prefetch_related('comments'))
    except Http404:
        return render(request, 'pages/404.html', status=404)

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj,
    })


def profile(request, username):
    user = error_404_or_object(request, User, username=username)
    if isinstance(user, HttpResponse):
        return user

    posts = Post.objects.filter(author=user)
    is_owner = request.user.is_authenticated and request.user == user
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': user,
        'posts': posts,
        'is_owner': is_owner,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    if request.user.username != request.user.username:
        return redirect('blog:profile', username=request.user.username)

    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = UserChangeForm(instance=request.user)

    return render(request, 'blog/user.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'blog/password_change_form.html', {'form': form})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = error_404_or_object(request, Post, id=post_id)
    if isinstance(post, HttpResponse):
        return post
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post.id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form, 'is_edit': True})


@login_required
def delete_post(request, post_id):
    """
    Удаление поста, если он существует и принадлежит текущему пользователю.
    """
    post = error_404_or_object(request, Post, id=post_id)
    if isinstance(post, HttpResponse):
        return post
    if post.author != request.user:
        raise Http404("Пост не найден")

    if request.method == "POST":
        post.delete()
        return redirect('blog:index')

    return render(request, 'blog/create.html', {'post': post})


@login_required
def delete_comment(request, post_id, comment_id):
    """
    Удаление комментария, если он принадлежит текущему пользователю.
    """
    comment = error_404_or_object(request, Comment, id=comment_id)
    if isinstance(comment, HttpResponse):
        return comment

    if comment.author != request.user:
        raise Http404("Комментарий не найден")

    if request.method == "POST":
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', {
        'comment': comment,
        'delete': True,
    })


@login_required
def add_comment(request, post_id):
    post = error_404_or_object(request, Post, id=post_id)
    if isinstance(post, HttpResponse):
        return post

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm()

    return render(request, 'blog/detail.html', {'post': post, 'form': form})


@login_required
def edit_comment(request, post_id, comment_id):
    post = error_404_or_object(request, Post, id=post_id)
    if isinstance(post, HttpResponse):
        return post
    comment = error_404_or_object(request, Comment,
                                  id=comment_id, post_id=post_id)
    if isinstance(comment, HttpResponse):
        return comment
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/comment.html', {
        'form': form,
        'post': post,
        'comment': comment,
        'post_id': post_id,
    })
