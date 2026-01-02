# MIFTAH - Complete Project Documentation
## Every Single File Explained In Detail

This document provides exhaustive documentation of every file in the Miftah project, explaining every line of code, the logic behind it, and how files relate to each other.

---

# TABLE OF CONTENTS

1. [Project Overview](#project-overview)
2. [Root Configuration Files](#root-configuration-files)
3. [Django Project Configuration (miftah/)](#django-project-configuration-miftah)
4. [Accounts App](#accounts-app)
5. [Study App](#study-app)
6. [Posts App](#posts-app)
7. [Admin Panel App](#admin-panel-app)
8. [Templates](#templates)
9. [Database Schema](#database-schema)
10. [File Relationships](#file-relationships)

---

# PROJECT OVERVIEW

**Miftah** (Arabic for "Key") is an Arabic educational platform built with Django that allows users to:
- Generate AI-powered flashcards and quizzes from text or PDF files
- Share study materials with other users
- Follow other users and interact with their content
- Like/dislike posts and leave comments
- Report inappropriate content

## Technology Stack
- **Backend**: Django 5.x (Python 3.12)
- **Database**: PostgreSQL 16
- **AI**: DeepSeek API (via OpenAI Python client)
- **Frontend**: Bootstrap 5 RTL + HTMX
- **Containerization**: Docker & Docker Compose

---

# ROOT CONFIGURATION FILES

## 1. manage.py

**Location**: `manage.py`
**Purpose**: Django's command-line utility for administrative tasks

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os                                                    # Line 3: Import os module for environment variables
import sys                                                   # Line 4: Import sys for command-line arguments


def main():                                                  # Line 7: Define main function
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miftah.settings')  # Line 9: Set default settings module
    try:                                                     # Line 10: Try block for importing Django
        from django.core.management import execute_from_command_line  # Line 11: Import Django's CLI handler
    except ImportError as exc:                              # Line 12: Catch import errors
        raise ImportError(                                   # Line 13-17: Raise descriptive error
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)                     # Line 18: Execute the command with arguments


if __name__ == '__main__':                                  # Line 21: Only run if executed directly
    main()                                                   # Line 22: Call main function
```

**How it works**:
1. Sets `DJANGO_SETTINGS_MODULE` environment variable to `miftah.settings`
2. Imports Django's management command executor
3. Passes command-line arguments (like `runserver`, `migrate`, etc.) to Django

**Used for**: Running commands like `python manage.py runserver`, `migrate`, `createsuperuser`, etc.

---

## 2. requirements.txt

**Location**: `requirements.txt`
**Purpose**: Python package dependencies

```
Django>=5.0,<6.0          # Django web framework, version 5.x
psycopg2-binary>=2.9.9    # PostgreSQL adapter for Python
python-decouple>=3.8      # Configuration management (reads .env files)
openai>=1.0.0             # OpenAI Python client (used for DeepSeek API)
pypdf>=4.0.0              # PDF text extraction library
gunicorn>=21.0.0          # Production WSGI server (not used in dev)
```

**Why each package**:
- `Django`: The web framework powering the entire application
- `psycopg2-binary`: Required for PostgreSQL database connection
- `python-decouple`: Reads configuration from `.env` file (SECRET_KEY, DB passwords)
- `openai`: Provides the client interface for DeepSeek API (DeepSeek uses OpenAI-compatible API)
- `pypdf`: Extracts text from PDF files for AI processing
- `gunicorn`: Production-ready WSGI HTTP server

---

## 3. Dockerfile

**Location**: `Dockerfile`
**Purpose**: Docker image build instructions

```dockerfile
FROM python:3.12-slim                    # Line 1: Base image - Python 3.12 slim (minimal Debian)

WORKDIR /app                             # Line 3: Set working directory inside container

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y \  # Line 6-9: Install system packages
    gcc \                                    # C compiler (needed to build psycopg2)
    libpq-dev \                              # PostgreSQL development headers
    && rm -rf /var/lib/apt/lists/*           # Clean up apt cache to reduce image size

COPY requirements.txt .                   # Line 11: Copy requirements file first (for layer caching)
RUN pip install --no-cache-dir -r requirements.txt  # Line 12: Install Python packages

COPY . .                                  # Line 14: Copy entire project into container

EXPOSE 8000                               # Line 16: Document that container listens on port 8000

CMD ["./entrypoint.sh"]                   # Line 18: Run entrypoint script when container starts
```

**Build optimization**:
- Copies `requirements.txt` before the full project so Docker can cache the pip install layer
- Uses `--no-cache-dir` to avoid storing pip cache in the image

---

## 4. docker-compose.yml

**Location**: `docker-compose.yml`
**Purpose**: Multi-container Docker application definition

```yaml
services:
  db:                                     # PostgreSQL database service
    image: postgres:16-alpine             # Use PostgreSQL 16 (Alpine for smaller size)
    environment:
      POSTGRES_DB: miftah                 # Create database named "miftah"
      POSTGRES_USER: miftah               # Database username
      POSTGRES_PASSWORD: miftah123        # Database password
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Persist database data
    healthcheck:                          # Health check configuration
      test: ["CMD-SHELL", "pg_isready -U miftah"]  # Check if PostgreSQL is ready
      interval: 5s                        # Check every 5 seconds
      timeout: 5s                         # Timeout after 5 seconds
      retries: 5                          # Retry 5 times before marking unhealthy

  web:                                    # Django web application service
    build: .                              # Build from Dockerfile in current directory
    ports:
      - "8000:8000"                        # Map host port 8000 to container port 8000
    volumes:
      - .:/app                            # Mount current directory for live code changes
    env_file:
      - .env                              # Load environment variables from .env file
    depends_on:
      db:
        condition: service_healthy        # Wait until db is healthy before starting

volumes:
  postgres_data:                          # Named volume for PostgreSQL data persistence
```

**Service relationships**:
- `web` depends on `db` - Django won't start until PostgreSQL is healthy
- Volume mount allows code changes without rebuilding the container

---

## 5. entrypoint.sh

**Location**: `entrypoint.sh`
**Purpose**: Container startup script

```bash
#!/bin/bash                               # Line 1: Bash shell interpreter

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."          # Line 4: Status message
while ! python -c "import socket; socket.create_connection(('db', 5432))" 2>/dev/null; do
    # Line 5-7: Python one-liner to check if port 5432 is open on 'db' host
    sleep 1                               # Wait 1 second before retry
done
echo "PostgreSQL is ready!"               # Line 9: Success message

# Run database migrations
echo "Running migrations..."              # Line 12: Status message
python manage.py migrate --noinput        # Line 13: Apply all pending migrations

# Collect static files
echo "Collecting static files..."         # Line 16: Status message
python manage.py collectstatic --noinput  # Line 17: Gather static files

# Start development server
echo "Starting Django development server..."  # Line 20: Status message
python manage.py runserver 0.0.0.0:8000       # Line 21: Start server on all interfaces, port 8000
```

**Startup sequence**:
1. Wait for PostgreSQL to accept connections (using Python socket)
2. Run database migrations
3. Collect static files
4. Start Django development server

---

## 6. .env

**Location**: `.env`
**Purpose**: Environment-specific configuration (secrets)

```
DEBUG=True                                # Enable Django debug mode
SECRET_KEY=your-secret-key-here-change-in-production  # Django secret key for cryptographic signing
DATABASE_URL=postgres://miftah:miftah123@db:5432/miftah  # PostgreSQL connection string

# DeepSeek AI Configuration
DEEPSEEK_API_KEY=sk-68e8cd12841e47abaa9e0d6d1d185c7a  # API key for DeepSeek
DEEPSEEK_BASE_URL=https://api.deepseek.com           # DeepSeek API endpoint
```

**Security note**: This file contains sensitive information and should never be committed to version control in production.

---

# DJANGO PROJECT CONFIGURATION (miftah/)

## 1. miftah/__init__.py

**Location**: `miftah/__init__.py`
**Purpose**: Marks directory as Python package

```python
# Empty file - its presence makes 'miftah' a Python package
```

This file is empty but essential. Python requires `__init__.py` to recognize a directory as an importable package.

---

## 2. miftah/settings.py

**Location**: `miftah/settings.py`
**Purpose**: Central Django configuration

```python
"""
Django settings for miftah project.
"""

from pathlib import Path                           # Line 5: Modern path handling
from decouple import config                        # Line 6: Read from .env file

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent  # Line 9: Project root directory
# Path(__file__) = this file's path
# .resolve() = absolute path
# .parent.parent = go up two directories (miftah/ -> project root)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-fallback-key')
# Line 13: Read SECRET_KEY from .env, with fallback for development

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)
# Line 16: Read DEBUG from .env, convert string to boolean

ALLOWED_HOSTS = ['*']                              # Line 18: Allow all hosts (restrict in production)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',       # Line 22: Django admin interface
    'django.contrib.auth',        # Line 23: Authentication system
    'django.contrib.contenttypes', # Line 24: Content type framework (for GenericForeignKey)
    'django.contrib.sessions',    # Line 25: Session management
    'django.contrib.messages',    # Line 26: Flash messages
    'django.contrib.staticfiles', # Line 27: Static file handling

    # Project apps
    'accounts',                   # Line 30: User accounts, profiles, follows
    'study',                      # Line 31: Study sets, flashcards, quizzes
    'posts',                      # Line 32: Posts, comments, reactions
    'admin_panel',                # Line 33: Custom admin dashboard, reports
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',        # Line 37: Security headers
    'django.contrib.sessions.middleware.SessionMiddleware', # Line 38: Session handling
    'django.middleware.common.CommonMiddleware',            # Line 39: Common operations
    'django.middleware.csrf.CsrfViewMiddleware',            # Line 40: CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Line 41: User authentication
    'django.contrib.messages.middleware.MessageMiddleware',    # Line 42: Flash messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Line 43: Clickjacking protection
]

ROOT_URLCONF = 'miftah.urls'              # Line 46: Root URL configuration module

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # Line 50: Django template engine
        'DIRS': [BASE_DIR / 'templates'],  # Line 51: Global templates directory
        'APP_DIRS': True,                  # Line 52: Look for templates in app directories
        'OPTIONS': {
            'context_processors': [        # Line 54-59: Variables available in all templates
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Makes 'request' available
                'django.contrib.auth.context_processors.auth', # Makes 'user' available
                'django.contrib.messages.context_processors.messages', # Flash messages
            ],
        },
    },
]

WSGI_APPLICATION = 'miftah.wsgi.application'  # Line 64: WSGI application path

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # Line 69: PostgreSQL backend
        'NAME': 'miftah',                           # Line 70: Database name
        'USER': 'miftah',                           # Line 71: Database user
        'PASSWORD': 'miftah123',                    # Line 72: Database password
        'HOST': 'db',                               # Line 73: PostgreSQL host (Docker service name)
        'PORT': '5432',                             # Line 74: PostgreSQL port
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
# Lines 78-83: Password strength requirements

# Internationalization
LANGUAGE_CODE = 'ar'                      # Line 86: Arabic language
TIME_ZONE = 'Asia/Riyadh'                 # Line 87: Saudi Arabia timezone
USE_I18N = True                           # Line 88: Enable internationalization
USE_TZ = True                             # Line 89: Enable timezone support

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'                    # Line 92: URL prefix for static files
STATIC_ROOT = BASE_DIR / 'staticfiles'    # Line 93: Directory for collected static files

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  # Line 96: Use BigAutoField for primary keys

# Login/Logout URLs
LOGIN_URL = 'accounts:login'              # Line 99: Redirect here when @login_required fails
LOGIN_REDIRECT_URL = 'home'               # Line 100: Redirect here after login

# DeepSeek AI Configuration
DEEPSEEK_API_KEY = config('DEEPSEEK_API_KEY', default='')      # Line 103: DeepSeek API key
DEEPSEEK_BASE_URL = config('DEEPSEEK_BASE_URL', default='https://api.deepseek.com')  # Line 104: API URL
```

**Key configurations**:
- Uses PostgreSQL database hosted in Docker container named 'db'
- Arabic language and Riyadh timezone
- Four custom apps: accounts, study, posts, admin_panel
- DeepSeek API configured via environment variables

---

## 3. miftah/urls.py

**Location**: `miftah/urls.py`
**Purpose**: Root URL routing

```python
"""
URL configuration for miftah project.
"""

from django.contrib import admin                   # Line 5: Django admin
from django.urls import path, include             # Line 6: URL routing functions
from . import views                               # Line 7: Import views from this package

urlpatterns = [
    # Landing page (unauthenticated)
    path('', views.landing, name='landing'),       # Line 11: Root URL -> landing page

    # Home page (authenticated)
    path('home/', views.home, name='home'),        # Line 14: Home dashboard

    # Django Admin
    path('admin/', admin.site.urls),               # Line 17: Built-in Django admin

    # App URLs
    path('accounts/', include('accounts.urls')),   # Line 20: Account-related URLs
    path('study/', include('study.urls')),         # Line 21: Study set URLs
    path('posts/', include('posts.urls')),         # Line 22: Post URLs
    path('feed/', include('posts.feed_urls')),     # Line 23: Feed URLs (recent/following)
    path('admin-panel/', include('admin_panel.urls')),  # Line 24: Custom admin panel
]
```

**URL structure**:
- `/` - Landing page for guests
- `/home/` - Dashboard for authenticated users
- `/admin/` - Django's built-in admin
- `/accounts/` - Login, signup, profile, etc.
- `/study/` - Flashcards and quizzes
- `/posts/` - Post creation, detail, reactions
- `/feed/` - Recent and following feeds
- `/admin-panel/` - Staff moderation dashboard

---

## 4. miftah/views.py

**Location**: `miftah/views.py`
**Purpose**: Root-level view functions

```python
"""
Root views for landing and home pages.
"""

from django.shortcuts import render, redirect     # Line 5: Response helpers
from django.contrib.auth.decorators import login_required  # Line 6: Auth decorator


def landing(request):                             # Line 9: Landing page view
    """Show landing page for unauthenticated users."""
    if request.user.is_authenticated:             # Line 11: Check if logged in
        return redirect('home')                   # Line 12: Redirect to home if logged in
    return render(request, 'landing.html')        # Line 13: Show landing page


@login_required                                   # Line 16: Require login
def home(request):                                # Line 17: Home page view
    """Show home dashboard for authenticated users."""
    return render(request, 'home.html')           # Line 19: Render home template
```

**Flow logic**:
- Unauthenticated users see `landing.html` (marketing page)
- Authenticated users are redirected to `home.html` (dashboard)
- `home` view requires login (redirects to login page if not authenticated)

---

## 5. miftah/wsgi.py

**Location**: `miftah/wsgi.py`
**Purpose**: WSGI application entry point

```python
"""
WSGI config for miftah project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os                                         # Line 10: OS module

from django.core.wsgi import get_wsgi_application  # Line 12: WSGI app factory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miftah.settings')  # Line 14: Set settings

application = get_wsgi_application()              # Line 16: Create WSGI application
```

**Purpose**: This is the entry point for WSGI-compatible web servers (like Gunicorn) to serve the Django application in production.

---

# ACCOUNTS APP

The accounts app handles user authentication, profiles, and follow relationships.

## 1. accounts/__init__.py

**Location**: `accounts/__init__.py`

Empty file marking this directory as a Python package.

---

## 2. accounts/models.py

**Location**: `accounts/models.py`
**Purpose**: User profile and follow relationship models

```python
"""
Models for user accounts, profiles, and follow relationships.
"""

from django.db import models                      # Line 5: Django ORM
from django.contrib.auth.models import User       # Line 6: Built-in User model
from django.db.models.signals import post_save    # Line 7: Signal for post-save events
from django.dispatch import receiver              # Line 8: Signal receiver decorator


class Profile(models.Model):                      # Line 11: Profile model definition
    """
    Extended user profile.
    Each User has one Profile created automatically.
    """
    user = models.OneToOneField(                  # Line 16: One-to-one with User
        User,
        on_delete=models.CASCADE,                 # Delete profile when user is deleted
        related_name='profile'                    # Access as user.profile
    )
    bio = models.TextField(                       # Line 21: User biography
        max_length=500,
        blank=True,                               # Optional field
        verbose_name='نبذة عني'                   # Arabic label
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Line 26: Auto-set on creation

    class Meta:                                   # Line 28: Model metadata
        verbose_name = 'الملف الشخصي'             # Arabic singular name
        verbose_name_plural = 'الملفات الشخصية'   # Arabic plural name

    def __str__(self):                            # Line 32: String representation
        return f'ملف {self.user.username}'        # "Profile of [username]" in Arabic

    @property                                     # Line 35: Computed property
    def followers_count(self):                    # Line 36: Count followers
        """Number of users following this user."""
        return self.user.followers.count()        # Uses Follow.followers related_name

    @property                                     # Line 40: Computed property
    def following_count(self):                    # Line 41: Count following
        """Number of users this user follows."""
        return self.user.following.count()        # Uses Follow.following related_name


class Follow(models.Model):                       # Line 46: Follow relationship model
    """
    Follow relationship between users.
    follower follows following.
    """
    follower = models.ForeignKey(                 # Line 51: Who is following
        User,
        on_delete=models.CASCADE,                 # Delete follows when user deleted
        related_name='following',                 # user.following = users this user follows
        verbose_name='المتابِع'                   # Arabic: "The follower"
    )
    following = models.ForeignKey(                # Line 57: Who is being followed
        User,
        on_delete=models.CASCADE,
        related_name='followers',                 # user.followers = users following this user
        verbose_name='المتابَع'                   # Arabic: "The followed"
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Line 63: When follow occurred

    class Meta:                                   # Line 65: Model metadata
        verbose_name = 'متابعة'
        verbose_name_plural = 'المتابعات'
        unique_together = ('follower', 'following')  # Line 68: Prevent duplicate follows
        constraints = [                           # Line 69: Database constraints
            models.CheckConstraint(               # Line 70: Check constraint
                check=~models.Q(follower=models.F('following')),  # follower != following
                name='prevent_self_follow'        # Constraint name
            )
        ]
    # This constraint prevents a user from following themselves

    def __str__(self):                            # Line 76: String representation
        return f'{self.follower.username} يتابع {self.following.username}'
        # "[user] follows [user]" in Arabic


# Signal to create Profile automatically when User is created
@receiver(post_save, sender=User)                 # Line 81: Listen to User.save()
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile when a new User is created."""
    if created:                                   # Line 84: Only on new user creation
        Profile.objects.create(user=instance)     # Line 85: Create profile for new user


@receiver(post_save, sender=User)                 # Line 88: Another post_save signal
def save_user_profile(sender, instance, **kwargs):
    """Save the Profile when User is saved."""
    if hasattr(instance, 'profile'):              # Line 91: Check if profile exists
        instance.profile.save()                   # Line 92: Save the profile
```

**Model relationships**:
- `User` (Django built-in) ↔ `Profile` (one-to-one)
- `User` ↔ `Follow` ↔ `User` (many-to-many through Follow)

**Signal pattern**: When a User is created, a Profile is automatically created for them.

---

## 3. accounts/views.py

**Location**: `accounts/views.py`
**Purpose**: Authentication and profile views

```python
"""
Views for user authentication, profiles, and follow system.
"""

from django.shortcuts import render, redirect, get_object_or_404  # Line 5: Helper functions
from django.contrib.auth import login, logout    # Line 6: Auth functions
from django.contrib.auth.decorators import login_required  # Line 7: Require login
from django.contrib.auth.models import User      # Line 8: User model
from django.contrib import messages              # Line 9: Flash messages
from django.http import HttpResponse             # Line 10: HTTP response
from django.views.decorators.http import require_POST  # Line 11: POST-only decorator

from .forms import SignUpForm, LoginForm, ProfileForm, UserUpdateForm  # Line 13: Form classes
from .models import Follow                       # Line 14: Follow model


def signup_view(request):                        # Line 17: User registration
    """Handle user registration."""
    if request.user.is_authenticated:            # Line 19: Already logged in?
        return redirect('home')                  # Line 20: Go to home

    if request.method == 'POST':                 # Line 22: Form submitted
        form = SignUpForm(request.POST)          # Line 23: Create form with POST data
        if form.is_valid():                      # Line 24: Validate form
            user = form.save()                   # Line 25: Save new user
            login(request, user)                 # Line 26: Log in the new user
            messages.success(request, 'تم إنشاء حسابك بنجاح! مرحباً بك في مفتاح.')
            # Line 27: Success message in Arabic
            return redirect('home')              # Line 28: Go to home
    else:                                        # Line 29: GET request
        form = SignUpForm()                      # Line 30: Empty form

    return render(request, 'accounts/signup.html', {'form': form})  # Line 32: Render template


def login_view(request):                         # Line 35: User login
    """Handle user login."""
    if request.user.is_authenticated:            # Line 37: Already logged in?
        return redirect('home')                  # Line 38: Go to home

    if request.method == 'POST':                 # Line 40: Form submitted
        form = LoginForm(request, data=request.POST)  # Line 41: Create form with data
        if form.is_valid():                      # Line 42: Validate credentials
            user = form.get_user()               # Line 43: Get authenticated user
            login(request, user)                 # Line 44: Log in
            messages.success(request, f'مرحباً {user.username}!')  # Line 45: Welcome message
            # Redirect to next page if specified, otherwise home
            next_url = request.GET.get('next', 'home')  # Line 47: Get 'next' parameter
            return redirect(next_url)            # Line 48: Redirect
    else:                                        # Line 49: GET request
        form = LoginForm()                       # Line 50: Empty form

    return render(request, 'accounts/login.html', {'form': form})  # Line 52: Render template


@login_required                                  # Line 55: Require login
def logout_view(request):                        # Line 56: User logout
    """Handle user logout."""
    logout(request)                              # Line 58: Log out user
    messages.info(request, 'تم تسجيل خروجك بنجاح.')  # Line 59: Logout message
    return redirect('landing')                   # Line 60: Go to landing page


@login_required                                  # Line 63: Require login
def profile_view(request, username):             # Line 64: View user profile
    """View a user's profile."""
    profile_user = get_object_or_404(User, username=username)  # Line 66: Get user or 404
    is_own_profile = request.user == profile_user  # Line 67: Check if viewing own profile

    # Get follow status
    is_following = False                         # Line 70: Default not following
    follows_me = False                           # Line 71: Default not followed

    if not is_own_profile:                       # Line 73: Only check for other users
        is_following = Follow.objects.filter(    # Line 74-77: Check if following
            follower=request.user,
            following=profile_user
        ).exists()
        follows_me = Follow.objects.filter(      # Line 78-81: Check if followed by
            follower=profile_user,
            following=request.user
        ).exists()

    # Get user's posts (non-deleted)
    from posts.models import Post                # Line 84: Import Post model
    posts = Post.objects.filter(                 # Line 85-88: Get user's posts
        author=profile_user,
        deleted_at__isnull=True                  # Only non-deleted posts
    ).order_by('-created_at')                    # Newest first

    context = {                                  # Line 90-96: Context dictionary
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'is_following': is_following,
        'follows_me': follows_me,
        'posts': posts,
    }

    return render(request, 'accounts/profile.html', context)  # Line 98: Render template


@login_required                                  # Line 101: Require login
def edit_profile_view(request):                  # Line 102: Edit own profile
    """Edit own profile."""
    if request.method == 'POST':                 # Line 104: Form submitted
        user_form = UserUpdateForm(request.POST, instance=request.user)  # Line 105
        profile_form = ProfileForm(request.POST, instance=request.user.profile)  # Line 106

        if user_form.is_valid() and profile_form.is_valid():  # Line 108: Both valid?
            user_form.save()                     # Line 109: Save user changes
            profile_form.save()                  # Line 110: Save profile changes
            messages.success(request, 'تم تحديث ملفك الشخصي بنجاح.')  # Line 111
            return redirect('accounts:profile', username=request.user.username)  # Line 112
    else:                                        # Line 113: GET request
        user_form = UserUpdateForm(instance=request.user)  # Line 114: Pre-fill with current data
        profile_form = ProfileForm(instance=request.user.profile)  # Line 115

    return render(request, 'accounts/edit_profile.html', {  # Line 117-120
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required                                  # Line 123: Require login
@require_POST                                    # Line 124: POST only
def toggle_follow(request, username):            # Line 125: Toggle follow/unfollow
    """Toggle follow/unfollow a user. Returns HTMX partial."""
    target_user = get_object_or_404(User, username=username)  # Line 127: Get target user

    if target_user == request.user:              # Line 129: Trying to self-follow?
        return HttpResponse('لا يمكنك متابعة نفسك', status=400)  # Line 130: Error

    follow_exists = Follow.objects.filter(       # Line 132-135: Check existing follow
        follower=request.user,
        following=target_user
    ).exists()

    if follow_exists:                            # Line 137: Currently following?
        # Unfollow
        Follow.objects.filter(                   # Line 139-142: Delete follow
            follower=request.user,
            following=target_user
        ).delete()
        is_following = False                     # Line 143: Now not following
    else:                                        # Line 144: Not currently following
        # Follow
        Follow.objects.create(                   # Line 146-149: Create follow
            follower=request.user,
            following=target_user
        )
        is_following = True                      # Line 150: Now following

    # Check if they follow me (for follow back button)
    follows_me = Follow.objects.filter(          # Line 153-156: Check mutual
        follower=target_user,
        following=request.user
    ).exists()

    # Return updated button HTML for HTMX
    return render(request, 'accounts/partials/follow_button.html', {  # Line 159-163
        'profile_user': target_user,
        'is_following': is_following,
        'follows_me': follows_me,
    })


@login_required                                  # Line 166: Require login
def following_list(request):                     # Line 167: Show who user follows
    """Show list of users the current user follows."""
    following = Follow.objects.filter(           # Line 169-171
        follower=request.user
    ).select_related('following', 'following__profile').order_by('-created_at')
    # select_related: Eager load related objects to avoid N+1 queries

    return render(request, 'accounts/following_list.html', {  # Line 173-175
        'following': following,
    })


@login_required                                  # Line 178: Require login
def followers_list(request, username):           # Line 179: Show who follows user
    """Show list of users following a specific user."""
    profile_user = get_object_or_404(User, username=username)  # Line 181
    followers = Follow.objects.filter(           # Line 182-184
        following=profile_user
    ).select_related('follower', 'follower__profile').order_by('-created_at')

    return render(request, 'accounts/followers_list.html', {  # Line 186-189
        'profile_user': profile_user,
        'followers': followers,
    })
```

**View summary**:
- `signup_view`: Register new users, auto-login after signup
- `login_view`: Authenticate users, handle 'next' redirect
- `logout_view`: Log out and redirect to landing
- `profile_view`: Display user profile with posts and follow status
- `edit_profile_view`: Update username, email, bio
- `toggle_follow`: HTMX-powered follow/unfollow
- `following_list`: Who the current user follows
- `followers_list`: Who follows a specific user

---

## 4. accounts/forms.py

**Location**: `accounts/forms.py`
**Purpose**: Form classes for authentication and profiles

```python
"""
Forms for user registration and profile management.
"""

from django import forms                         # Line 5: Django forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm  # Line 6
from django.contrib.auth.models import User      # Line 7: User model
from .models import Profile                      # Line 8: Profile model


class SignUpForm(UserCreationForm):              # Line 11: Registration form
    """Form for user registration."""
    email = forms.EmailField(                    # Line 13-21: Email field
        required=True,
        label='البريد الإلكتروني',               # Arabic label
        widget=forms.EmailInput(attrs={
            'class': 'form-control',             # Bootstrap class
            'placeholder': 'example@email.com',
            'dir': 'ltr'                         # Left-to-right for email
        })
    )

    class Meta:                                  # Line 23-35: Form metadata
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'اسم المستخدم',          # Arabic label
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المستخدم',
                'dir': 'ltr'                     # LTR for username
            }),
        }

    def __init__(self, *args, **kwargs):         # Line 37-54: Customize password fields
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

    def clean_email(self):                       # Line 56-60: Email validation
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():  # Check uniqueness
            raise forms.ValidationError('هذا البريد الإلكتروني مستخدم بالفعل.')
        return email


class LoginForm(AuthenticationForm):             # Line 63-85: Login form
    """Form for user login."""
    username = forms.CharField(                  # Line 65-72: Username field
        label='اسم المستخدم',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اسم المستخدم',
            'dir': 'ltr'
        })
    )
    password = forms.CharField(                  # Line 73-80: Password field
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'كلمة المرور',
            'dir': 'ltr'
        })
    )

    error_messages = {                           # Line 82-85: Arabic error messages
        'invalid_login': 'اسم المستخدم أو كلمة المرور غير صحيحة.',
        'inactive': 'هذا الحساب غير مفعل.',
    }


class ProfileForm(forms.ModelForm):              # Line 88-99: Profile edit form
    """Form for editing user profile."""
    class Meta:
        model = Profile
        fields = ('bio',)                        # Only bio field
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'اكتب نبذة عنك...'
            })
        }


class UserUpdateForm(forms.ModelForm):           # Line 102-123: User update form
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
```

**Form purposes**:
- `SignUpForm`: Extends Django's UserCreationForm with email field and Arabic labels
- `LoginForm`: Extends AuthenticationForm with Arabic styling
- `ProfileForm`: Edit bio in Profile model
- `UserUpdateForm`: Edit username and email in User model

---

## 5. accounts/urls.py

**Location**: `accounts/urls.py`
**Purpose**: URL routing for accounts app

```python
"""
URL patterns for accounts app.
"""

from django.urls import path                     # Line 5: URL routing
from . import views                              # Line 6: Import views

app_name = 'accounts'                            # Line 8: Namespace for URL reversing

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),           # Line 11: Registration
    path('login/', views.login_view, name='login'),              # Line 12: Login
    path('logout/', views.logout_view, name='logout'),           # Line 13: Logout
    path('profile/<str:username>/', views.profile_view, name='profile'),  # Line 14: View profile
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),  # Line 15: Edit own profile
    path('follow/<str:username>/', views.toggle_follow, name='toggle_follow'),  # Line 16: Follow/unfollow
    path('following/', views.following_list, name='following_list'),  # Line 17: Following list
    path('followers/<str:username>/', views.followers_list, name='followers_list'),  # Line 18: Followers
]
```

**URL patterns**:
- `/accounts/signup/` - Registration page
- `/accounts/login/` - Login page
- `/accounts/logout/` - Logout action
- `/accounts/profile/<username>/` - View any user's profile
- `/accounts/profile/edit/` - Edit own profile
- `/accounts/follow/<username>/` - Toggle follow (HTMX)
- `/accounts/following/` - List of users you follow
- `/accounts/followers/<username>/` - List of user's followers

---

## 6. accounts/admin.py

**Location**: `accounts/admin.py`
**Purpose**: Django admin configuration for accounts

```python
"""
Admin configuration for accounts app.
"""

from django.contrib import admin                 # Line 5: Admin module
from .models import Profile, Follow              # Line 6: Models


@admin.register(Profile)                         # Line 9: Register with decorator
class ProfileAdmin(admin.ModelAdmin):            # Line 10: Profile admin config
    list_display = ('user', 'bio', 'created_at')  # Columns in list view
    search_fields = ('user__username', 'bio')    # Search by username or bio
    readonly_fields = ('created_at',)            # Non-editable field


@admin.register(Follow)                          # Line 16: Register Follow
class FollowAdmin(admin.ModelAdmin):             # Line 17: Follow admin config
    list_display = ('follower', 'following', 'created_at')  # Columns
    list_filter = ('created_at',)                # Filter sidebar
    search_fields = ('follower__username', 'following__username')  # Search
```

---

## 7. accounts/apps.py

**Location**: `accounts/apps.py`
**Purpose**: App configuration

```python
from django.apps import AppConfig                # Line 1: App config base


class AccountsConfig(AppConfig):                 # Line 4: App config class
    default_auto_field = 'django.db.models.BigAutoField'  # Line 5: Default PK type
    name = 'accounts'                            # Line 6: App name (matches directory)
    verbose_name = 'الحسابات'                    # Line 7: Arabic display name
```

---

## 8. accounts/migrations/0001_initial.py

**Location**: `accounts/migrations/0001_initial.py`
**Purpose**: Initial database migration

This migration file creates the database tables for Profile and Follow models:

```python
# Generated by Django 5.2.9 on 2025-12-31 00:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True                               # This is the initial migration

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),  # Depends on User model
    ]

    operations = [
        migrations.CreateModel(                  # Create Profile table
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, max_length=500, verbose_name='نبذة عني')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'الملف الشخصي',
                'verbose_name_plural': 'الملفات الشخصية',
            },
        ),
        migrations.CreateModel(                  # Create Follow table
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='المتابِع')),
                ('following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to=settings.AUTH_USER_MODEL, verbose_name='المتابَع')),
            ],
            options={
                'verbose_name': 'متابعة',
                'verbose_name_plural': 'المتابعات',
                'constraints': [models.CheckConstraint(condition=models.Q(('follower', models.F('following')), _negated=True), name='prevent_self_follow')],
                'unique_together': {('follower', 'following')},
            },
        ),
    ]
```

**Database tables created**:
1. `accounts_profile`:
   - `id` (BigAutoField, PK)
   - `bio` (TextField, max 500 chars)
   - `created_at` (DateTimeField)
   - `user_id` (FK to auth_user)

2. `accounts_follow`:
   - `id` (BigAutoField, PK)
   - `created_at` (DateTimeField)
   - `follower_id` (FK to auth_user)
   - `following_id` (FK to auth_user)
   - UNIQUE constraint on (follower_id, following_id)
   - CHECK constraint: follower_id != following_id

---

# STUDY APP

The study app handles AI-powered study set generation, flashcards, and quizzes.

## 1. study/models.py

**Location**: `study/models.py`
**Purpose**: Data models for study sets, flashcards, and quizzes

```python
"""
Models for study sets, flashcards, and quizzes.
"""

from django.db import models                     # Line 5: Django ORM
from django.contrib.auth.models import User      # Line 6: User model


class StudySet(models.Model):                    # Line 9: Study set model
    """
    A study set containing either flashcards or quiz questions.
    Generated by AI from user-provided text or PDF.
    """
    TYPE_CHOICES = [                             # Line 14-17: Set type options
        ('flashcards', 'بطاقات تعليمية'),        # Flashcards option
        ('quiz', 'اختبار'),                      # Quiz option
    ]

    LANGUAGE_CHOICES = [                         # Line 19-22: Language options
        ('ar', 'العربية'),                       # Arabic
        ('en', 'English'),                       # English
    ]

    owner = models.ForeignKey(                   # Line 24-28: Owner relationship
        User,
        on_delete=models.CASCADE,                # Delete sets when user deleted
        related_name='study_sets',               # user.study_sets
        verbose_name='المالك'
    )
    set_type = models.CharField(                 # Line 29-33: Type field
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='نوع المجموعة'
    )
    language = models.CharField(                 # Line 34-38: Language field
        max_length=2,
        choices=LANGUAGE_CHOICES,
        verbose_name='اللغة'
    )
    title = models.CharField(                    # Line 39-43: Title field
        max_length=200,
        blank=True,                              # Optional
        verbose_name='العنوان'
    )
    source_text = models.TextField(              # Line 44-47: Original text
        verbose_name='النص المصدر',
        help_text='النص الأصلي المستخدم لإنشاء المجموعة'
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Line 48

    class Meta:                                  # Line 50-53: Model metadata
        verbose_name = 'مجموعة دراسية'
        verbose_name_plural = 'المجموعات الدراسية'
        ordering = ['-created_at']               # Newest first

    def __str__(self):                           # Line 55-56: String representation
        return f'{self.get_set_type_display()} - {self.title or "بدون عنوان"}'

    @property                                    # Line 58-63: Item count property
    def item_count(self):
        """Number of items (flashcards or questions) in this set."""
        if self.set_type == 'flashcards':
            return self.flashcards.count()       # Count related flashcards
        return self.questions.count()            # Count related questions

    @property                                    # Line 65-68: Shared status property
    def is_shared(self):
        """Check if this study set has been shared in any post."""
        return self.posts.filter(deleted_at__isnull=True).exists()


class Flashcard(models.Model):                   # Line 71: Flashcard model
    """A single flashcard with question and answer."""
    study_set = models.ForeignKey(               # Line 73-76: Parent relationship
        StudySet,
        on_delete=models.CASCADE,                # Delete cards when set deleted
        related_name='flashcards'                # study_set.flashcards
    )
    index = models.PositiveIntegerField(verbose_name='الترتيب')  # Line 77: Order
    question = models.TextField(verbose_name='السؤال')           # Line 78: Question
    answer = models.TextField(verbose_name='الإجابة')            # Line 79: Answer

    class Meta:                                  # Line 81-85: Metadata
        verbose_name = 'بطاقة تعليمية'
        verbose_name_plural = 'البطاقات التعليمية'
        ordering = ['index']                     # Order by index
        unique_together = ('study_set', 'index') # Unique index per set

    def __str__(self):                           # Line 87-88: String representation
        return f'بطاقة {self.index + 1}: {self.question[:50]}'


class QuizQuestion(models.Model):                # Line 91: Quiz question model
    """A single quiz question with multiple choice options."""
    study_set = models.ForeignKey(               # Line 93-96: Parent relationship
        StudySet,
        on_delete=models.CASCADE,
        related_name='questions'                 # study_set.questions
    )
    index = models.PositiveIntegerField(verbose_name='الترتيب')  # Line 97: Order
    question = models.TextField(verbose_name='السؤال')           # Line 98: Question
    options = models.JSONField(                  # Line 99-102: Choices as JSON array
        verbose_name='الخيارات',
        help_text='قائمة من 4 خيارات'
    )
    correct_index = models.PositiveSmallIntegerField(  # Line 103-106: Correct answer index
        verbose_name='رقم الإجابة الصحيحة',
        help_text='0-3'                          # 0-based index
    )
    explanation = models.TextField(              # Line 107-110: Explanation
        verbose_name='الشرح',
        help_text='شرح للإجابة الصحيحة والخاطئة'
    )

    class Meta:                                  # Line 112-116: Metadata
        verbose_name = 'سؤال اختبار'
        verbose_name_plural = 'أسئلة الاختبار'
        ordering = ['index']
        unique_together = ('study_set', 'index')

    def __str__(self):                           # Line 118-119: String representation
        return f'سؤال {self.index + 1}: {self.question[:50]}'

    @property                                    # Line 121-125: Correct answer text
    def correct_answer(self):
        """Get the correct answer text."""
        if 0 <= self.correct_index < len(self.options):
            return self.options[self.correct_index]
        return None
```

**Model relationships**:
- `StudySet` belongs to `User` (ForeignKey)
- `Flashcard` belongs to `StudySet` (ForeignKey)
- `QuizQuestion` belongs to `StudySet` (ForeignKey)

---

## 2. study/ai_service.py

**Location**: `study/ai_service.py`
**Purpose**: AI integration with DeepSeek API

```python
"""
AI service for generating flashcards and quizzes using DeepSeek API.
"""

import json                                      # Line 5: JSON parsing
import re                                        # Line 6: Regular expressions
from openai import OpenAI                        # Line 7: OpenAI client (DeepSeek compatible)
from django.conf import settings                 # Line 8: Django settings


def detect_language(text):                       # Line 11: Language detection
    """
    Detect if text is primarily Arabic or English.
    Returns 'ar' for Arabic, 'en' for English.
    """
    # Count Arabic characters (Arabic Unicode range)
    arabic_chars = len(re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', text))
    # Line 17: Regex matches Arabic Unicode characters

    # Count English/Latin characters
    english_chars = len(re.findall(r'[a-zA-Z]', text))  # Line 20: Count English letters

    if arabic_chars > english_chars:             # Line 22-23: Compare counts
        return 'ar'
    return 'en'


def get_deepseek_client():                       # Line 26: Get API client
    """Get configured DeepSeek client."""
    return OpenAI(                               # Line 28-31: Create OpenAI client
        api_key=settings.DEEPSEEK_API_KEY,       # From settings (from .env)
        base_url=settings.DEEPSEEK_BASE_URL      # DeepSeek's API URL
    )


def clean_json_response(response_text):          # Line 34: Clean AI response
    """
    Clean AI response to extract valid JSON.
    Sometimes AI wraps JSON in markdown code blocks.
    """
    cleaned = response_text.strip()              # Line 39: Remove whitespace

    # Remove ```json or ``` wrapper
    if cleaned.startswith('```'):                # Line 42: Check for code block
        first_newline = cleaned.find('\n')       # Line 44: Find first newline
        if first_newline != -1:
            cleaned = cleaned[first_newline + 1:]  # Line 46: Skip first line
        if cleaned.endswith('```'):              # Line 48: Remove trailing ```
            cleaned = cleaned[:-3]

    return cleaned.strip()                       # Line 51: Return cleaned JSON


def generate_flashcards(text, count=10):         # Line 54: Generate flashcards
    """
    Generate flashcards from the provided text using DeepSeek.

    Args:
        text: Source text to generate flashcards from
        count: Number of flashcards to generate (default 10)

    Returns:
        dict with 'success', 'language', 'flashcards' or 'error'
    """
    language = detect_language(text)             # Line 65: Detect text language

    if language == 'ar':                         # Line 67: Arabic prompts
        system_prompt = """أنت مساعد تعليمي متخصص في إنشاء بطاقات تعليمية.
قواعد مهمة:
1. استخدم فقط المعلومات الموجودة في النص المقدم
2. إذا لم تكن المعلومة موجودة في النص، اكتب "غير مذكور في النص"
3. اجعل الأسئلة واضحة ومباشرة
4. اجعل الإجابات موجزة ودقيقة
5. أرجع JSON فقط بدون أي نص إضافي"""

        user_prompt = f"""أنشئ {count} بطاقة تعليمية من النص التالي.

النص:
{text}

أرجع JSON بالتنسيق التالي فقط:
{{"flashcards": [{{"question": "السؤال", "answer": "الإجابة"}}]}}"""

    else:                                        # Line 84: English prompts
        system_prompt = """You are an educational assistant specialized in creating flashcards.
Important rules:
1. Use ONLY information from the provided text
2. If information is not stated in the text, write "Not stated in the text"
3. Make questions clear and direct
4. Keep answers concise and accurate
5. Return JSON only without any additional text"""

        user_prompt = f"""Create {count} flashcards from the following text.

Text:
{text}

Return JSON in this format only:
{{"flashcards": [{{"question": "Question here", "answer": "Answer here"}}]}}"""

    try:                                         # Line 100: Try API call
        client = get_deepseek_client()           # Line 101: Get client

        response = client.chat.completions.create(  # Line 103-111: API call
            model="deepseek-chat",               # Model name
            messages=[
                {"role": "system", "content": system_prompt},  # System instructions
                {"role": "user", "content": user_prompt}       # User request
            ],
            temperature=0.3,                     # Low temperature for consistency
            max_tokens=4000                      # Max response length
        )

        response_text = response.choices[0].message.content  # Line 113: Get response
        cleaned_json = clean_json_response(response_text)    # Line 114: Clean JSON

        data = json.loads(cleaned_json)          # Line 117: Parse JSON

        # Validate structure
        if 'flashcards' not in data:             # Line 120-121: Check key exists
            raise ValueError("Missing 'flashcards' key in response")

        flashcards = data['flashcards']          # Line 123: Get flashcards
        if not isinstance(flashcards, list):     # Line 124-125: Check type
            raise ValueError("'flashcards' must be a list")

        # Validate each flashcard
        for i, card in enumerate(flashcards):    # Line 128-130: Validate items
            if 'question' not in card or 'answer' not in card:
                raise ValueError(f"Flashcard {i} missing question or answer")

        return {                                 # Line 132-136: Return success
            'success': True,
            'language': language,
            'flashcards': flashcards
        }

    except json.JSONDecodeError as e:            # Line 138-142: JSON error
        return {
            'success': False,
            'error': f'خطأ في تحليل الرد: {str(e)}' if language == 'ar' else f'JSON parsing error: {str(e)}'
        }
    except Exception as e:                       # Line 143-147: Other errors
        return {
            'success': False,
            'error': f'خطأ في الاتصال بالخدمة: {str(e)}' if language == 'ar' else f'Service error: {str(e)}'
        }


def generate_quiz(text, count=10):               # Line 150: Generate quiz
    """
    Generate quiz questions from the provided text using DeepSeek.
    """
    language = detect_language(text)             # Line 163: Detect language

    # Similar structure to generate_flashcards, but with quiz-specific prompts
    # Prompts ask for multiple choice questions with 4 options and explanations

    # ... (Similar to flashcards but for quiz questions)

    # Returns: {'success': True, 'language': 'ar'/'en', 'questions': [...]}


def extract_text_from_pdf(pdf_file):             # Line 267: PDF extraction
    """
    Extract text content from a PDF file.

    Args:
        pdf_file: Django uploaded file object

    Returns:
        dict with 'success' and 'text' or 'error'
    """
    try:                                         # Line 278: Try extraction
        from pypdf import PdfReader              # Line 279: Import PDF library

        reader = PdfReader(pdf_file)             # Line 281: Create reader
        text_parts = []                          # Line 282: Store pages

        for page in reader.pages:                # Line 284-287: Iterate pages
            page_text = page.extract_text()      # Extract text from page
            if page_text:
                text_parts.append(page_text)

        full_text = '\n'.join(text_parts).strip()  # Line 289: Join pages

        if not full_text:                        # Line 291-296: Check for OCR PDF
            return {
                'success': False,
                'error': 'لا يمكن استخراج نص من هذا الملف. يبدو أنه ملف PDF ممسوح ضوئياً (صور). يرجى استخدام ملف PDF يحتوي على نص قابل للنسخ.',
                'is_ocr': True
            }

        if len(full_text) < 50:                  # Line 299-304: Check text length
            return {
                'success': False,
                'error': 'النص المستخرج قصير جداً (أقل من 50 حرف). قد يكون الملف ممسوحاً ضوئياً أو تالفاً. يرجى استخدام ملف PDF آخر.',
                'is_ocr': True
            }

        return {                                 # Line 306-310: Return success
            'success': True,
            'text': full_text,
            'char_count': len(full_text)
        }

    except Exception as e:                       # Line 312-315: Handle errors
        return {
            'success': False,
            'error': f'خطأ في قراءة الملف: {str(e)}'
        }
```

**AI service functions**:
- `detect_language`: Determines if text is Arabic or English by counting characters
- `get_deepseek_client`: Creates OpenAI-compatible client for DeepSeek API
- `clean_json_response`: Removes markdown code blocks from AI response
- `generate_flashcards`: Generates Q&A pairs from text using AI
- `generate_quiz`: Generates multiple-choice questions using AI
- `extract_text_from_pdf`: Extracts text from PDF files

---

## 3. study/views.py

**Location**: `study/views.py`
**Purpose**: View functions for study set operations

```python
"""
Views for study set generation and viewing.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse

from .models import StudySet, Flashcard, QuizQuestion
from .forms import GenerateStudySetForm
from .ai_service import generate_flashcards, generate_quiz, extract_text_from_pdf


@login_required
def generate_view(request, set_type):            # Line 16: Generate study set
    """
    Generate a new study set (flashcards or quiz).
    set_type: 'flashcards' or 'quiz'
    """
    if set_type not in ['flashcards', 'quiz']:   # Line 21: Validate type
        return redirect('home')

    if request.method == 'POST':                 # Line 24: Form submitted
        form = GenerateStudySetForm(request.POST, request.FILES)  # Line 25: Handle files

        if form.is_valid():                      # Line 27: Validate form
            input_type = form.cleaned_data['input_type']  # Line 28: text or pdf
            count = form.cleaned_data['count']   # Line 29: Number of items
            title = form.cleaned_data['title']   # Line 30: Optional title

            # Get text content
            if input_type == 'pdf':              # Line 33: PDF input
                pdf_result = extract_text_from_pdf(request.FILES['pdf_file'])  # Line 34
                if not pdf_result['success']:    # Line 35-40: Handle error
                    messages.error(request, pdf_result['error'])
                    return render(request, 'study/generate.html', {
                        'form': form,
                        'set_type': set_type
                    })
                text = pdf_result['text']        # Line 41: Get extracted text
            else:                                # Line 42: Text input
                text = form.cleaned_data['text_content']  # Line 43

            # Generate content using AI
            if set_type == 'flashcards':         # Line 46-49: Call appropriate AI function
                result = generate_flashcards(text, count)
            else:
                result = generate_quiz(text, count)

            if not result['success']:            # Line 51-56: Handle AI error
                messages.error(request, result['error'])
                return render(request, 'study/generate.html', {
                    'form': form,
                    'set_type': set_type
                })

            # Create StudySet
            study_set = StudySet.objects.create(  # Line 59-65: Save to database
                owner=request.user,
                set_type=set_type,
                language=result['language'],      # Detected language
                title=title,
                source_text=text[:5000]           # Limit stored text to 5000 chars
            )

            # Create items
            if set_type == 'flashcards':         # Line 68-76: Create flashcards
                for i, card in enumerate(result['flashcards']):
                    Flashcard.objects.create(
                        study_set=study_set,
                        index=i,
                        question=card['question'],
                        answer=card['answer']
                    )
            else:                                # Line 77-85: Create questions
                for i, q in enumerate(result['questions']):
                    QuizQuestion.objects.create(
                        study_set=study_set,
                        index=i,
                        question=q['question'],
                        options=q['options'],
                        correct_index=q['correctIndex'],
                        explanation=q['explanation']
                    )

            messages.success(request, 'تم إنشاء المجموعة بنجاح!')  # Line 87
            return redirect('study:detail', pk=study_set.pk)       # Line 88

    else:                                        # Line 90: GET request
        form = GenerateStudySetForm(initial={'set_type': set_type})

    return render(request, 'study/generate.html', {  # Line 93-96
        'form': form,
        'set_type': set_type
    })


@login_required
def study_set_detail(request, pk):               # Line 100: View study set
    """View a study set (flashcards or quiz)."""
    study_set = get_object_or_404(StudySet, pk=pk)  # Line 102

    # Check access: owner can always view, others only if shared
    if study_set.owner != request.user:          # Line 105: Not owner?
        if not study_set.is_shared:              # Line 106: Not shared?
            return HttpResponseForbidden('ليس لديك صلاحية لعرض هذه المجموعة.')

    context = {                                  # Line 109-112
        'study_set': study_set,
        'is_owner': study_set.owner == request.user,
    }

    if study_set.set_type == 'flashcards':       # Line 114-118: Render appropriate template
        context['flashcards'] = study_set.flashcards.all()
        return render(request, 'study/flashcards_view.html', context)
    else:
        context['questions'] = study_set.questions.all()
        return render(request, 'study/quiz_view.html', context)


@login_required
def history_view(request):                       # Line 122: View history
    """View user's study set history."""
    study_sets = StudySet.objects.filter(        # Line 124-126
        owner=request.user
    ).order_by('-created_at')

    # Filter by type if specified
    set_type = request.GET.get('type')           # Line 129: Get filter param
    if set_type in ['flashcards', 'quiz']:       # Line 130-131
        study_sets = study_sets.filter(set_type=set_type)

    return render(request, 'study/history.html', {  # Line 133-136
        'study_sets': study_sets,
        'current_type': set_type,
    })


@login_required
def delete_study_set(request, pk):               # Line 140: Delete study set
    """Delete a study set."""
    study_set = get_object_or_404(StudySet, pk=pk, owner=request.user)  # Line 142

    if request.method == 'POST':                 # Line 144-147: Confirm delete
        study_set.delete()
        messages.success(request, 'تم حذف المجموعة بنجاح.')
        return redirect('study:history')

    return render(request, 'study/confirm_delete.html', {  # Line 149-151
        'study_set': study_set
    })


@login_required
def study_set_json(request, pk):                 # Line 155: JSON API
    """Return study set data as JSON (for HTMX picker)."""
    study_set = get_object_or_404(StudySet, pk=pk, owner=request.user)

    data = {                                     # Line 159-168: Build JSON
        'id': study_set.pk,
        'type': study_set.set_type,
        'type_display': study_set.get_set_type_display(),
        'language': study_set.language,
        'title': study_set.title or 'بدون عنوان',
        'item_count': study_set.item_count,
        'created_at': study_set.created_at.strftime('%Y-%m-%d'),
        'is_shared': study_set.is_shared,
    }

    # Add preview
    if study_set.set_type == 'flashcards':       # Line 171-178
        first_card = study_set.flashcards.first()
        if first_card:
            data['preview'] = first_card.question[:100]
    else:
        first_q = study_set.questions.first()
        if first_q:
            data['preview'] = first_q.question[:100]

    return JsonResponse(data)                    # Line 180: Return JSON
```

---

## 4. study/forms.py

**Location**: `study/forms.py`
**Purpose**: Form for study set generation

```python
"""
Forms for study set generation.
"""

from django import forms


class GenerateStudySetForm(forms.Form):          # Line 8: Generation form
    """Form for generating flashcards or quizzes."""

    TYPE_CHOICES = [                             # Line 11-14: Set type choices
        ('flashcards', 'بطاقات تعليمية'),
        ('quiz', 'اختبار'),
    ]

    INPUT_CHOICES = [                            # Line 16-19: Input type choices
        ('text', 'نص'),
        ('pdf', 'ملف PDF'),
    ]

    set_type = forms.ChoiceField(                # Line 21-25: Set type field
        choices=TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='نوع المجموعة'
    )

    input_type = forms.ChoiceField(              # Line 27-32: Input type field
        choices=INPUT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='text',
        label='نوع المدخل'
    )

    text_content = forms.CharField(              # Line 34-42: Text input field
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'الصق النص هنا...'
        }),
        label='النص'
    )

    pdf_file = forms.FileField(                  # Line 44-51: PDF upload field
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf'
        }),
        label='ملف PDF'
    )

    count = forms.IntegerField(                  # Line 53-62: Item count field
        min_value=1,
        max_value=30,
        initial=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'style': 'width: 100px;'
        }),
        label='عدد العناصر'
    )

    title = forms.CharField(                     # Line 64-72: Title field
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'عنوان اختياري للمجموعة'
        }),
        label='العنوان (اختياري)'
    )

    def clean(self):                             # Line 74-99: Custom validation
        cleaned_data = super().clean()
        input_type = cleaned_data.get('input_type')
        text_content = cleaned_data.get('text_content')
        pdf_file = cleaned_data.get('pdf_file')

        if input_type == 'text':                 # Line 80-84: Text validation
            if not text_content or len(text_content.strip()) < 50:
                raise forms.ValidationError(
                    'يرجى إدخال نص لا يقل عن 50 حرفاً.'
                )
        elif input_type == 'pdf':                # Line 85-99: PDF validation
            if not pdf_file:
                raise forms.ValidationError(
                    'يرجى رفع ملف PDF.'
                )
            if not pdf_file.name.lower().endswith('.pdf'):
                raise forms.ValidationError(
                    'يرجى رفع ملف بصيغة PDF فقط.'
                )
            if pdf_file.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError(
                    'حجم الملف يجب أن لا يتجاوز 10 ميجابايت.'
                )

        return cleaned_data
```

---

## 5. study/urls.py

**Location**: `study/urls.py`
**Purpose**: URL routing for study app

```python
"""
URL patterns for study app.
"""

from django.urls import path
from . import views

app_name = 'study'                               # Line 8: Namespace

urlpatterns = [
    path('generate/<str:set_type>/', views.generate_view, name='generate'),  # Line 11
    path('history/', views.history_view, name='history'),                     # Line 12
    path('<int:pk>/', views.study_set_detail, name='detail'),                 # Line 13
    path('<int:pk>/delete/', views.delete_study_set, name='delete'),          # Line 14
    path('<int:pk>/json/', views.study_set_json, name='json'),                # Line 15
]
```

**URL patterns**:
- `/study/generate/flashcards/` - Generate flashcards
- `/study/generate/quiz/` - Generate quiz
- `/study/history/` - View history
- `/study/123/` - View study set #123
- `/study/123/delete/` - Delete study set #123
- `/study/123/json/` - Get study set #123 as JSON

---

# POSTS APP

The posts app handles content sharing, social interactions, and feed functionality.

## 1. posts/models.py

**Location**: `posts/models.py`
**Purpose**: Models for posts, tags, reactions, and comments

```python
"""
Models for posts, tags, reactions, and comments.
"""

from django.db import models
from django.contrib.auth.models import User
from study.models import StudySet


class Tag(models.Model):                         # Line 10: Tag model
    """Tag for categorizing posts."""
    name = models.CharField(max_length=50, unique=True, verbose_name='اسم التصنيف')
    color = models.CharField(max_length=7, default='#94a3b8', verbose_name='اللون')
    # Color is hex code for UI display

    class Meta:
        verbose_name = 'تصنيف'
        verbose_name_plural = 'التصنيفات'
        ordering = ['name']

    def __str__(self):
        return self.name


class Post(models.Model):                        # Line 27: Post model
    """A post sharing a study set."""
    author = models.ForeignKey(                  # Line 29-34: Author relationship
        User,
        on_delete=models.CASCADE,
        related_name='posts',                    # user.posts
        verbose_name='الكاتب'
    )
    study_set = models.ForeignKey(               # Line 35-40: Study set relationship
        StudySet,
        on_delete=models.CASCADE,
        related_name='posts',                    # study_set.posts
        verbose_name='المجموعة الدراسية'
    )
    title = models.CharField(max_length=200, verbose_name='العنوان')
    caption = models.TextField(blank=True, null=True, verbose_name='وصف قصير')
    tags = models.ManyToManyField(               # Line 45-50: Tags (through PostTag)
        Tag,
        through='PostTag',                       # Explicit through model
        related_name='posts',
        verbose_name='الوسوم'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # Soft delete

    class Meta:
        verbose_name = 'منشور'
        verbose_name_plural = 'المنشورات'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property                                    # Line 67-68: Check if deleted
    def is_deleted(self):
        return self.deleted_at is not None

    @property                                    # Line 71-73: Like count
    def likes_count(self):
        return self.reactions.filter(value='like').count()

    @property                                    # Line 75-77: Dislike count
    def dislikes_count(self):
        return self.reactions.filter(value='dislike').count()

    def get_user_reaction(self, user):           # Line 79-84: Get user's reaction
        """Get user's reaction to this post, if any."""
        if not user.is_authenticated:
            return None
        reaction = self.reactions.filter(user=user).first()
        return reaction.value if reaction else None


class PostTag(models.Model):                     # Line 87-93: Through model for Post-Tag
    """Through model for Post-Tag relationship."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'tag')        # Prevent duplicate tags on post


class Reaction(models.Model):                    # Line 96: Reaction model
    """User reaction to a post (like or dislike)."""
    VALUE_CHOICES = [
        ('like', 'إعجاب'),
        ('dislike', 'عدم إعجاب'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    value = models.CharField(max_length=10, choices=VALUE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'تفاعل'
        verbose_name_plural = 'التفاعلات'
        unique_together = ('user', 'post')       # One reaction per user per post


class Comment(models.Model):                     # Line 125: Comment model
    """Simple comment on a post."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField(verbose_name='التعليق')
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # Soft delete

    class Meta:
        verbose_name = 'تعليق'
        verbose_name_plural = 'التعليقات'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username}: {self.body[:30]}'

    @property
    def is_deleted(self):
        return self.deleted_at is not None
```

**Soft delete pattern**: Posts and comments use `deleted_at` field instead of actual deletion. This allows recovery and maintains data integrity.

---

## 2. posts/views.py

**Location**: `posts/views.py`
**Purpose**: Views for post creation, viewing, reactions, and comments

```python
"""
Views for posts, reactions, and comments.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Post, Tag, Reaction, Comment
from .forms import PostForm, CommentForm
from study.models import StudySet


@login_required
def create_post(request):                        # Line 18: Create new post
    """Create a new post sharing a study set."""
    # Get user's study sets that can be shared
    study_sets = StudySet.objects.filter(owner=request.user).order_by('-created_at')
    all_tags = Tag.objects.all()                 # Line 22: Get all available tags

    # Check for preselected study set from URL parameter
    preselected_study_set = None
    study_set_id = request.GET.get('study_set')  # Line 26: Get from query string
    if study_set_id:
        preselected_study_set = StudySet.objects.filter(
            pk=study_set_id, owner=request.user
        ).first()

    if request.method == 'POST':                 # Line 32: Form submitted
        form = PostForm(request.POST)
        if form.is_valid():
            study_set_id = request.POST.get('study_set')  # Line 35: Get selected set
            study_set = get_object_or_404(StudySet, pk=study_set_id, owner=request.user)

            # Create post
            post = Post.objects.create(          # Line 39-43: Create post record
                author=request.user,
                study_set=study_set,
                title=form.cleaned_data['title'],
                caption=form.cleaned_data.get('caption', '')
            )

            # Add tags
            tag_ids = request.POST.getlist('tags')  # Line 47: Get selected tag IDs
            for tag_id in tag_ids[:4]:           # Max 4 tags
                try:
                    tag = Tag.objects.get(pk=tag_id)
                    post.tags.add(tag)           # Line 51: Add tag to post
                except Tag.DoesNotExist:
                    pass

            messages.success(request, 'تم نشر المنشور بنجاح!')
            return redirect('posts:detail', pk=post.pk)
    else:
        form = PostForm()

    return render(request, 'posts/create.html', {  # Line 60-65
        'form': form,
        'study_sets': study_sets,
        'all_tags': all_tags,
        'preselected_study_set': preselected_study_set,
    })


@login_required
def post_detail(request, pk):                    # Line 69: View single post
    """View a single post with comments."""
    post = get_object_or_404(Post, pk=pk, deleted_at__isnull=True)  # Only non-deleted
    is_owner = request.user == post.author       # Line 72: Check ownership

    # Get comments (non-deleted)
    comments = post.comments.filter(deleted_at__isnull=True).order_by('-created_at')

    # Handle comment submission
    if request.method == 'POST':                 # Line 78: Comment submitted
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            Comment.objects.create(              # Line 81-85: Create comment
                post=post,
                author=request.user,
                body=comment_form.cleaned_data['body']
            )
            return redirect('posts:detail', pk=pk)  # Refresh page
    else:
        comment_form = CommentForm()

    # Get user's reaction to this post
    user_reaction = post.get_user_reaction(request.user)  # Line 92

    return render(request, 'posts/detail.html', {  # Line 94-100
        'post': post,
        'is_owner': is_owner,
        'comments': comments,
        'comment_form': comment_form,
        'user_reaction': user_reaction,
    })


@login_required
@require_POST
def react_to_post(request, pk):                  # Line 104: Like/dislike post
    """Handle like/dislike reactions via HTMX."""
    post = get_object_or_404(Post, pk=pk, deleted_at__isnull=True)
    reaction_type = request.POST.get('type')     # Line 107: 'like' or 'dislike'

    if reaction_type not in ['like', 'dislike']:
        return HttpResponse('Invalid reaction', status=400)

    # Check for existing reaction
    existing = Reaction.objects.filter(user=request.user, post=post).first()

    if existing:                                 # Line 114: User already reacted
        if existing.value == reaction_type:      # Same reaction = remove it
            existing.delete()
        else:                                    # Different reaction = change it
            existing.value = reaction_type
            existing.save()
    else:                                        # Line 120: New reaction
        Reaction.objects.create(
            user=request.user,
            post=post,
            value=reaction_type
        )

    # Return updated buttons partial for HTMX
    user_reaction = post.get_user_reaction(request.user)
    return render(request, 'posts/partials/reaction_buttons.html', {
        'post': post,
        'user_reaction': user_reaction,
    })


@login_required
@require_POST
def delete_post(request, pk):                    # Line 136: Delete post
    """Soft delete a post (owner only)."""
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.deleted_at = timezone.now()             # Soft delete
    post.save()
    messages.success(request, 'تم حذف المنشور.')
    return redirect('home')


@login_required
@require_POST
def delete_comment(request, pk):                 # Line 147: Delete comment
    """Soft delete a comment (author only). Returns empty for HTMX."""
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    comment.deleted_at = timezone.now()          # Soft delete
    comment.save()
    return HttpResponse('')                      # Empty response removes element


def search_posts(request):                       # Line 155: Search posts
    """Search posts by title, caption, or tags."""
    query = request.GET.get('q', '').strip()
    tag_filter = request.GET.getlist('tags')     # Line 158: Get tag filters

    posts = Post.objects.filter(deleted_at__isnull=True)  # Only non-deleted

    if query:                                    # Line 161: Text search
        posts = posts.filter(
            models.Q(title__icontains=query) |
            models.Q(caption__icontains=query)
        )

    if tag_filter:                               # Line 166: Tag filter
        posts = posts.filter(tags__name__in=tag_filter).distinct()

    posts = posts.order_by('-created_at')        # Line 169: Order by newest

    return render(request, 'posts/search.html', {
        'posts': posts,
        'query': query,
        'tag_filter': tag_filter,
        'all_tags': Tag.objects.all(),
    })
```

---

## 3. posts/feed_views.py

**Location**: `posts/feed_views.py`
**Purpose**: Feed views for recent and following posts

```python
"""
Feed views for browsing posts.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Post, Tag
from accounts.models import Follow


@login_required
def recent_feed(request):                        # Line 13: Recent posts feed
    """Show all recent posts (public feed)."""
    query = request.GET.get('q', '').strip()
    tag_filter = request.GET.getlist('tags')

    posts = Post.objects.filter(deleted_at__isnull=True)  # Non-deleted only

    if query:                                    # Text search
        posts = posts.filter(
            models.Q(title__icontains=query) |
            models.Q(caption__icontains=query)
        )

    if tag_filter:                               # Tag filter
        posts = posts.filter(tags__name__in=tag_filter).distinct()

    posts = posts.order_by('-created_at')[:50]   # Limit to 50 posts

    return render(request, 'posts/feed.html', {
        'posts': posts,
        'feed_type': 'recent',
        'query': query,
        'tag_filter': tag_filter,
        'all_tags': Tag.objects.all(),
    })


@login_required
def following_feed(request):                     # Line 43: Following feed
    """Show posts from users the current user follows."""
    # Get IDs of users being followed
    following_ids = Follow.objects.filter(
        follower=request.user
    ).values_list('following_id', flat=True)     # Line 48: Get followed user IDs

    posts = Post.objects.filter(
        author_id__in=following_ids,             # Filter by followed authors
        deleted_at__isnull=True
    ).order_by('-created_at')[:50]

    following_count = len(following_ids)         # Line 55: Count for empty state

    return render(request, 'posts/feed.html', {
        'posts': posts,
        'feed_type': 'following',
        'following_count': following_count,
        'all_tags': Tag.objects.all(),
    })
```

---

## 4. posts/forms.py

**Location**: `posts/forms.py`
**Purpose**: Forms for posts and comments

```python
"""
Forms for posts and comments.
"""

from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):                 # Line 9: Post creation form
    """Form for creating a new post."""
    class Meta:
        model = Post
        fields = ['title', 'caption']
        labels = {
            'title': 'عنوان المنشور',
            'caption': 'وصف (اختياري)',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان المنشور'
            }),
            'caption': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أضف وصفاً للمنشور...'
            }),
        }


class CommentForm(forms.ModelForm):              # Line 32: Comment form
    """Form for adding a comment."""
    class Meta:
        model = Comment
        fields = ['body']
        labels = {
            'body': '',                          # No label
        }
        widgets = {
            'body': forms.TextInput(attrs={      # Single line input
                'class': 'form-control',
                'placeholder': 'اكتب تعليقاً...'
            }),
        }
```

---

## 5. posts/urls.py

**Location**: `posts/urls.py`
**Purpose**: URL patterns for posts app

```python
"""
URL patterns for posts app.
"""

from django.urls import path
from . import views

app_name = 'posts'                               # Namespace

urlpatterns = [
    path('new/', views.create_post, name='create'),           # Create post
    path('<int:pk>/', views.post_detail, name='detail'),      # View post
    path('<int:pk>/react/', views.react_to_post, name='react'), # Like/dislike
    path('<int:pk>/delete/', views.delete_post, name='delete'), # Delete post
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('search/', views.search_posts, name='search'),       # Search
]
```

---

## 6. posts/feed_urls.py

**Location**: `posts/feed_urls.py`
**Purpose**: URL patterns for feed views

```python
"""
URL patterns for feed views.
"""

from django.urls import path
from . import feed_views

app_name = 'feed'                                # Namespace

urlpatterns = [
    path('recent/', feed_views.recent_feed, name='recent'),       # All posts
    path('following/', feed_views.following_feed, name='following'), # Following only
]
```

---

## 7. posts/admin.py

**Location**: `posts/admin.py`
**Purpose**: Django admin configuration for posts

```python
from django.contrib import admin
from .models import Post, Tag, Reaction, Comment, PostTag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'study_set', 'created_at', 'deleted_at')
    list_filter = ('created_at', 'deleted_at', 'tags')
    search_fields = ('title', 'caption', 'author__username')
    raw_id_fields = ('author', 'study_set')      # Performance for large datasets


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'value', 'created_at')
    list_filter = ('value', 'created_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'body_preview', 'created_at', 'deleted_at')
    list_filter = ('created_at', 'deleted_at')
    search_fields = ('body', 'author__username')

    def body_preview(self, obj):                 # Show truncated body
        return obj.body[:50] + '...' if len(obj.body) > 50 else obj.body
    body_preview.short_description = 'التعليق'
```

---

## 8. posts/management/commands/seed_tags.py

**Location**: `posts/management/commands/seed_tags.py`
**Purpose**: Django management command to seed default tags

```python
"""
Management command to seed default tags.
Run with: python manage.py seed_tags
"""

from django.core.management.base import BaseCommand
from posts.models import Tag


class Command(BaseCommand):
    help = 'Seed default tags for posts'

    def handle(self, *args, **options):
        tags_data = [                            # Default tags with colors
            {'name': 'رياضيات', 'color': '#ef4444'},       # Red
            {'name': 'فيزياء', 'color': '#f97316'},        # Orange
            {'name': 'كيمياء', 'color': '#eab308'},        # Yellow
            {'name': 'أحياء', 'color': '#22c55e'},         # Green
            {'name': 'تاريخ', 'color': '#14b8a6'},         # Teal
            {'name': 'جغرافيا', 'color': '#06b6d4'},       # Cyan
            {'name': 'لغة عربية', 'color': '#3b82f6'},     # Blue
            {'name': 'لغة إنجليزية', 'color': '#8b5cf6'},  # Violet
            {'name': 'علوم', 'color': '#d946ef'},          # Fuchsia
            {'name': 'دين', 'color': '#ec4899'},           # Pink
            {'name': 'برمجة', 'color': '#6366f1'},         # Indigo
            {'name': 'طب', 'color': '#10b981'},            # Emerald
            {'name': 'هندسة', 'color': '#f59e0b'},         # Amber
            {'name': 'اقتصاد', 'color': '#84cc16'},        # Lime
            {'name': 'أخرى', 'color': '#94a3b8'},          # Slate (default)
        ]

        created_count = 0
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(  # Create if not exists
                name=tag_data['name'],
                defaults={'color': tag_data['color']}
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully seeded {created_count} new tags')
        )
```

---

## 9. posts/migrations/0001_initial.py

**Location**: `posts/migrations/0001_initial.py`
**Purpose**: Initial migration for posts app

Creates these database tables:
- `posts_tag`: Tag model with name and color
- `posts_post`: Post model with soft delete
- `posts_posttag`: Through model for Post-Tag M2M
- `posts_comment`: Comment model with soft delete
- `posts_reaction`: Reaction model (like/dislike)

---

## 10. posts/migrations/0002_add_color_to_tag.py

**Location**: `posts/migrations/0002_add_color_to_tag.py`
**Purpose**: Add color field to Tag model

```python
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='color',
            field=models.CharField(default='#94a3b8', max_length=7, verbose_name='اللون'),
        ),
    ]
```

---

# ADMIN PANEL APP

The admin_panel app provides a staff-only dashboard for moderating content and viewing statistics.

## 1. admin_panel/models.py

**Location**: `admin_panel/models.py`
**Purpose**: Report model for flagging inappropriate content

```python
"""
Models for admin panel - reports and moderation.
"""

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Report(models.Model):                      # Line 11: Report model
    """
    Report for flagging inappropriate content.
    Uses GenericForeignKey to report any model (Post, Comment, etc.)
    """
    REASON_CHOICES = [                           # Line 16-23: Report reasons
        ('hate_speech', 'خطاب كراهية'),
        ('spam', 'محتوى مزعج (سبام)'),
        ('inappropriate', 'محتوى غير لائق'),
        ('misinformation', 'معلومات مضللة'),
        ('harassment', 'تحرش أو إساءة'),
        ('other', 'أخرى'),
    ]

    STATUS_CHOICES = [                           # Line 25-29: Report status
        ('pending', 'قيد المراجعة'),
        ('approved', 'تمت الموافقة'),
        ('dismissed', 'مرفوض'),
    ]

    # Who submitted the report
    reporter = models.ForeignKey(                # Line 32-36
        User,
        on_delete=models.CASCADE,
        related_name='reports_submitted',
        verbose_name='المُبلِّغ'
    )

    # Generic Foreign Key - can point to any model
    content_type = models.ForeignKey(            # Line 39-42
        ContentType,
        on_delete=models.CASCADE,
        verbose_name='نوع المحتوى'
    )
    object_id = models.PositiveIntegerField(verbose_name='معرف المحتوى')
    content_object = GenericForeignKey('content_type', 'object_id')  # Line 45

    # Report details
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, verbose_name='السبب')
    details = models.TextField(blank=True, verbose_name='تفاصيل إضافية')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Review info
    reviewed_by = models.ForeignKey(             # Line 52-57: Who reviewed
        User,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='reports_reviewed',
        verbose_name='تمت المراجعة بواسطة'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:                                  # Line 62-66
        verbose_name = 'بلاغ'
        verbose_name_plural = 'البلاغات'
        ordering = ['-created_at']
        unique_together = ('reporter', 'content_type', 'object_id')  # Prevent duplicates

    def __str__(self):
        return f'بلاغ #{self.pk} - {self.get_reason_display()}'

    @property                                    # Line 71-77: Arabic content type name
    def get_content_type_display_ar(self):
        """Get Arabic name for content type."""
        type_map = {
            'post': 'منشور',
            'comment': 'تعليق',
        }
        return type_map.get(self.content_type.model, self.content_type.model)

    @property                                    # Line 79-88: Content preview
    def get_reported_content_preview(self):
        """Get preview of reported content."""
        if self.content_object is None:
            return 'محتوى محذوف'
        if hasattr(self.content_object, 'title'):
            return self.content_object.title[:50]
        if hasattr(self.content_object, 'body'):
            return self.content_object.body[:50]
        return str(self.content_object)[:50]
```

**GenericForeignKey pattern**: This allows the Report model to reference any other model (Post, Comment, etc.) without needing separate foreign keys for each. It uses `content_type` to store which model and `object_id` to store the primary key.

---

## 2. admin_panel/views.py

**Location**: `admin_panel/views.py`
**Purpose**: Views for admin dashboard and report management

```python
"""
Views for admin panel - dashboard and report management.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count

from .models import Report
from .forms import ReportForm
from posts.models import Post, Comment, Tag


def staff_required(user):                        # Line 19: Staff check function
    """Check if user is staff member."""
    return user.is_authenticated and user.is_staff


@user_passes_test(staff_required)                # Line 24: Require staff
def dashboard(request):                          # Line 25: Main dashboard
    """Admin dashboard with statistics."""
    # Count statistics
    total_users = User.objects.count()
    total_posts = Post.objects.filter(deleted_at__isnull=True).count()
    total_comments = Comment.objects.filter(deleted_at__isnull=True).count()

    # Recent activity
    now = timezone.now()
    posts_24h = Post.objects.filter(
        created_at__gte=now - timezone.timedelta(hours=24),
        deleted_at__isnull=True
    ).count()
    posts_7d = Post.objects.filter(
        created_at__gte=now - timezone.timedelta(days=7),
        deleted_at__isnull=True
    ).count()

    # Pending reports count
    pending_reports_count = Report.objects.filter(status='pending').count()

    # Top posts by likes
    top_posts = Post.objects.filter(deleted_at__isnull=True).annotate(
        like_count=Count('reactions', filter=models.Q(reactions__value='like'))
    ).order_by('-like_count')[:5]

    # Top tags by usage
    top_tags = Tag.objects.annotate(
        post_count=Count('posts', filter=models.Q(posts__deleted_at__isnull=True))
    ).order_by('-post_count')[:10]

    # Recent reports
    recent_reports = Report.objects.filter(status='pending')[:5]

    return render(request, 'admin_panel/dashboard.html', {
        'total_users': total_users,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'posts_24h': posts_24h,
        'posts_7d': posts_7d,
        'pending_reports_count': pending_reports_count,
        'top_posts': top_posts,
        'top_tags': top_tags,
        'recent_reports': recent_reports,
    })


@user_passes_test(staff_required)
def reports_list(request):                       # Line 75: List reports
    """List all reports with status filter."""
    status_filter = request.GET.get('status', 'pending')  # Default: pending

    if status_filter == 'all':
        reports = Report.objects.all()
    else:
        reports = Report.objects.filter(status=status_filter)

    pending_reports_count = Report.objects.filter(status='pending').count()

    return render(request, 'admin_panel/reports/list.html', {
        'reports': reports,
        'status_filter': status_filter,
        'pending_reports_count': pending_reports_count,
    })


@user_passes_test(staff_required)
def report_detail(request, pk):                  # Line 93: View single report
    """View details of a single report."""
    report = get_object_or_404(Report, pk=pk)
    pending_reports_count = Report.objects.filter(status='pending').count()

    return render(request, 'admin_panel/reports/detail.html', {
        'report': report,
        'pending_reports_count': pending_reports_count,
    })


@user_passes_test(staff_required)
def approve_report(request, pk):                 # Line 105: Approve report
    """Approve report and soft-delete the content."""
    report = get_object_or_404(Report, pk=pk, status='pending')

    if request.method == 'POST':
        # Soft delete the reported content
        if report.content_object:
            report.content_object.deleted_at = timezone.now()
            report.content_object.save()

        # Update report status
        report.status = 'approved'
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.save()

        messages.success(request, 'تم قبول البلاغ وحذف المحتوى.')
        return redirect('admin_panel:reports_list')

    return redirect('admin_panel:report_detail', pk=pk)


@user_passes_test(staff_required)
def dismiss_report(request, pk):                 # Line 127: Dismiss report
    """Dismiss a report without action."""
    report = get_object_or_404(Report, pk=pk, status='pending')

    if request.method == 'POST':
        report.status = 'dismissed'
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.save()

        messages.success(request, 'تم رفض البلاغ.')
        return redirect('admin_panel:reports_list')

    return redirect('admin_panel:report_detail', pk=pk)


@login_required                                  # Line 143: Submit report (user-facing)
def submit_report(request):
    """Submit a report (for regular users via HTMX)."""
    if request.method == 'POST':
        content_type_str = request.POST.get('content_type')  # 'post' or 'comment'
        object_id = request.POST.get('object_id')
        reason = request.POST.get('reason')
        details = request.POST.get('details', '')

        # Get content type model
        if content_type_str == 'post':
            content_type = ContentType.objects.get_for_model(Post)
        elif content_type_str == 'comment':
            content_type = ContentType.objects.get_for_model(Comment)
        else:
            return HttpResponse('<div class="alert alert-danger">نوع محتوى غير صالح</div>')

        # Check for duplicate report
        if Report.objects.filter(
            reporter=request.user,
            content_type=content_type,
            object_id=object_id
        ).exists():
            return HttpResponse('<div class="alert alert-warning">لقد أبلغت عن هذا المحتوى مسبقاً</div>')

        # Create report
        Report.objects.create(
            reporter=request.user,
            content_type=content_type,
            object_id=object_id,
            reason=reason,
            details=details
        )

        return HttpResponse('<div class="alert alert-success">تم إرسال البلاغ بنجاح. شكراً لمساعدتك!</div>')

    return HttpResponse('Method not allowed', status=405)
```

---

## 3. admin_panel/urls.py

**Location**: `admin_panel/urls.py`
**Purpose**: URL routing for admin panel

```python
from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Reports management
    path('reports/', views.reports_list, name='reports_list'),
    path('reports/<int:pk>/', views.report_detail, name='report_detail'),
    path('reports/<int:pk>/approve/', views.approve_report, name='approve_report'),
    path('reports/<int:pk>/dismiss/', views.dismiss_report, name='dismiss_report'),

    # Report submission (for users)
    path('report/submit/', views.submit_report, name='submit_report'),
]
```

---

## 4. admin_panel/forms.py

**Location**: `admin_panel/forms.py`
**Purpose**: Forms for admin panel

```python
from django import forms
from .models import Report


class ReportForm(forms.ModelForm):
    """Form for submitting a report."""
    class Meta:
        model = Report
        fields = ['reason', 'details']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أضف تفاصيل إضافية (اختياري)...'
            }),
        }
```

---

## 5. admin_panel/migrations/0001_initial.py

**Location**: `admin_panel/migrations/0001_initial.py`
**Purpose**: Create Report table

Creates `admin_panel_report` table with:
- `id` (BigAutoField, PK)
- `reporter_id` (FK to auth_user)
- `content_type_id` (FK to django_content_type)
- `object_id` (PositiveIntegerField)
- `reason` (CharField with choices)
- `details` (TextField)
- `status` (CharField with choices)
- `reviewed_by_id` (FK to auth_user, nullable)
- `reviewed_at` (DateTimeField, nullable)
- `created_at` (DateTimeField)
- UNIQUE constraint on (reporter_id, content_type_id, object_id)

---

# TEMPLATES - DETAILED DOCUMENTATION

## 1. templates/base.html

**Location**: `templates/base.html`
**Purpose**: Base template that all other templates extend

**Key sections:**
- **Head**: Bootstrap 5 RTL CSS, Bootstrap Icons, custom styles
- **Navbar**: Logo, navigation links, user dropdown
- **Content block**: Where child templates insert content
- **Scripts**: Bootstrap JS, HTMX library

```html
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}مفتاح{% endblock %}</title>

    <!-- Bootstrap 5 RTL CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.rtl.min.css" rel="stylesheet">

    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">

    <!-- Custom CSS for flashcards, quizzes, etc. -->
    <style>
        /* Flashcard flip animation */
        .flashcard { /* ... */ }
        .flashcard.flipped .flashcard-inner { transform: rotateY(180deg); }

        /* Quiz option styles */
        .quiz-option.correct { background-color: #dcfce7; }
        .quiz-option.incorrect { background-color: #fee2e2; }

        /* Tag badges */
        .tag-badge { /* ... */ }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom">
        <!-- Brand, navigation, user menu -->
    </nav>

    <!-- Flash messages -->
    {% if messages %}
    <div class="container mt-3">
        {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <!-- Main content -->
    <main class="py-4">
        {% block content %}{% endblock %}
    </main>

    <!-- Bootstrap JS Bundle -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

    <!-- HTMX for dynamic updates without page reload -->
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

---

## 2. templates/landing.html

**Location**: `templates/landing.html`
**Purpose**: Marketing/landing page for unauthenticated users

```html
{% extends 'base.html' %}

{% block title %}مفتاح - منصة تعليمية للطلاب العرب{% endblock %}

{% block content %}
<div class="landing-page">
    <!-- Hero Section - Main call to action -->
    <section class="hero-section text-center py-5">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <h1 class="display-3 fw-bold mb-4">
                        <i class="bi bi-key-fill text-primary"></i>
                        مفتاح
                    </h1>
                    <p class="lead mb-4">
                        منصة تعليمية ذكية تساعدك على تحويل أي نص أو ملف PDF
                        <br>
                        إلى بطاقات تعليمية واختبارات تفاعلية باستخدام الذكاء الاصطناعي
                    </p>
                    <div class="d-flex gap-3 justify-content-center">
                        <a href="{% url 'accounts:signup' %}" class="btn btn-primary btn-lg px-5">
                            ابدأ الآن
                        </a>
                        <a href="{% url 'accounts:login' %}" class="btn btn-outline-primary btn-lg px-5">
                            تسجيل الدخول
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section - How it works -->
    <section class="features-section py-5 bg-white">
        <div class="container">
            <h2 class="text-center mb-5">كيف يعمل مفتاح؟</h2>
            <div class="row g-4">
                <!-- Step 1: Input text -->
                <div class="col-md-4">
                    <div class="card h-100 text-center p-4">
                        <div class="card-body">
                            <div class="feature-icon mb-3">
                                <i class="bi bi-file-text display-4 text-primary"></i>
                            </div>
                            <h5 class="card-title">أدخل النص</h5>
                            <p class="card-text text-muted">
                                الصق أي نص دراسي أو ارفع ملف PDF
                                <br>
                                يدعم اللغتين العربية والإنجليزية
                            </p>
                        </div>
                    </div>
                </div>
                <!-- Step 2: AI processing -->
                <div class="col-md-4">
                    <div class="card h-100 text-center p-4">
                        <div class="card-body">
                            <div class="feature-icon mb-3">
                                <i class="bi bi-robot display-4 text-primary"></i>
                            </div>
                            <h5 class="card-title">الذكاء الاصطناعي</h5>
                            <p class="card-text text-muted">
                                يقوم الذكاء الاصطناعي بتحليل النص
                                <br>
                                وإنشاء محتوى تعليمي مخصص
                            </p>
                        </div>
                    </div>
                </div>
                <!-- Step 3: Learn -->
                <div class="col-md-4">
                    <div class="card h-100 text-center p-4">
                        <div class="card-body">
                            <div class="feature-icon mb-3">
                                <i class="bi bi-mortarboard display-4 text-primary"></i>
                            </div>
                            <h5 class="card-title">تعلم بفعالية</h5>
                            <p class="card-text text-muted">
                                استخدم البطاقات التعليمية والاختبارات
                                <br>
                                للمراجعة والتحضير للامتحانات
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Study Types Section -->
    <section class="study-types-section py-5">
        <div class="container">
            <div class="row g-4">
                <!-- Flashcards card -->
                <div class="col-md-6">
                    <div class="card h-100 study-card">
                        <div class="card-body p-4">
                            <div class="d-flex align-items-center mb-3">
                                <i class="bi bi-stack display-5 text-primary me-3"></i>
                                <h4 class="mb-0">بطاقات تعليمية</h4>
                            </div>
                            <p class="text-muted">
                                بطاقات تفاعلية بتأثير القلب
                                <br>
                                مثالية للحفظ والمراجعة السريعة
                            </p>
                            <ul class="list-unstyled">
                                <li><i class="bi bi-check-circle text-success me-2"></i> سؤال وجواب</li>
                                <li><i class="bi bi-check-circle text-success me-2"></i> تأثير قلب البطاقة</li>
                                <li><i class="bi bi-check-circle text-success me-2"></i> سهلة المشاركة</li>
                            </ul>
                        </div>
                    </div>
                </div>
                <!-- Quiz card -->
                <div class="col-md-6">
                    <div class="card h-100 study-card">
                        <div class="card-body p-4">
                            <div class="d-flex align-items-center mb-3">
                                <i class="bi bi-question-circle display-5 text-primary me-3"></i>
                                <h4 class="mb-0">اختبارات</h4>
                            </div>
                            <p class="text-muted">
                                اختبارات اختيار من متعدد
                                <br>
                                مع شرح لكل إجابة
                            </p>
                            <ul class="list-unstyled">
                                <li><i class="bi bi-check-circle text-success me-2"></i> 4 خيارات لكل سؤال</li>
                                <li><i class="bi bi-check-circle text-success me-2"></i> شرح مفصل للإجابات</li>
                                <li><i class="bi bi-check-circle text-success me-2"></i> تقييم فوري</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section py-5 bg-primary text-white text-center">
        <div class="container">
            <h2 class="mb-4">ابدأ رحلتك التعليمية الآن</h2>
            <p class="lead mb-4">انضم إلى مجتمع الطلاب وشارك موادك التعليمية</p>
            <a href="{% url 'accounts:signup' %}" class="btn btn-light btn-lg px-5">
                إنشاء حساب مجاني
            </a>
        </div>
    </section>

    <!-- Footer -->
    <footer class="py-4 border-top">
        <div class="container text-center text-muted">
            <p class="mb-0">مفتاح - منصة تعليمية للطلاب العرب</p>
        </div>
    </footer>
</div>

<style>
    .hero-section {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 100px 0;
    }
    .feature-icon {
        width: 80px;
        height: 80px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #f0f9ff;
        border-radius: 50%;
    }
    .cta-section {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    }
</style>
{% endblock %}
```

**Line-by-line explanation:**
- **Lines 1-3**: Extends base template, sets Arabic page title
- **Lines 8-31**: Hero section with app name, tagline, and signup/login buttons
- **Lines 34-76**: Features section explaining the 3-step process (input → AI → learn)
- **Lines 79-132**: Two cards showcasing flashcards and quizzes features
- **Lines 135-145**: Final call-to-action section with gradient background
- **Lines 148-152**: Simple footer
- **Lines 155-175**: Inline CSS for hero gradient, feature icons, and CTA styling

---

## 3. templates/home.html

**Location**: `templates/home.html`
**Purpose**: Dashboard for authenticated users - main hub for creating study materials

```html
{% extends 'base.html' %}

{% block title %}الرئيسية - مفتاح{% endblock %}

{% block content %}
<div class="container">
    <!-- Search Bar - searches posts by title, caption, or tags -->
    <div class="row justify-content-center mb-5">
        <div class="col-lg-8">
            <form action="{% url 'posts:search' %}" method="get" class="d-flex gap-2">
                <input type="text" name="q" class="form-control form-control-lg"
                       placeholder="ابحث في المنشورات...">
                <button type="submit" class="btn btn-primary btn-lg">
                    <i class="bi bi-search"></i>
                </button>
            </form>
        </div>
    </div>

    <!-- Main Options - Two big cards for creating content -->
    <div class="row justify-content-center">
        <div class="col-lg-10">
            <h2 class="text-center mb-4">أنشئ مجموعة دراسية جديدة</h2>
            <div class="row g-4">
                <!-- Flashcards Option -->
                <div class="col-md-6">
                    <a href="{% url 'study:generate' 'flashcards' %}" class="text-decoration-none">
                        <div class="card study-card h-100">
                            <div class="card-body p-5 text-center">
                                <div class="option-icon mb-4">
                                    <i class="bi bi-stack display-1 text-primary"></i>
                                </div>
                                <h3 class="card-title mb-3">بطاقات تعليمية</h3>
                                <p class="card-text text-muted">
                                    أنشئ بطاقات تعليمية تفاعلية
                                    <br>
                                    مثالية للحفظ والمراجعة
                                </p>
                                <div class="mt-4">
                                    <span class="btn btn-primary btn-lg">
                                        <i class="bi bi-plus-lg me-2"></i>
                                        إنشاء بطاقات
                                    </span>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>

                <!-- Quiz Option -->
                <div class="col-md-6">
                    <a href="{% url 'study:generate' 'quiz' %}" class="text-decoration-none">
                        <div class="card study-card h-100">
                            <div class="card-body p-5 text-center">
                                <div class="option-icon mb-4">
                                    <i class="bi bi-question-circle display-1 text-primary"></i>
                                </div>
                                <h3 class="card-title mb-3">اختبار</h3>
                                <p class="card-text text-muted">
                                    أنشئ اختبار اختيار من متعدد
                                    <br>
                                    مع شرح لكل إجابة
                                </p>
                                <div class="mt-4">
                                    <span class="btn btn-primary btn-lg">
                                        <i class="bi bi-plus-lg me-2"></i>
                                        إنشاء اختبار
                                    </span>
                                </div>
                            </div>
                        </div>
                    </a>
                </div>
            </div>
        </div>
    </div>

    <!-- Quick Links - Secondary navigation -->
    <div class="row justify-content-center mt-5">
        <div class="col-lg-10">
            <div class="d-flex justify-content-center gap-3 flex-wrap">
                <a href="{% url 'study:history' %}" class="btn btn-outline-secondary">
                    <i class="bi bi-clock-history me-2"></i>
                    عرض السجل
                </a>
                <a href="{% url 'feed:recent' %}" class="btn btn-outline-secondary">
                    <i class="bi bi-globe me-2"></i>
                    استكشف المنشورات
                </a>
                <a href="{% url 'feed:following' %}" class="btn btn-outline-secondary">
                    <i class="bi bi-people me-2"></i>
                    منشورات المتابَعين
                </a>
            </div>
        </div>
    </div>
</div>

<style>
    .option-icon {
        width: 120px;
        height: 120px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 50%;
    }
</style>
{% endblock %}
```

**Line-by-line explanation:**
- **Lines 7-17**: Search bar that submits to posts:search view
- **Lines 20-72**: Two large cards linking to flashcard and quiz generation
- **Lines 75-91**: Quick links to history, explore feed, and following feed
- **Lines 93-105**: CSS for circular gradient icon background

---

## 4. templates/accounts/login.html

**Location**: `templates/accounts/login.html`
**Purpose**: User login form

```html
{% extends 'base.html' %}

{% block title %}تسجيل الدخول - مفتاح{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-5">
            <!-- Branding -->
            <div class="text-center mb-4">
                <a href="{% url 'landing' %}" class="text-decoration-none">
                    <h1 class="display-5 text-primary">
                        <i class="bi bi-key-fill"></i> مفتاح
                    </h1>
                </a>
            </div>

            <div class="card">
                <div class="card-body p-4">
                    <h4 class="text-center mb-4">تسجيل الدخول</h4>

                    <form method="post">
                        {% csrf_token %}

                        <!-- Non-field errors (e.g., invalid credentials) -->
                        {% if form.non_field_errors %}
                        <div class="alert alert-danger">
                            {% for error in form.non_field_errors %}
                            {{ error }}
                            {% endfor %}
                        </div>
                        {% endif %}

                        <!-- Username field -->
                        <div class="mb-3">
                            <label for="id_username" class="form-label">{{ form.username.label }}</label>
                            {{ form.username }}
                            {% if form.username.errors %}
                            <div class="text-danger small">{{ form.username.errors.0 }}</div>
                            {% endif %}
                        </div>

                        <!-- Password field -->
                        <div class="mb-3">
                            <label for="id_password" class="form-label">{{ form.password.label }}</label>
                            {{ form.password }}
                            {% if form.password.errors %}
                            <div class="text-danger small">{{ form.password.errors.0 }}</div>
                            {% endif %}
                        </div>

                        <button type="submit" class="btn btn-primary w-100 mb-3">
                            تسجيل الدخول
                        </button>
                    </form>

                    <!-- Link to signup -->
                    <div class="text-center">
                        <span class="text-muted">ليس لديك حساب؟</span>
                        <a href="{% url 'accounts:signup' %}">إنشاء حساب جديد</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 5. templates/accounts/signup.html

**Location**: `templates/accounts/signup.html`
**Purpose**: User registration form

```html
{% extends 'base.html' %}

{% block title %}إنشاء حساب - مفتاح{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-5">
            <!-- Branding -->
            <div class="text-center mb-4">
                <a href="{% url 'landing' %}" class="text-decoration-none">
                    <h1 class="display-5 text-primary">
                        <i class="bi bi-key-fill"></i> مفتاح
                    </h1>
                </a>
            </div>

            <div class="card">
                <div class="card-body p-4">
                    <h4 class="text-center mb-4">إنشاء حساب جديد</h4>

                    <form method="post">
                        {% csrf_token %}

                        {% if form.non_field_errors %}
                        <div class="alert alert-danger">
                            {% for error in form.non_field_errors %}
                            {{ error }}
                            {% endfor %}
                        </div>
                        {% endif %}

                        <!-- Username -->
                        <div class="mb-3">
                            <label for="id_username" class="form-label">{{ form.username.label }}</label>
                            {{ form.username }}
                            {% if form.username.help_text %}
                            <div class="form-text">{{ form.username.help_text }}</div>
                            {% endif %}
                            {% if form.username.errors %}
                            <div class="text-danger small">{{ form.username.errors.0 }}</div>
                            {% endif %}
                        </div>

                        <!-- Email -->
                        <div class="mb-3">
                            <label for="id_email" class="form-label">{{ form.email.label }}</label>
                            {{ form.email }}
                            {% if form.email.errors %}
                            <div class="text-danger small">{{ form.email.errors.0 }}</div>
                            {% endif %}
                        </div>

                        <!-- Password -->
                        <div class="mb-3">
                            <label for="id_password1" class="form-label">{{ form.password1.label }}</label>
                            {{ form.password1 }}
                            {% if form.password1.help_text %}
                            <div class="form-text">{{ form.password1.help_text }}</div>
                            {% endif %}
                            {% if form.password1.errors %}
                            <div class="text-danger small">{{ form.password1.errors.0 }}</div>
                            {% endif %}
                        </div>

                        <!-- Confirm Password -->
                        <div class="mb-3">
                            <label for="id_password2" class="form-label">{{ form.password2.label }}</label>
                            {{ form.password2 }}
                            {% if form.password2.errors %}
                            <div class="text-danger small">{{ form.password2.errors.0 }}</div>
                            {% endif %}
                        </div>

                        <button type="submit" class="btn btn-primary w-100 mb-3">
                            إنشاء الحساب
                        </button>
                    </form>

                    <!-- Link to login -->
                    <div class="text-center">
                        <span class="text-muted">لديك حساب بالفعل؟</span>
                        <a href="{% url 'accounts:login' %}">تسجيل الدخول</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 6. templates/accounts/profile.html

**Location**: `templates/accounts/profile.html`
**Purpose**: Display user profile with their posts and follow button

```html
{% extends 'base.html' %}

{% block title %}{{ profile_user.username }} - مفتاح{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <!-- Profile Header Card -->
            <div class="card mb-4">
                <div class="card-body p-4">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="d-flex align-items-center gap-3">
                            <!-- Avatar placeholder -->
                            <div class="profile-avatar">
                                <i class="bi bi-person-circle display-1 text-primary"></i>
                            </div>
                            <div>
                                <h3 class="mb-1">{{ profile_user.username }}</h3>
                                {% if profile_user.profile.bio %}
                                <p class="text-muted mb-2">{{ profile_user.profile.bio }}</p>
                                {% endif %}
                                <!-- Follower/Following counts -->
                                <div class="d-flex gap-3 text-muted">
                                    <span>
                                        <strong>{{ profile_user.profile.followers_count }}</strong> متابِع
                                    </span>
                                    <span>
                                        <strong>{{ profile_user.profile.following_count }}</strong> متابَع
                                    </span>
                                </div>
                            </div>
                        </div>

                        <!-- Action buttons -->
                        <div>
                            {% if is_own_profile %}
                            <a href="{% url 'accounts:edit_profile' %}" class="btn btn-outline-primary">
                                <i class="bi bi-pencil me-1"></i>
                                تعديل الملف
                            </a>
                            {% else %}
                            <!-- Follow button container for HTMX updates -->
                            <div id="follow-button">
                                {% include 'accounts/partials/follow_button.html' %}
                            </div>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>

            <!-- User's Posts Section -->
            <h5 class="mb-3">
                <i class="bi bi-file-post me-2"></i>
                منشورات {{ profile_user.username }}
            </h5>

            {% if posts %}
            <div class="row g-3">
                {% for post in posts %}
                <div class="col-12">
                    {% include 'posts/partials/post_card.html' %}
                </div>
                {% endfor %}
            </div>
            {% else %}
            <div class="empty-state">
                <i class="bi bi-file-earmark-text"></i>
                <p>لا توجد منشورات حتى الآن</p>
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

**Key features:**
- **Line 40-44**: Includes follow button partial with HTMX target container
- **Line 57-61**: Loops through user's posts using post_card partial
- Profile shows different UI for own profile vs others (edit button vs follow button)

---

## 7. templates/accounts/edit_profile.html

**Location**: `templates/accounts/edit_profile.html`
**Purpose**: Form for editing user's own profile

```html
{% extends 'base.html' %}

{% block title %}تعديل الملف الشخصي - مفتاح{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">تعديل الملف الشخصي</h5>
                </div>
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}

                        <!-- Username field from UserUpdateForm -->
                        <div class="mb-3">
                            <label for="id_username" class="form-label">{{ user_form.username.label }}</label>
                            {{ user_form.username }}
                            {% if user_form.username.errors %}
                            <div class="text-danger small">{{ user_form.username.errors.0 }}</div>
                            {% endif %}
                        </div>

                        <!-- Email field from UserUpdateForm -->
                        <div class="mb-3">
                            <label for="id_email" class="form-label">{{ user_form.email.label }}</label>
                            {{ user_form.email }}
                            {% if user_form.email.errors %}
                            <div class="text-danger small">{{ user_form.email.errors.0 }}</div>
                            {% endif %}
                        </div>

                        <!-- Bio field from ProfileForm -->
                        <div class="mb-3">
                            <label for="id_bio" class="form-label">{{ profile_form.bio.label }}</label>
                            {{ profile_form.bio }}
                            {% if profile_form.bio.errors %}
                            <div class="text-danger small">{{ profile_form.bio.errors.0 }}</div>
                            {% endif %}
                        </div>

                        <div class="d-flex gap-2">
                            <button type="submit" class="btn btn-primary">
                                <i class="bi bi-check-lg me-1"></i>
                                حفظ التغييرات
                            </button>
                            <a href="{% url 'accounts:profile' user.username %}" class="btn btn-outline-secondary">
                                إلغاء
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

**Note**: Uses two forms (UserUpdateForm + ProfileForm) to update both User model and Profile model.

---

## 8. templates/accounts/partials/follow_button.html

**Location**: `templates/accounts/partials/follow_button.html`
**Purpose**: HTMX-powered follow/unfollow button partial

```html
{% if is_following %}
<!-- Already following - show "متابَع" (Following) button -->
<button type="button" class="btn btn-secondary"
        hx-post="{% url 'accounts:toggle_follow' profile_user.username %}"
        hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'
        hx-target="#follow-button"
        hx-swap="innerHTML">
    <i class="bi bi-check-lg me-1"></i>
    متابَع
</button>
{% elif follows_me %}
<!-- They follow me but I don't follow them - show "Follow back" -->
<button type="button" class="btn btn-primary"
        hx-post="{% url 'accounts:toggle_follow' profile_user.username %}"
        hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'
        hx-target="#follow-button"
        hx-swap="innerHTML">
    <i class="bi bi-person-plus me-1"></i>
    متابعة متبادلة
</button>
{% else %}
<!-- Not following - show "Follow" button -->
<button type="button" class="btn btn-primary"
        hx-post="{% url 'accounts:toggle_follow' profile_user.username %}"
        hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'
        hx-target="#follow-button"
        hx-swap="innerHTML">
    <i class="bi bi-person-plus me-1"></i>
    متابعة
</button>
{% endif %}
```

**HTMX explanation:**
- `hx-post`: Sends POST request to toggle_follow endpoint
- `hx-headers`: Includes CSRF token for Django security
- `hx-target="#follow-button"`: Updates the parent container
- `hx-swap="innerHTML"`: Replaces inner HTML with server response
- **Result**: Button updates instantly without page reload

---

## 9. templates/study/generate.html

**Location**: `templates/study/generate.html`
**Purpose**: Form for generating flashcards or quizzes using AI

```html
{% extends 'base.html' %}

{% block title %}{% if set_type == 'flashcards' %}إنشاء بطاقات{% else %}إنشاء اختبار{% endif %} - مفتاح{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">
                        {% if set_type == 'flashcards' %}
                        <i class="bi bi-stack me-2"></i>
                        إنشاء بطاقات تعليمية
                        {% else %}
                        <i class="bi bi-question-circle me-2"></i>
                        إنشاء اختبار
                        {% endif %}
                    </h5>
                </div>
                <div class="card-body">
                    <form method="post" enctype="multipart/form-data" id="generate-form">
                        {% csrf_token %}
                        <input type="hidden" name="set_type" value="{{ set_type }}">

                        <!-- Title field -->
                        <div class="mb-3">
                            <label class="form-label">{{ form.title.label }}</label>
                            {{ form.title }}
                        </div>

                        <!-- Input Type Toggle: Text vs PDF -->
                        <div class="mb-3">
                            <label class="form-label">{{ form.input_type.label }}</label>
                            <div class="d-flex gap-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="input_type"
                                           id="input_text" value="text" checked
                                           onchange="toggleInputType('text')">
                                    <label class="form-check-label" for="input_text">
                                        <i class="bi bi-file-text me-1"></i> نص
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="input_type"
                                           id="input_pdf" value="pdf"
                                           onchange="toggleInputType('pdf')">
                                    <label class="form-check-label" for="input_pdf">
                                        <i class="bi bi-file-pdf me-1"></i> ملف PDF
                                    </label>
                                </div>
                            </div>
                        </div>

                        <!-- Text Input Section (shown by default) -->
                        <div class="mb-3" id="text-input-section">
                            <label class="form-label">{{ form.text_content.label }}</label>
                            {{ form.text_content }}
                            <div class="form-text">أدخل النص الذي تريد إنشاء المحتوى منه (50 حرف على الأقل)</div>
                        </div>

                        <!-- PDF Input Section (hidden by default) -->
                        <div class="mb-3 d-none" id="pdf-input-section">
                            <label class="form-label">{{ form.pdf_file.label }}</label>
                            {{ form.pdf_file }}
                            <div class="form-text">ارفع ملف PDF (الحد الأقصى 10 ميجابايت)</div>
                            <!-- PDF warnings about OCR -->
                            <div class="alert alert-warning mt-2 py-2">
                                <strong>تنبيهات مهمة:</strong>
                                <ul class="mb-0 mt-1 small">
                                    <li>ملفات PDF الممسوحة ضوئياً لا يمكن استخراج النص منها</li>
                                    <li>الملفات الكبيرة قد تستغرق وقتاً أطول</li>
                                </ul>
                            </div>
                        </div>

                        <!-- Count selector (1-30) -->
                        <div class="mb-4">
                            <label class="form-label">{{ form.count.label }}</label>
                            <div class="d-flex align-items-center gap-2">
                                {{ form.count }}
                                <span class="text-muted">
                                    {% if set_type == 'flashcards' %}بطاقة{% else %}سؤال{% endif %}
                                </span>
                            </div>
                        </div>

                        <button type="submit" class="btn btn-primary btn-lg" id="submit-btn">
                            <i class="bi bi-magic me-2"></i>
                            إنشاء باستخدام الذكاء الاصطناعي
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>

{% block extra_js %}
<script>
    // Toggle between text and PDF input sections
    function toggleInputType(type) {
        const textSection = document.getElementById('text-input-section');
        const pdfSection = document.getElementById('pdf-input-section');
        if (type === 'text') {
            textSection.classList.remove('d-none');
            pdfSection.classList.add('d-none');
        } else {
            textSection.classList.add('d-none');
            pdfSection.classList.remove('d-none');
        }
    }

    // Show loading state on form submit
    document.getElementById('generate-form').addEventListener('submit', function() {
        const btn = document.getElementById('submit-btn');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> جاري الإنشاء...';
    });
</script>
{% endblock %}
{% endblock %}
```

---

## 10. templates/study/flashcards_view.html

**Location**: `templates/study/flashcards_view.html`
**Purpose**: Interactive flashcard viewer with flip animation

```html
{% extends 'base.html' %}

{% block title %}{{ study_set.title|default:'بطاقات تعليمية' }} - مفتاح{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <!-- Header with title and action buttons -->
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h4 class="mb-1">
                        <i class="bi bi-stack me-2 text-primary"></i>
                        {{ study_set.title|default:'بطاقات تعليمية' }}
                    </h4>
                    <div class="text-muted">
                        {{ flashcards|length }} بطاقة •
                        {% if study_set.language == 'ar' %}العربية{% else %}English{% endif %}
                    </div>
                </div>
                {% if is_owner %}
                <div class="d-flex gap-2">
                    <a href="{% url 'posts:create' %}?study_set={{ study_set.pk }}" class="btn btn-primary">
                        <i class="bi bi-share me-1"></i> مشاركة
                    </a>
                    <a href="{% url 'study:delete' study_set.pk %}" class="btn btn-outline-danger">
                        <i class="bi bi-trash"></i>
                    </a>
                </div>
                {% endif %}
            </div>

            <!-- Flashcard Carousel -->
            <div class="flashcard-container mb-4">
                <!-- Navigation buttons -->
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <button class="btn btn-outline-secondary" onclick="prevCard()" id="prev-btn">
                        <i class="bi bi-chevron-right"></i> السابق
                    </button>
                    <span class="text-muted" id="card-counter">1 / {{ flashcards|length }}</span>
                    <button class="btn btn-outline-secondary" onclick="nextCard()" id="next-btn">
                        التالي <i class="bi bi-chevron-left"></i>
                    </button>
                </div>

                <!-- Flashcards (only first one visible) -->
                {% for card in flashcards %}
                <div class="flashcard {% if not forloop.first %}d-none{% endif %}"
                     data-index="{{ forloop.counter0 }}"
                     onclick="flipCard(this)">
                    <div class="flashcard-inner">
                        <div class="flashcard-front">
                            <div>
                                <div class="small mb-2 opacity-75">السؤال</div>
                                <div class="fs-5">{{ card.question }}</div>
                            </div>
                        </div>
                        <div class="flashcard-back">
                            <div>
                                <div class="small mb-2 opacity-75">الإجابة</div>
                                <div class="fs-5">{{ card.answer }}</div>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}

                <div class="text-center mt-3 text-muted">
                    <i class="bi bi-hand-index-thumb"></i> اضغط على البطاقة لقلبها
                </div>
            </div>

            <!-- All Cards List View -->
            <div class="card">
                <div class="card-header">
                    <h6 class="mb-0">جميع البطاقات</h6>
                </div>
                <div class="card-body p-0">
                    <div class="list-group list-group-flush">
                        {% for card in flashcards %}
                        <div class="list-group-item">
                            <div class="row">
                                <div class="col-md-6">
                                    <small class="text-muted">السؤال</small>
                                    <p class="mb-0">{{ card.question }}</p>
                                </div>
                                <div class="col-md-6">
                                    <small class="text-muted">الإجابة</small>
                                    <p class="mb-0">{{ card.answer }}</p>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

{% block extra_js %}
<script>
    let currentIndex = 0;
    const totalCards = {{ flashcards|length }};

    function showCard(index) {
        document.querySelectorAll('.flashcard').forEach((card, i) => {
            card.classList.toggle('d-none', i !== index);
            card.classList.remove('flipped');
        });
        document.getElementById('card-counter').textContent = `${index + 1} / ${totalCards}`;
        document.getElementById('prev-btn').disabled = index === 0;
        document.getElementById('next-btn').disabled = index === totalCards - 1;
    }

    function nextCard() {
        if (currentIndex < totalCards - 1) { currentIndex++; showCard(currentIndex); }
    }

    function prevCard() {
        if (currentIndex > 0) { currentIndex--; showCard(currentIndex); }
    }

    function flipCard(card) {
        card.classList.toggle('flipped');
    }

    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowLeft') nextCard();
        if (e.key === 'ArrowRight') prevCard();
        if (e.key === ' ') {
            e.preventDefault();
            const currentCard = document.querySelector(`.flashcard[data-index="${currentIndex}"]`);
            if (currentCard) flipCard(currentCard);
        }
    });
</script>
{% endblock %}
{% endblock %}
```

**JavaScript features:**
- **showCard()**: Shows card at given index, hides others, updates counter
- **nextCard()/prevCard()**: Navigation functions
- **flipCard()**: Toggles 'flipped' class for CSS 3D rotation
- **Keyboard support**: Left/Right arrows for navigation, Space to flip

---

## 11. templates/study/quiz_view.html

**Location**: `templates/study/quiz_view.html`
**Purpose**: Interactive quiz with scoring and explanations

```html
{% extends 'base.html' %}

{% block title %}{{ study_set.title|default:'اختبار' }} - مفتاح{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <!-- Header -->
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h4 class="mb-1">
                        <i class="bi bi-question-circle me-2 text-primary"></i>
                        {{ study_set.title|default:'اختبار' }}
                    </h4>
                    <div class="text-muted">
                        {{ questions|length }} سؤال •
                        {% if study_set.language == 'ar' %}العربية{% else %}English{% endif %}
                    </div>
                </div>
                {% if is_owner %}
                <div class="d-flex gap-2">
                    <a href="{% url 'posts:create' %}?study_set={{ study_set.pk }}" class="btn btn-primary">
                        <i class="bi bi-share me-1"></i> مشاركة
                    </a>
                    <a href="{% url 'study:delete' study_set.pk %}" class="btn btn-outline-danger">
                        <i class="bi bi-trash"></i>
                    </a>
                </div>
                {% endif %}
            </div>

            <!-- Score Display (hidden initially) -->
            <div class="card mb-4 d-none" id="score-card">
                <div class="card-body text-center py-4">
                    <h3 class="mb-2">النتيجة النهائية</h3>
                    <div class="display-4 text-primary" id="score-display">0/{{ questions|length }}</div>
                    <button class="btn btn-primary mt-3" onclick="resetQuiz()">
                        <i class="bi bi-arrow-clockwise me-1"></i> إعادة الاختبار
                    </button>
                </div>
            </div>

            <!-- Questions Container -->
            <div id="questions-container">
                {% for q in questions %}
                <div class="card mb-4 question-card" data-question="{{ forloop.counter0 }}" data-correct="{{ q.correct_index }}">
                    <div class="card-header">
                        <span class="badge bg-primary me-2">{{ forloop.counter }}</span>
                        {{ q.question }}
                    </div>
                    <div class="card-body">
                        <div class="options-container">
                            {% for option in q.options %}
                            <div class="quiz-option" data-option="{{ forloop.counter0 }}"
                                 onclick="selectOption(this, {{ forloop.parentloop.counter0 }}, {{ forloop.counter0 }})">
                                <span class="option-letter me-2">
                                    {% if forloop.counter == 1 %}أ{% elif forloop.counter == 2 %}ب{% elif forloop.counter == 3 %}ج{% else %}د{% endif %})
                                </span>
                                {{ option }}
                            </div>
                            {% endfor %}
                        </div>
                        <!-- Explanation (hidden until results shown) -->
                        <div class="explanation mt-3 d-none">
                            <div class="alert alert-info mb-0">
                                <strong><i class="bi bi-lightbulb me-1"></i> الشرح:</strong>
                                <p class="mb-0 mt-2">{{ q.explanation }}</p>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>

            <!-- Submit Button -->
            <div class="text-center mb-4" id="submit-section">
                <button class="btn btn-primary btn-lg" onclick="showResults()">
                    <i class="bi bi-check-circle me-2"></i> عرض النتائج
                </button>
            </div>
        </div>
    </div>
</div>

{% block extra_js %}
<script>
    const answers = {};
    const totalQuestions = {{ questions|length }};

    function selectOption(element, questionIndex, optionIndex) {
        const questionCard = element.closest('.question-card');
        if (questionCard.classList.contains('answered')) return;

        // Clear previous selection
        element.parentElement.querySelectorAll('.quiz-option').forEach(opt => opt.classList.remove('selected'));
        element.classList.add('selected');
        answers[questionIndex] = optionIndex;
    }

    function showResults() {
        let score = 0;
        document.querySelectorAll('.question-card').forEach((card, index) => {
            const correctIndex = parseInt(card.dataset.correct);
            const selectedIndex = answers[index];
            const options = card.querySelectorAll('.quiz-option');

            card.classList.add('answered');
            options.forEach((opt, optIndex) => {
                if (optIndex === correctIndex) opt.classList.add('correct');
                else if (optIndex === selectedIndex && selectedIndex !== correctIndex) opt.classList.add('incorrect');
            });
            if (selectedIndex === correctIndex) score++;
            card.querySelector('.explanation').classList.remove('d-none');
        });

        document.getElementById('score-display').textContent = `${score}/${totalQuestions}`;
        document.getElementById('score-card').classList.remove('d-none');
        document.getElementById('submit-section').classList.add('d-none');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function resetQuiz() {
        Object.keys(answers).forEach(key => delete answers[key]);
        document.querySelectorAll('.question-card').forEach(card => {
            card.classList.remove('answered');
            card.querySelectorAll('.quiz-option').forEach(opt => opt.classList.remove('selected', 'correct', 'incorrect'));
            card.querySelector('.explanation').classList.add('d-none');
        });
        document.getElementById('score-card').classList.add('d-none');
        document.getElementById('submit-section').classList.remove('d-none');
    }
</script>
{% endblock %}
{% endblock %}
```

---

## 12. templates/study/history.html

**Location**: `templates/study/history.html`
**Purpose**: Display user's saved study sets with filter options

```html
{% extends 'base.html' %}

{% block title %}السجل - مفتاح{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-lg-10">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h4 class="mb-0">
                    <i class="bi bi-clock-history me-2"></i>
                    سجل المجموعات الدراسية
                </h4>

                <!-- Type Filter -->
                <div class="btn-group">
                    <a href="{% url 'study:history' %}"
                       class="btn btn-outline-secondary {% if not current_type %}active{% endif %}">
                        الكل
                    </a>
                    <a href="{% url 'study:history' %}?type=flashcards"
                       class="btn btn-outline-secondary {% if current_type == 'flashcards' %}active{% endif %}">
                        <i class="bi bi-stack me-1"></i> بطاقات
                    </a>
                    <a href="{% url 'study:history' %}?type=quiz"
                       class="btn btn-outline-secondary {% if current_type == 'quiz' %}active{% endif %}">
                        <i class="bi bi-question-circle me-1"></i> اختبارات
                    </a>
                </div>
            </div>

            {% if study_sets %}
            <div class="row g-3">
                {% for study_set in study_sets %}
                <div class="col-md-6">
                    <div class="card study-card h-100">
                        <div class="card-body">
                            <!-- Badges row -->
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <div>
                                    {% if study_set.set_type == 'flashcards' %}
                                    <span class="badge bg-primary">
                                        <i class="bi bi-stack me-1"></i> بطاقات
                                    </span>
                                    {% else %}
                                    <span class="badge bg-success">
                                        <i class="bi bi-question-circle me-1"></i> اختبار
                                    </span>
                                    {% endif %}
                                    <span class="badge bg-secondary">
                                        {% if study_set.language == 'ar' %}العربية{% else %}English{% endif %}
                                    </span>
                                    {% if study_set.is_shared %}
                                    <span class="badge bg-info"><i class="bi bi-share"></i> مُشارك</span>
                                    {% endif %}
                                </div>
                                <small class="text-muted">{{ study_set.created_at|date:"Y/m/d" }}</small>
                            </div>

                            <h6 class="card-title">{{ study_set.title|default:'بدون عنوان' }}</h6>
                            <p class="text-muted small mb-3">
                                {{ study_set.item_count }}
                                {% if study_set.set_type == 'flashcards' %}بطاقة{% else %}سؤال{% endif %}
                            </p>

                            <!-- Action buttons -->
                            <div class="d-flex gap-2">
                                <a href="{% url 'study:detail' study_set.pk %}" class="btn btn-primary btn-sm">
                                    <i class="bi bi-eye me-1"></i> عرض
                                </a>
                                <a href="{% url 'posts:create' %}?study_set={{ study_set.pk }}"
                                   class="btn btn-outline-primary btn-sm">
                                    <i class="bi bi-share me-1"></i> مشاركة
                                </a>
                                <a href="{% url 'study:delete' study_set.pk %}"
                                   class="btn btn-outline-danger btn-sm me-auto">
                                    <i class="bi bi-trash"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <div class="empty-state">
                <i class="bi bi-folder2-open"></i>
                <p>لا توجد مجموعات دراسية حتى الآن</p>
                <div class="d-flex gap-2 justify-content-center">
                    <a href="{% url 'study:generate' 'flashcards' %}" class="btn btn-primary">
                        <i class="bi bi-stack me-1"></i> إنشاء بطاقات
                    </a>
                    <a href="{% url 'study:generate' 'quiz' %}" class="btn btn-outline-primary">
                        <i class="bi bi-question-circle me-1"></i> إنشاء اختبار
                    </a>
                </div>
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

---

## 13. templates/posts/create.html

**Location**: `templates/posts/create.html`
**Purpose**: Form to create a new post sharing a study set

```html
{% extends 'base.html' %}

{% block title %}نشر جديد - مفتاح{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">
                        <i class="bi bi-pencil-square me-2"></i>
                        نشر جديد
                    </h5>
                </div>
                <div class="card-body">
                    {% if not study_sets %}
                    <!-- No study sets - show warning -->
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        لا توجد لديك مجموعات دراسية. يجب إنشاء مجموعة أولاً.
                        <div class="mt-2">
                            <a href="{% url 'study:generate' 'flashcards' %}" class="btn btn-primary btn-sm">إنشاء بطاقات</a>
                            <a href="{% url 'study:generate' 'quiz' %}" class="btn btn-outline-primary btn-sm">إنشاء اختبار</a>
                        </div>
                    </div>
                    {% else %}
                    <form method="post">
                        {% csrf_token %}

                        <!-- Study Set Selection Dropdown -->
                        <div class="mb-3">
                            <label class="form-label">
                                <i class="bi bi-collection me-1"></i>
                                المجموعة الدراسية (مطلوب)
                            </label>
                            <select name="study_set" class="form-select" required>
                                <option value="">اختر مجموعة...</option>
                                {% for ss in study_sets %}
                                <option value="{{ ss.pk }}" {% if preselected_study_set.pk == ss.pk %}selected{% endif %}>
                                    {% if ss.set_type == 'flashcards' %}📚{% else %}❓{% endif %}
                                    {{ ss.title|default:'بدون عنوان' }}
                                    ({{ ss.item_count }} {% if ss.set_type == 'flashcards' %}بطاقة{% else %}سؤال{% endif %})
                                </option>
                                {% endfor %}
                            </select>
                        </div>

                        <!-- Title -->
                        <div class="mb-3">
                            <label class="form-label">{{ form.title.label }} (مطلوب)</label>
                            {{ form.title }}
                        </div>

                        <!-- Tags Selection with search -->
                        <div class="mb-3">
                            <label class="form-label">
                                <i class="bi bi-tags me-1"></i>
                                التصنيفات (مطلوب)
                            </label>
                            <div class="form-text mb-2">اختر من 1 إلى 4 تصنيفات</div>
                            <div id="selected-tags" class="d-flex flex-wrap gap-2 mb-2"></div>
                            <input type="text" id="tag-search" class="form-control mb-2" placeholder="ابحث عن تصنيف...">
                            <div id="tags-container" class="border rounded p-3" style="max-height: 300px; overflow-y: auto;">
                                {% for tag in all_tags %}
                                <div class="tag-item d-inline-block m-1" data-tag-name="{{ tag.name|lower }}" data-tag-color="{{ tag.color }}">
                                    <input type="checkbox" name="tags" value="{{ tag.pk }}" id="tag-{{ tag.pk }}" class="d-none tag-checkbox">
                                    <label for="tag-{{ tag.pk }}" class="tag-chip badge rounded-pill px-3 py-2"
                                           style="cursor: pointer; background-color: #e9ecef; color: #495057;">
                                        {{ tag.name }}
                                    </label>
                                </div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Caption (optional) -->
                        <div class="mb-3">
                            <label class="form-label">{{ form.caption.label }}</label>
                            {{ form.caption }}
                        </div>

                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-send me-1"></i> نشر
                        </button>
                    </form>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('tag-search');
    const maxTags = 4;

    // Tag search filtering
    searchInput.addEventListener('input', function() {
        const query = this.value.trim().toLowerCase();
        document.querySelectorAll('.tag-item').forEach(item => {
            item.style.display = item.dataset.tagName.includes(query) ? 'inline-block' : 'none';
        });
    });

    // Tag selection with max limit
    document.querySelectorAll('.tag-checkbox').forEach(cb => {
        cb.addEventListener('change', updateTagStyles);
    });

    function updateTagStyles() {
        let selectedCount = 0;
        document.querySelectorAll('.tag-checkbox').forEach(cb => {
            const label = document.querySelector(`label[for="${cb.id}"]`);
            const color = cb.closest('.tag-item').dataset.tagColor;
            if (cb.checked) {
                selectedCount++;
                label.style.backgroundColor = color;
                label.style.color = '#ffffff';
            } else {
                label.style.backgroundColor = '#e9ecef';
                label.style.color = '#495057';
            }
        });
        // Disable unchecked if max reached
        document.querySelectorAll('.tag-checkbox').forEach(cb => {
            const label = document.querySelector(`label[for="${cb.id}"]`);
            label.style.opacity = (!cb.checked && selectedCount >= maxTags) ? '0.5' : '1';
            label.style.pointerEvents = (!cb.checked && selectedCount >= maxTags) ? 'none' : 'auto';
        });
    }
});
</script>
{% endblock %}
```

---

## 14. templates/posts/detail.html

**Location**: `templates/posts/detail.html`
**Purpose**: Full post view with reactions and comments

```html
{% extends 'base.html' %}

{% block title %}{{ post.title }} - مفتاح{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <!-- Post Card -->
            <div class="card mb-4">
                <div class="card-header">
                    <!-- Tags -->
                    <div class="mb-2">
                        {% for tag in post.tags.all %}
                        <span class="tag-badge" style="background-color: {{ tag.color }}">{{ tag.name }}</span>
                        {% endfor %}
                    </div>
                    <h4 class="mb-0">{{ post.title }}</h4>
                </div>

                <div class="card-body">
                    <!-- Author Info -->
                    <div class="d-flex align-items-center gap-2 mb-3">
                        <i class="bi bi-person-circle fs-4 text-primary"></i>
                        <div>
                            <a href="{% url 'accounts:profile' post.author.username %}" class="text-decoration-none">
                                <strong>{{ post.author.username }}</strong>
                            </a>
                            <div class="text-muted small">{{ post.created_at|date:"Y/m/d - H:i" }}</div>
                        </div>
                    </div>

                    <!-- Caption -->
                    {% if post.caption %}
                    <p class="mb-3">{{ post.caption }}</p>
                    {% endif %}

                    <!-- Study Set Preview -->
                    <div class="card bg-light mb-3">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    {% if post.study_set.set_type == 'flashcards' %}
                                    <span class="badge bg-primary me-2">
                                        <i class="bi bi-stack me-1"></i> بطاقات تعليمية
                                    </span>
                                    {% else %}
                                    <span class="badge bg-success me-2">
                                        <i class="bi bi-question-circle me-1"></i> اختبار
                                    </span>
                                    {% endif %}
                                    <span class="text-muted">{{ post.study_set.item_count }} {% if post.study_set.set_type == 'flashcards' %}بطاقة{% else %}سؤال{% endif %}</span>
                                </div>
                                <a href="{% url 'study:detail' post.study_set.pk %}" class="btn btn-primary btn-sm">
                                    <i class="bi bi-eye me-1"></i> عرض المحتوى
                                </a>
                            </div>
                        </div>
                    </div>

                    <!-- Reactions (HTMX-powered) -->
                    <div id="reaction-buttons">
                        {% include 'posts/partials/reaction_buttons.html' %}
                    </div>

                    <!-- Actions: Delete or Report -->
                    <div class="mt-3 pt-3 border-top d-flex gap-2">
                        {% if is_owner %}
                        <form method="post" action="{% url 'posts:delete' post.pk %}"
                              onsubmit="return confirm('هل أنت متأكد من حذف هذا المنشور؟')">
                            {% csrf_token %}
                            <button type="submit" class="btn btn-outline-danger btn-sm">
                                <i class="bi bi-trash me-1"></i> حذف المنشور
                            </button>
                        </form>
                        {% else %}
                        <button type="button" class="btn btn-outline-secondary btn-sm"
                                data-bs-toggle="modal" data-bs-target="#reportModal">
                            <i class="bi bi-flag me-1"></i> إبلاغ
                        </button>
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- Comments Section -->
            <div class="card">
                <div class="card-header">
                    <h6 class="mb-0">
                        <i class="bi bi-chat-dots me-2"></i>
                        التعليقات ({{ comments|length }})
                    </h6>
                </div>
                <div class="card-body">
                    <!-- Add Comment Form -->
                    <form method="post" class="mb-4">
                        {% csrf_token %}
                        <div class="d-flex gap-2">
                            {{ comment_form.body }}
                            <button type="submit" class="btn btn-primary"><i class="bi bi-send"></i></button>
                        </div>
                    </form>

                    <!-- Comments List -->
                    {% if comments %}
                    <div class="comments-list">
                        {% for comment in comments %}
                        <div class="d-flex gap-3 mb-3 pb-3 border-bottom" id="comment-{{ comment.pk }}">
                            <i class="bi bi-person-circle fs-4 text-secondary"></i>
                            <div class="flex-grow-1">
                                <div class="d-flex justify-content-between align-items-start">
                                    <div>
                                        <a href="{% url 'accounts:profile' comment.author.username %}" class="fw-bold text-decoration-none">
                                            {{ comment.author.username }}
                                        </a>
                                        <span class="text-muted small me-2">{{ comment.created_at|date:"Y/m/d - H:i" }}</span>
                                    </div>
                                    <div class="d-flex gap-1">
                                        {% if comment.author != request.user %}
                                        <button class="btn btn-sm btn-outline-secondary"
                                                data-bs-toggle="modal" data-bs-target="#reportModal-{{ comment.pk }}">
                                            <i class="bi bi-flag"></i>
                                        </button>
                                        {% endif %}
                                        {% if comment.author == request.user %}
                                        <button class="btn btn-sm btn-outline-danger"
                                                hx-post="{% url 'posts:delete_comment' comment.pk %}"
                                                hx-target="#comment-{{ comment.pk }}"
                                                hx-swap="outerHTML"
                                                hx-confirm="هل أنت متأكد من حذف هذا التعليق؟">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                        {% endif %}
                                    </div>
                                </div>
                                <p class="mb-0 mt-1">{{ comment.body }}</p>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <div class="text-center text-muted py-3">
                        <i class="bi bi-chat-dots fs-1"></i>
                        <p>لا توجد تعليقات. كن أول من يعلق!</p>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Report Modal for Post -->
{% if not is_owner %}
{% include 'admin_panel/partials/report_modal.html' with content_type='post' object_id=post.pk %}
{% endif %}

<!-- Report Modals for Comments -->
{% for comment in comments %}
{% if comment.author != request.user %}
{% include 'admin_panel/partials/report_modal.html' with content_type='comment' object_id=comment.pk modal_id=comment.pk %}
{% endif %}
{% endfor %}
{% endblock %}
```

---

## 15. templates/posts/partials/post_card.html

**Location**: `templates/posts/partials/post_card.html`
**Purpose**: Reusable post card component for feed/profile listings

```html
<div class="card study-card position-relative">
    <div class="card-body">
        <!-- Tags Row -->
        <div class="mb-2">
            {% for tag in post.tags.all %}
            <span class="tag-badge" style="background-color: {{ tag.color }}; font-size: 0.75rem;">
                {{ tag.name }}
            </span>
            {% endfor %}
        </div>

        <!-- Title with stretched-link makes whole card clickable -->
        <h5 class="card-title mb-2">
            <a href="{% url 'posts:detail' post.pk %}" class="text-decoration-none text-dark stretched-link">
                {{ post.title }}
            </a>
        </h5>

        <!-- Author & Date (z-index to make clickable above stretched-link) -->
        <div class="d-flex align-items-center gap-2 mb-2 text-muted small position-relative" style="z-index: 2;">
            <a href="{% url 'accounts:profile' post.author.username %}" class="text-decoration-none">
                <i class="bi bi-person-circle me-1"></i>
                {{ post.author.username }}
            </a>
            <span>•</span>
            <span>{{ post.created_at|date:"Y/m/d" }}</span>
        </div>

        <!-- Caption Preview -->
        {% if post.caption %}
        <p class="text-muted small mb-2">{{ post.caption|truncatechars:100 }}</p>
        {% endif %}

        <!-- Study Set Badge + Quick Reactions -->
        <div class="d-flex align-items-center justify-content-between">
            <div>
                {% if post.study_set.set_type == 'flashcards' %}
                <span class="badge bg-primary">
                    <i class="bi bi-stack me-1"></i>
                    {{ post.study_set.item_count }} بطاقة
                </span>
                {% else %}
                <span class="badge bg-success">
                    <i class="bi bi-question-circle me-1"></i>
                    {{ post.study_set.item_count }} سؤال
                </span>
                {% endif %}
            </div>
            <div class="d-flex gap-2 text-muted small">
                <span><i class="bi bi-hand-thumbs-up me-1"></i>{{ post.likes_count }}</span>
                <span><i class="bi bi-hand-thumbs-down me-1"></i>{{ post.dislikes_count }}</span>
                <span><i class="bi bi-chat me-1"></i>{{ post.comments.count }}</span>
            </div>
        </div>
    </div>
</div>
```

---

## 16. templates/posts/partials/reaction_buttons.html

**Location**: `templates/posts/partials/reaction_buttons.html`
**Purpose**: HTMX-powered like/dislike buttons

```html
<div class="d-flex gap-3">
    <!-- Like Button -->
    <button type="button"
            class="reaction-btn {% if user_reaction == 'like' %}active-like{% endif %}"
            hx-post="{% url 'posts:react' post.pk %}"
            hx-vals='{"type": "like"}'
            hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'
            hx-target="#reaction-buttons"
            hx-swap="innerHTML">
        <i class="bi bi-hand-thumbs-up{% if user_reaction == 'like' %}-fill{% endif %}"></i>
        <span>{{ post.likes_count }}</span>
    </button>

    <!-- Dislike Button -->
    <button type="button"
            class="reaction-btn {% if user_reaction == 'dislike' %}active-dislike{% endif %}"
            hx-post="{% url 'posts:react' post.pk %}"
            hx-vals='{"type": "dislike"}'
            hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'
            hx-target="#reaction-buttons"
            hx-swap="innerHTML">
        <i class="bi bi-hand-thumbs-down{% if user_reaction == 'dislike' %}-fill{% endif %}"></i>
        <span>{{ post.dislikes_count }}</span>
    </button>
</div>
```

**HTMX attributes:**
- `hx-post`: POST to react endpoint
- `hx-vals`: Send reaction type (like/dislike)
- `hx-target`: Replace the buttons container
- `hx-swap`: Replace innerHTML with new state

---

## 17. templates/posts/feed.html

**Location**: `templates/posts/feed.html`
**Purpose**: Feed page with tabs for recent/following posts

```html
{% extends 'base.html' %}

{% block title %}{% if feed_type == 'recent' %}الأحدث{% else %}المتابَعون{% endif %} - مفتاح{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <!-- Search Bar with Tag Filters -->
            <form action="" method="get" class="mb-4">
                <div class="input-group">
                    <input type="text" name="q" class="form-control" value="{{ query }}" placeholder="ابحث في المنشورات...">
                    <button type="submit" class="btn btn-primary"><i class="bi bi-search"></i></button>
                </div>
                {% if all_tags %}
                <div class="mt-2">
                    <small class="text-muted me-2">تصفية بالوسوم:</small>
                    {% for tag in all_tags %}
                    <div class="form-check form-check-inline">
                        <input type="checkbox" class="form-check-input" name="tags" value="{{ tag.name }}"
                               id="tag-{{ tag.pk }}" {% if tag.name in tag_filter %}checked{% endif %} onchange="this.form.submit()">
                        <label class="form-check-label" for="tag-{{ tag.pk }}" style="color: {{ tag.color }}">{{ tag.name }}</label>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
            </form>

            <!-- Feed Type Tabs -->
            <ul class="nav nav-tabs mb-4">
                <li class="nav-item">
                    <a class="nav-link {% if feed_type == 'recent' %}active{% endif %}" href="{% url 'feed:recent' %}">
                        <i class="bi bi-clock me-1"></i> الأحدث
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link {% if feed_type == 'following' %}active{% endif %}" href="{% url 'feed:following' %}">
                        <i class="bi bi-people me-1"></i> المتابَعون
                    </a>
                </li>
            </ul>

            <!-- Posts List -->
            {% if posts %}
            <div class="row g-3">
                {% for post in posts %}
                <div class="col-12">{% include 'posts/partials/post_card.html' %}</div>
                {% endfor %}
            </div>
            {% else %}
            <div class="empty-state">
                <i class="bi bi-file-earmark-text"></i>
                {% if feed_type == 'following' %}
                <p>{% if following_count == 0 %}أنت لا تتابع أحداً حتى الآن{% else %}لا توجد منشورات من المتابَعين{% endif %}</p>
                {% else %}
                <p>لا توجد منشورات</p>
                {% endif %}
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

---

## 18. templates/admin_panel/base_admin.html

**Location**: `templates/admin_panel/base_admin.html`
**Purpose**: Admin panel layout with sidebar navigation

```html
{% extends 'base.html' %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <!-- Sidebar Navigation -->
        <nav class="col-md-3 col-lg-2 d-md-block bg-light sidebar py-3 border-end" style="min-height: calc(100vh - 80px);">
            <div class="position-sticky">
                <h6 class="sidebar-heading px-3 mb-3 text-muted d-flex align-items-center">
                    <i class="bi bi-shield-check me-2"></i>
                    لوحة الإدارة
                </h6>
                <ul class="nav flex-column">
                    <li class="nav-item">
                        <a class="nav-link {% if request.resolver_match.url_name == 'dashboard' %}active text-primary fw-bold{% endif %}"
                           href="{% url 'admin_panel:dashboard' %}">
                            <i class="bi bi-speedometer2 me-2"></i> الإحصائيات
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if 'reports' in request.path %}active text-primary fw-bold{% endif %}"
                           href="{% url 'admin_panel:reports_list' %}">
                            <i class="bi bi-flag me-2"></i> البلاغات
                            {% if pending_reports_count %}
                            <span class="badge bg-danger rounded-pill ms-2">{{ pending_reports_count }}</span>
                            {% endif %}
                        </a>
                    </li>
                </ul>
                <hr class="my-3">
                <ul class="nav flex-column">
                    <li class="nav-item">
                        <a class="nav-link text-muted" href="{% url 'home' %}">
                            <i class="bi bi-arrow-right me-2"></i> العودة للموقع
                        </a>
                    </li>
                </ul>
            </div>
        </nav>

        <!-- Main Content Area -->
        <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 py-4">
            {% block admin_content %}{% endblock %}
        </main>
    </div>
</div>
{% endblock %}
```

---

## 19. templates/admin_panel/dashboard.html

**Location**: `templates/admin_panel/dashboard.html`
**Purpose**: Admin dashboard with platform statistics

```html
{% extends 'admin_panel/base_admin.html' %}

{% block title %}لوحة الإدارة - مفتاح{% endblock %}

{% block admin_content %}
<h4 class="mb-4"><i class="bi bi-speedometer2 me-2"></i> الإحصائيات</h4>

<!-- Stats Cards Row 1 -->
<div class="row g-4 mb-4">
    <div class="col-md-4">
        <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
                <div class="d-flex align-items-center">
                    <div class="rounded-circle bg-primary bg-opacity-10 p-3 me-3">
                        <i class="bi bi-people fs-4 text-primary"></i>
                    </div>
                    <div>
                        <h3 class="mb-0">{{ total_users }}</h3>
                        <small class="text-muted">إجمالي المستخدمين</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
                <div class="d-flex align-items-center">
                    <div class="rounded-circle bg-success bg-opacity-10 p-3 me-3">
                        <i class="bi bi-file-post fs-4 text-success"></i>
                    </div>
                    <div>
                        <h3 class="mb-0">{{ total_posts }}</h3>
                        <small class="text-muted">إجمالي المنشورات</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
                <div class="d-flex align-items-center">
                    <div class="rounded-circle bg-info bg-opacity-10 p-3 me-3">
                        <i class="bi bi-chat-dots fs-4 text-info"></i>
                    </div>
                    <div>
                        <h3 class="mb-0">{{ total_comments }}</h3>
                        <small class="text-muted">إجمالي التعليقات</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Stats Cards Row 2 -->
<div class="row g-4 mb-4">
    <div class="col-md-4">
        <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
                <div class="d-flex align-items-center">
                    <div class="rounded-circle bg-warning bg-opacity-10 p-3 me-3">
                        <i class="bi bi-clock-history fs-4 text-warning"></i>
                    </div>
                    <div>
                        <h3 class="mb-0">{{ posts_24h }}</h3>
                        <small class="text-muted">منشورات آخر 24 ساعة</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
                <div class="d-flex align-items-center">
                    <div class="rounded-circle bg-secondary bg-opacity-10 p-3 me-3">
                        <i class="bi bi-calendar-week fs-4 text-secondary"></i>
                    </div>
                    <div>
                        <h3 class="mb-0">{{ posts_7d }}</h3>
                        <small class="text-muted">منشورات آخر 7 أيام</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
                <div class="d-flex align-items-center">
                    <div class="rounded-circle bg-danger bg-opacity-10 p-3 me-3">
                        <i class="bi bi-flag fs-4 text-danger"></i>
                    </div>
                    <div>
                        <h3 class="mb-0">{{ pending_reports_count }}</h3>
                        <small class="text-muted">بلاغات قيد المراجعة</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Top Posts & Tags -->
<div class="row g-4">
    <div class="col-md-6">
        <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-0">
                <h6 class="mb-0"><i class="bi bi-heart me-2 text-danger"></i> أكثر المنشورات إعجاباً</h6>
            </div>
            <div class="card-body">
                {% if top_posts %}
                <ul class="list-group list-group-flush">
                    {% for post in top_posts %}
                    <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                        <div class="text-truncate me-2">
                            <a href="{% url 'posts:detail' post.pk %}">{{ post.title }}</a>
                            <small class="text-muted d-block">{{ post.author.username }}</small>
                        </div>
                        <span class="badge bg-danger rounded-pill">
                            <i class="bi bi-heart-fill me-1"></i>{{ post.like_count }}
                        </span>
                    </li>
                    {% endfor %}
                </ul>
                {% else %}
                <p class="text-muted text-center mb-0">لا توجد منشورات بعد</p>
                {% endif %}
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-0">
                <h6 class="mb-0"><i class="bi bi-tags me-2 text-primary"></i> أكثر التصنيفات استخداماً</h6>
            </div>
            <div class="card-body">
                {% if top_tags %}
                <div class="d-flex flex-wrap gap-2">
                    {% for tag in top_tags %}
                    <span class="badge rounded-pill px-3 py-2" style="background-color: {{ tag.color }};">
                        {{ tag.name }}
                        <span class="badge bg-light text-dark ms-1">{{ tag.post_count }}</span>
                    </span>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- Recent Reports Table -->
{% if recent_reports %}
<div class="card border-0 shadow-sm mt-4">
    <div class="card-header bg-white border-0 d-flex justify-content-between align-items-center">
        <h6 class="mb-0"><i class="bi bi-flag me-2 text-danger"></i> أحدث البلاغات</h6>
        <a href="{% url 'admin_panel:reports_list' %}" class="btn btn-sm btn-outline-primary">عرض الكل</a>
    </div>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-hover mb-0">
                <thead class="table-light">
                    <tr><th>#</th><th>المُبلِّغ</th><th>النوع</th><th>السبب</th><th>التاريخ</th><th></th></tr>
                </thead>
                <tbody>
                    {% for report in recent_reports %}
                    <tr>
                        <td>{{ report.pk }}</td>
                        <td>{{ report.reporter.username }}</td>
                        <td>{{ report.get_content_type_display_ar }}</td>
                        <td><span class="badge bg-warning text-dark">{{ report.get_reason_display }}</span></td>
                        <td>{{ report.created_at|date:"Y/m/d H:i" }}</td>
                        <td><a href="{% url 'admin_panel:report_detail' report.pk %}" class="btn btn-sm btn-outline-primary">عرض</a></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endif %}
{% endblock %}
```

---

## 20. templates/admin_panel/reports/list.html & detail.html

**Location**: `templates/admin_panel/reports/list.html`
**Purpose**: Filterable list of all reports

Key features:
- Status filter tabs (pending/approved/dismissed/all)
- Table with reporter, content type, reason, status, date
- Link to detail view for each report

**Location**: `templates/admin_panel/reports/detail.html`
**Purpose**: Single report view with approve/dismiss actions

Key features:
- Report details (reporter, date, reason, details)
- Reported content preview (post title/caption or comment body)
- Action buttons for pending reports:
  - "قبول البلاغ وحذف المحتوى" (Approve and delete content)
  - "رفض البلاغ" (Dismiss report)

---

## 21. templates/admin_panel/partials/report_modal.html

**Location**: `templates/admin_panel/partials/report_modal.html`
**Purpose**: Bootstrap modal for submitting reports (used in post detail)

```html
<!-- Report Modal -->
<div class="modal fade" id="reportModal{% if modal_id %}-{{ modal_id }}{% endif %}" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="bi bi-flag me-2"></i> الإبلاغ عن محتوى
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form hx-post="{% url 'admin_panel:submit_report' %}"
                  hx-target="#report-result{% if modal_id %}-{{ modal_id }}{% endif %}"
                  hx-swap="innerHTML"
                  hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
                {% csrf_token %}
                <input type="hidden" name="content_type" value="{{ content_type }}">
                <input type="hidden" name="object_id" value="{{ object_id }}">

                <div class="modal-body">
                    <div id="report-result{% if modal_id %}-{{ modal_id }}{% endif %}"></div>

                    <div class="mb-3">
                        <label class="form-label">سبب البلاغ <span class="text-danger">*</span></label>
                        <select name="reason" class="form-select" required>
                            <option value="">اختر السبب...</option>
                            <option value="hate_speech">خطاب كراهية</option>
                            <option value="spam">محتوى مزعج (سبام)</option>
                            <option value="inappropriate">محتوى غير لائق</option>
                            <option value="misinformation">معلومات مضللة</option>
                            <option value="harassment">تحرش أو إساءة</option>
                            <option value="other">أخرى</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">تفاصيل إضافية (اختياري)</label>
                        <textarea name="details" class="form-control" rows="3"
                                  placeholder="أضف أي تفاصيل تساعد في فهم البلاغ..."></textarea>
                    </div>
                </div>

                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                    <button type="submit" class="btn btn-danger">
                        <i class="bi bi-flag me-1"></i> إرسال البلاغ
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
```

**Usage**: Include with `{% include 'admin_panel/partials/report_modal.html' with content_type='post' object_id=post.pk %}`

---

# DATABASE SCHEMA

## Tables:

### auth_user (Django built-in)
- id, username, email, password, is_staff, is_superuser, etc.

### accounts_profile
- id, user_id (FK), bio, created_at

### accounts_follow
- id, follower_id (FK), following_id (FK), created_at
- UNIQUE(follower_id, following_id)
- CHECK(follower_id != following_id)

### study_studyset
- id, owner_id (FK), set_type, language, title, source_text, created_at

### study_flashcard
- id, study_set_id (FK), index, question, answer
- UNIQUE(study_set_id, index)

### study_quizquestion
- id, study_set_id (FK), index, question, options (JSON), correct_index, explanation
- UNIQUE(study_set_id, index)

### posts_tag
- id, name (UNIQUE), color

### posts_post
- id, author_id (FK), study_set_id (FK), title, caption, created_at, deleted_at

### posts_posttag
- id, post_id (FK), tag_id (FK)
- UNIQUE(post_id, tag_id)

### posts_reaction
- id, user_id (FK), post_id (FK), value, created_at
- UNIQUE(user_id, post_id)

### posts_comment
- id, post_id (FK), author_id (FK), body, created_at, deleted_at

### admin_panel_report
- id, reporter_id (FK), content_type_id (FK), object_id, reason, details, status, reviewed_by_id (FK), reviewed_at, created_at
- UNIQUE(reporter_id, content_type_id, object_id)

---

# FILE RELATIONSHIPS

## Request Flow Example: Creating a Post

1. User visits `/posts/new/`
2. `miftah/urls.py` routes to `posts.urls`
3. `posts/urls.py` routes to `posts.views.create_post`
4. `create_post` view:
   - Gets user's study sets from `study.models.StudySet`
   - Gets all tags from `posts.models.Tag`
   - Renders `templates/posts/create.html`
5. User submits form
6. View creates `posts.models.Post` with:
   - Author (from `request.user`)
   - StudySet (selected)
   - Tags (through `posts.models.PostTag`)
7. Redirect to `posts.views.post_detail`

## Data Flow: AI Study Set Generation

1. User submits text/PDF on generate page
2. `study.views.generate_view` receives request
3. If PDF: `study.ai_service.extract_text_from_pdf` extracts text
4. `study.ai_service.detect_language` determines language
5. `study.ai_service.generate_flashcards/quiz` calls DeepSeek API
6. View creates `study.models.StudySet` and child records
7. Redirect to detail view

---

# COMMANDS REFERENCE

```bash
# Start the application
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Seed tags
docker-compose exec web python manage.py seed_tags

# Make user staff
docker-compose exec web python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(username='admin').update(is_staff=True)
```

---

This concludes the complete documentation of every file in the Miftah project.
