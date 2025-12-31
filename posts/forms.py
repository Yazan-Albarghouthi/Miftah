"""
Forms for creating posts and comments.
"""

from django import forms
from .models import Post, Tag, Comment


class PostForm(forms.ModelForm):
    """Form for creating a new post."""

    tags_input = forms.CharField(
        label='الوسوم',
        help_text='أدخل الوسوم مفصولة بفواصل (مطلوب وسم واحد على الأقل)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'مثال: فيزياء، كيمياء، أحياء'
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

    def clean_tags_input(self):
        tags_input = self.cleaned_data.get('tags_input', '')
        # Split by comma and clean
        tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]

        if not tag_names:
            raise forms.ValidationError('يرجى إدخال وسم واحد على الأقل.')

        if len(tag_names) > 10:
            raise forms.ValidationError('الحد الأقصى 10 وسوم.')

        # Validate each tag
        for name in tag_names:
            if len(name) > 50:
                raise forms.ValidationError(f'الوسم "{name}" طويل جداً (الحد الأقصى 50 حرف).')

        return tag_names

    def save(self, commit=True, author=None, study_set=None):
        post = super().save(commit=False)

        if author:
            post.author = author
        if study_set:
            post.study_set = study_set

        if commit:
            post.save()

            # Create tags
            tag_names = self.cleaned_data.get('tags_input', [])
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                post.tags.add(tag)

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
