from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.utils import timezone
from django.http import Http404

from .models import Category, Post, Comment
from .forms import PostForm, CommentForm
from .services import (paginate_queryset,
                       filter_published_posts,
                       annotate_with_comment_count)
from .constants import POSTS_PER_PAGE


def error_404_or_object(request, model, *args, **kwargs):
    try:
        obj = get_object_or_404(model, *args, **kwargs)
        return obj
    except Http404:
        return render(request, 'pages/404.html', status=404)


def index(request):
    posts = filter_published_posts(Post.objects.all())
    posts = annotate_with_comment_count(posts)
    page_number = request.GET.get('page')
    page_obj = paginate_queryset(posts, page_number, POSTS_PER_PAGE)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
    except Http404:
        return render(request, 'pages/404.html', status=404)

    if (post.pub_date > timezone.now() and post.author != request.user
        or not post.category.is_published and post.author != request.user
            or not post.is_published and post.author != request.user):
        return render(request, 'pages/404.html', status=404)

    comments = post.comments.select_related('author').all()

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
    })


def category_posts(request, category_slug):
    try:
        category = get_object_or_404(Category,
                                     slug=category_slug,
                                     is_published=True)
    except Http404:
        return render(request, 'pages/404.html', status=404)
    posts = filter_published_posts(
        annotate_with_comment_count(
            category.posts.all().select_related('author', 'category'))
    )

    page_number = request.GET.get('page')
    page_obj = paginate_queryset(posts, page_number, POSTS_PER_PAGE)

    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj,
    })


def profile(request, username):
    try:
        author = get_object_or_404(User, username=username)
    except Http404:
        return render(request, 'pages/404.html', status=404)
    posts = annotate_with_comment_count(author.posts.order_by('-pub_date'))

    if not (request.user.is_authenticated and request.user == author):
        posts = filter_published_posts(posts)

    page_number = request.GET.get('page')
    page_obj = paginate_queryset(posts, page_number, POSTS_PER_PAGE)

    return render(request, 'blog/profile.html', {
        'profile': author,
        'page_obj': page_obj,
    })


@login_required
def edit_profile(request):
    form = UserChangeForm(request.POST or None, instance=request.user)

    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/user.html', {'form': form})


@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
    except Http404:
        return render(request, 'pages/404.html', status=404)

    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post.id)

    form = PostForm(request.POST or None, request.FILES or None, instance=post)

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.id)

    return render(request, 'blog/create.html', {'form': form, 'is_edit': True})


@login_required
def delete_post(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
    except Http404:
        return render(request, 'pages/404.html', status=404)

    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post.id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')

    return render(request, 'blog/create.html', {'post': post})


@login_required
def delete_comment(request, post_id, comment_id):
    try:
        comment = get_object_or_404(Comment, id=comment_id)
    except Http404:
        return render(request, 'pages/404.html', status=404)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', {
        'comment': comment,
        'delete': True,
    })


@login_required
def add_comment(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
    except Http404:
        return render(request, 'pages/404.html', status=404)

    if request.method == 'POST':
        form = CommentForm(request.POST or None)
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
    try:
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    except Http404:
        return render(request, 'pages/404.html', status=404)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', {
        'form': form,
        'comment': comment,
    })
