"""
Admin configuration for study app.
"""

from django.contrib import admin
from .models import StudySet, Flashcard, QuizQuestion


class FlashcardInline(admin.TabularInline):
    model = Flashcard
    extra = 0


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 0


@admin.register(StudySet)
class StudySetAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'set_type', 'language', 'item_count', 'created_at')
    list_filter = ('set_type', 'language', 'created_at')
    search_fields = ('title', 'owner__username')
    readonly_fields = ('created_at',)
    inlines = [FlashcardInline, QuizQuestionInline]


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ('study_set', 'index', 'question')
    list_filter = ('study_set__set_type',)
    search_fields = ('question', 'answer')


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('study_set', 'index', 'question', 'correct_index')
    search_fields = ('question',)
