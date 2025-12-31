"""
Admin configuration for posts app.
"""

from django.contrib import admin
from .models import Post, Tag, Reaction, Comment


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'study_set', 'created_at', 'deleted_at')
    list_filter = ('created_at', 'deleted_at')
    search_fields = ('title', 'author__username')
    readonly_fields = ('created_at',)


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'value', 'created_at')
    list_filter = ('value', 'created_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'body', 'created_at', 'deleted_at')
    list_filter = ('created_at', 'deleted_at')
    search_fields = ('body', 'author__username')
