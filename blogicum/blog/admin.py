from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User

from .models import Category, Location, Post

admin.site.unregister(User)


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


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'posts_count')
    search_fields = ('username', 'email')

    @admin.display(description='Кол-во постов')
    def posts_count(self, obj):
        return obj.posts.count()


admin.site.unregister(Group)
