"""
Forms for user registration and profile management.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile


class SignUpForm(UserCreationForm):
    """Form for user registration."""
    email = forms.EmailField(
        required=True,
        label='البريد الإلكتروني',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com',
            'dir': 'ltr'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'اسم المستخدم',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المستخدم',
                'dir': 'ltr'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'كلمة المرور'
        self.fields['password2'].label = 'تأكيد كلمة المرور'
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'كلمة المرور',
            'dir': 'ltr'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'أعد كتابة كلمة المرور',
            'dir': 'ltr'
        })
        # Arabic help texts
        self.fields['username'].help_text = 'مطلوب. 150 حرف أو أقل. أحرف وأرقام و @/./+/-/_ فقط.'
        self.fields['password1'].help_text = 'كلمة المرور يجب أن تحتوي على 8 أحرف على الأقل.'
        self.fields['password2'].help_text = 'أدخل نفس كلمة المرور للتأكيد.'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('هذا البريد الإلكتروني مستخدم بالفعل.')
        return email


class LoginForm(AuthenticationForm):
    """Form for user login."""
    username = forms.CharField(
        label='اسم المستخدم',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اسم المستخدم',
            'dir': 'ltr'
        })
    )
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'كلمة المرور',
            'dir': 'ltr'
        })
    )

    error_messages = {
        'invalid_login': 'اسم المستخدم أو كلمة المرور غير صحيحة.',
        'inactive': 'هذا الحساب غير مفعل.',
    }


class ProfileForm(forms.ModelForm):
    """Form for editing user profile."""
    class Meta:
        model = Profile
        fields = ('bio',)
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'اكتب نبذة عنك...'
            })
        }


class UserUpdateForm(forms.ModelForm):
    """Form for updating user basic info."""
    email = forms.EmailField(
        label='البريد الإلكتروني',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'dir': 'ltr'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email')
        labels = {
            'username': 'اسم المستخدم',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'dir': 'ltr'
            }),
        }
