"""
Forms for creating posts and comments.
"""

from django import forms
from .models import Post, Tag, Comment


class PostForm(forms.ModelForm):
    """Form for creating a new post."""

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by('name'),
        label='التصنيفات',
        help_text='اختر من 1 إلى 4 تصنيفات',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'tag-checkbox-list'
        })
    )

    class Meta:
        model = Post
        fields = ['title', 'caption']
        labels = {
            'title': 'العنوان',
            'caption': 'وصف قصير (اختياري)',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان المنشور'
            }),
            'caption': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'اكتب وصفاً قصيراً عن المحتوى...'
            }),
        }

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', [])

        if len(tags) < 1:
            raise forms.ValidationError('يرجى اختيار تصنيف واحد على الأقل.')

        if len(tags) > 4:
            raise forms.ValidationError('الحد الأقصى 4 تصنيفات.')

        return tags

    def save(self, commit=True, author=None, study_set=None):
        post = super().save(commit=False)

        if author:
            post.author = author
        if study_set:
            post.study_set = study_set

        if commit:
            post.save()

            # Add selected tags
            tags = self.cleaned_data.get('tags', [])
            post.tags.set(tags)

        return post


class CommentForm(forms.ModelForm):
    """Form for adding a comment."""

    class Meta:
        model = Comment
        fields = ['body']
        labels = {
            'body': 'التعليق',
        }
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'اكتب تعليقك...'
            }),
        }
