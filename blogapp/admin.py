from django.contrib import admin
from .models import Author, Category, Tag, Article


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'pub_date']
    list_filter = ['category', 'author', 'pub_date']
    search_fields = ['title', 'content']
    filter_horizontal = ['tags']
    date_hierarchy = 'pub_date'