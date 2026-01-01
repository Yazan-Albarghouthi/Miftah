"""
Forms for the admin panel.
"""

from django import forms
from .models import Report


class ReportForm(forms.ModelForm):
    """Form for submitting a report."""

    class Meta:
        model = Report
        fields = ['reason', 'details']
        widgets = {
            'reason': forms.Select(attrs={
                'class': 'form-select',
            }),
            'details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أضف أي تفاصيل تساعد في فهم البلاغ...'
            }),
        }
