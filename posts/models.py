"""
Models for posts, tags, reactions, and comments.
"""

from django.db import models
from django.contrib.auth.models import User
from study.models import StudySet


class Tag(models.Model):
    """
    Tag for categorizing posts.
    Predefined tags with specific colors.
    """
    name = models.CharField(max_length=50, unique=True, verbose_name='اسم التصنيف')
    color = models.CharField(max_length=7, default='#94a3b8', verbose_name='اللون')

    class Meta:
        verbose_name = 'تصنيف'
        verbose_name_plural = 'التصنيفات'
        ordering = ['name']

    def __str__(self):
        return self.name


class Post(models.Model):
    """
    A post sharing a study set.
    Posts are soft-deleted (deleted_at).
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='الكاتب'
    )
    study_set = models.ForeignKey(
        StudySet,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='المجموعة الدراسية'
    )
    title = models.CharField(max_length=200, verbose_name='العنوان')
    caption = models.TextField(
        blank=True,
        null=True,
        verbose_name='وصف قصير'
    )
    tags = models.ManyToManyField(
        Tag,
        through='PostTag',
        related_name='posts',
        verbose_name='الوسوم'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'منشور'
        verbose_name_plural = 'المنشورات'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    @property
    def likes_count(self):
        return self.reactions.filter(value='like').count()

    @property
    def dislikes_count(self):
        return self.reactions.filter(value='dislike').count()

    def get_user_reaction(self, user):
        """Get user's reaction to this post, if any."""
        if not user.is_authenticated:
            return None
        reaction = self.reactions.filter(user=user).first()
        return reaction.value if reaction else None


class PostTag(models.Model):
    """Through model for Post-Tag relationship."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'tag')


class Reaction(models.Model):
    """
    User reaction to a post (like or dislike).
    Only one reaction per user per post.
    """
    VALUE_CHOICES = [
        ('like', 'إعجاب'),
        ('dislike', 'عدم إعجاب'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    value = models.CharField(max_length=10, choices=VALUE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'تفاعل'
        verbose_name_plural = 'التفاعلات'
        unique_together = ('user', 'post')


class Comment(models.Model):
    """
    Simple comment on a post.
    No replies or reactions on comments.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    body = models.TextField(verbose_name='التعليق')
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'تعليق'
        verbose_name_plural = 'التعليقات'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username}: {self.body[:30]}'

    @property
    def is_deleted(self):
        return self.deleted_at is not None
