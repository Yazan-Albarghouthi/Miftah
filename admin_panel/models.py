"""
Models for admin panel and content moderation.
"""

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Report(models.Model):
    """
    Report submitted by users against inappropriate content.
    Uses GenericForeignKey to support reporting both Posts and Comments.
    """
    REASON_CHOICES = [
        ('hate_speech', 'خطاب كراهية'),
        ('spam', 'محتوى مزعج (سبام)'),
        ('inappropriate', 'محتوى غير لائق'),
        ('misinformation', 'معلومات مضللة'),
        ('harassment', 'تحرش أو إساءة'),
        ('other', 'أخرى'),
    ]

    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'تمت الموافقة'),
        ('dismissed', 'مرفوض'),
    ]

    # Reporter
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports_submitted',
        verbose_name='المُبلِّغ'
    )

    # Generic relation to reported content (Post or Comment)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name='نوع المحتوى'
    )
    object_id = models.PositiveIntegerField(verbose_name='معرف المحتوى')
    content_object = GenericForeignKey('content_type', 'object_id')

    # Report details
    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        verbose_name='سبب البلاغ'
    )
    details = models.TextField(
        blank=True,
        verbose_name='تفاصيل إضافية'
    )

    # Status and resolution
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='الحالة'
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_reviewed',
        verbose_name='المُراجع'
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ المراجعة'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        verbose_name = 'بلاغ'
        verbose_name_plural = 'البلاغات'
        ordering = ['-created_at']
        # Prevent duplicate reports from same user on same content
        unique_together = ('reporter', 'content_type', 'object_id')

    def __str__(self):
        return f'بلاغ #{self.pk} - {self.get_reason_display()}'

    @property
    def is_pending(self):
        return self.status == 'pending'

    def get_reported_content_preview(self):
        """Get a preview of the reported content."""
        obj = self.content_object
        if obj is None:
            return "محتوى محذوف"
        if hasattr(obj, 'title'):
            return obj.title[:50]
        if hasattr(obj, 'body'):
            return obj.body[:50]
        return str(obj)[:50]

    def get_content_type_display_ar(self):
        """Get Arabic display name for content type."""
        if self.content_type.model == 'post':
            return 'منشور'
        elif self.content_type.model == 'comment':
            return 'تعليق'
        return self.content_type.model
