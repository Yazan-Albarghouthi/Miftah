"""
Django admin configuration for admin_panel app.
"""

from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'reporter', 'content_type', 'reason', 'status', 'created_at', 'reviewed_at']
    list_filter = ['status', 'reason', 'content_type', 'created_at']
    search_fields = ['reporter__username', 'details']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
