"""
Forms for study set generation.
"""

from django import forms


class GenerateStudySetForm(forms.Form):
    """Form for generating flashcards or quizzes."""

    TYPE_CHOICES = [
        ('flashcards', 'بطاقات تعليمية'),
        ('quiz', 'اختبار'),
    ]

    INPUT_CHOICES = [
        ('text', 'نص'),
        ('pdf', 'ملف PDF'),
    ]

    set_type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='نوع المجموعة'
    )

    input_type = forms.ChoiceField(
        choices=INPUT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='text',
        label='نوع المدخل'
    )

    text_content = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'الصق النص هنا...'
        }),
        label='النص'
    )

    pdf_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf'
        }),
        label='ملف PDF'
    )

    count = forms.IntegerField(
        min_value=1,
        max_value=30,
        initial=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'style': 'width: 100px;'
        }),
        label='عدد العناصر'
    )

    title = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'عنوان اختياري للمجموعة'
        }),
        label='العنوان (اختياري)'
    )

    def clean(self):
        cleaned_data = super().clean()
        input_type = cleaned_data.get('input_type')
        text_content = cleaned_data.get('text_content')
        pdf_file = cleaned_data.get('pdf_file')

        if input_type == 'text':
            if not text_content or len(text_content.strip()) < 50:
                raise forms.ValidationError(
                    'يرجى إدخال نص لا يقل عن 50 حرفاً.'
                )
        elif input_type == 'pdf':
            if not pdf_file:
                raise forms.ValidationError(
                    'يرجى رفع ملف PDF.'
                )
            # Check file extension
            if not pdf_file.name.lower().endswith('.pdf'):
                raise forms.ValidationError(
                    'يرجى رفع ملف بصيغة PDF فقط.'
                )
            # Check file size (max 10MB)
            if pdf_file.size > 10 * 1024 * 1024:
                raise forms.ValidationError(
                    'حجم الملف يجب أن لا يتجاوز 10 ميجابايت.'
                )

        return cleaned_data
