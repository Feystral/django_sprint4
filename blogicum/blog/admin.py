from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.utils.safestring import mark_safe
from typing import Optional, Any

from .models import Category, Location, Post, Comment

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published')
    search_fields = ('name',)
    list_filter = ('is_published',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published')
    search_fields = ('title', 'slug')
    list_filter = ('is_published',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'pub_date', 'is_published')
    search_fields = ('title', 'author__username', 'category__title')
    list_filter = ('is_published', 'pub_date', 'category')
    list_display_links = ('title', 'author')

    def image_preview(self, obj: Any) -> Optional[str]:
        if hasattr(obj, 'image') and obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80"'
                             'height="60" style="object-fit:cover;'
                             'border-radius:4px;">')
        return "Нет изображения"
    setattr(image_preview, 'short_description', 'Превью изображения')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'posts_count')
    search_fields = ('username', 'email')

    @admin.display(description='Кол-во постов')
    def posts_count(self, obj):
        return obj.posts.count()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'created_at')
    search_fields = ('text', 'author__username', 'post__title')
    list_filter = ('created_at', 'post')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
