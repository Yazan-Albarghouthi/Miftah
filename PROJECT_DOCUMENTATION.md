# Miftah Project - Complete Technical Documentation

> **Last Updated:** January 2026
> **Purpose:** This document provides a comprehensive explanation of every file, component, and relationship in the Miftah project. Written for someone who has never seen this codebase before.

---

# Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack Explained](#2-technology-stack-explained)
3. [Project Architecture](#3-project-architecture)
4. [Docker Configuration](#4-docker-configuration)
5. [Django Project Configuration (miftah/)](#5-django-project-configuration-miftah)
6. [Accounts App - Authentication & Social](#6-accounts-app---authentication--social)
7. [Study App - AI-Powered Learning](#7-study-app---ai-powered-learning)
8. [Posts App - Social Sharing](#8-posts-app---social-sharing)
9. [Feed App - Content Discovery](#9-feed-app---content-discovery)
10. [Admin Panel App - Moderation](#10-admin-panel-app---moderation)
11. [Templates - The UI Layer](#11-templates---the-ui-layer)
12. [Database Schema](#12-database-schema)
13. [URL Routing System](#13-url-routing-system)
14. [Data Flow Examples](#14-data-flow-examples)
15. [File-by-File Reference](#15-file-by-file-reference)

---

# 1. Project Overview

## What is Miftah?

**Miftah** (Arabic: مفتاح, meaning "Key") is an educational web platform designed for Arab students. It allows users to:

1. **Generate AI-powered study materials** - Convert any text or PDF into flashcards or quizzes using the DeepSeek AI API
2. **Share educational content** - Post study sets with tags for others to discover and use
3. **Follow other students** - Build a social network and see posts from people you follow
4. **Interact with content** - Like/dislike posts, comment, and report inappropriate content
5. **Moderate the platform** - Staff members can review reports and manage content

## Core Concepts

### Study Sets
A **StudySet** is the fundamental unit of educational content. It can be either:
- **Flashcards**: Question/answer pairs for memorization (flip cards)
- **Quiz**: Multiple choice questions with explanations

### Posts
A **Post** shares a StudySet with the community. Posts:
- Must include exactly one StudySet (no standalone text posts)
- Must have 1-4 tags from predefined categories
- Can receive likes/dislikes and comments

### The Arabic-First Design
The entire UI is in Arabic with Right-to-Left (RTL) layout. The AI generates content in the same language as the input - Arabic input produces Arabic flashcards/quizzes, English input produces English content.

---

# 2. Technology Stack Explained

## Backend: Django 5

**Django** is a Python web framework that follows the Model-View-Template (MVT) pattern:
- **Models**: Define database tables as Python classes
- **Views**: Handle HTTP requests and return responses
- **Templates**: HTML files with Django template language for dynamic content

Django provides:
- Built-in user authentication
- ORM (Object-Relational Mapping) for database operations
- Admin interface
- Form handling and validation
- Security features (CSRF, XSS protection)

## Database: PostgreSQL 16

PostgreSQL is a relational database running in a Docker container. It stores:
- User accounts and profiles
- Study sets, flashcards, and quiz questions
- Posts, comments, and reactions
- Follow relationships
- Reports

## Frontend: Bootstrap 5 RTL + HTMX

**Bootstrap 5 RTL** provides:
- Pre-built CSS components (cards, buttons, forms)
- Right-to-left support for Arabic text
- Responsive grid system

**HTMX** enables:
- AJAX requests without writing JavaScript
- Partial page updates (e.g., like button changes without page reload)
- Form submission with dynamic responses

## AI: DeepSeek API

**DeepSeek** is the AI service (similar to OpenAI) that:
- Analyzes input text
- Generates flashcards with questions and answers
- Creates multiple-choice quiz questions with explanations
- Detects the input language and responds in the same language

## Containerization: Docker

**Docker** packages the application into isolated containers:
- **web**: The Django application
- **db**: PostgreSQL database

This ensures consistent environments across development and deployment.

---

# 3. Project Architecture

## Directory Structure Overview

```
graduation_project/
├── miftah/                 # Django project configuration
├── accounts/               # User authentication & profiles
├── study/                  # AI-generated study materials
├── posts/                  # Social posting & interactions
├── feed/                   # (URLs only - views in posts/)
├── admin_panel/            # Staff dashboard & moderation
├── templates/              # HTML templates
├── docker-compose.yml      # Docker services definition
├── Dockerfile              # Django container build
├── entrypoint.sh           # Container startup script
├── manage.py               # Django CLI
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables
```

## How Django Apps Work Together

```
                    ┌─────────────────────────────────────────────────────┐
                    │                  HTTP Request                        │
                    └─────────────────────┬───────────────────────────────┘
                                          │
                                          ▼
                    ┌─────────────────────────────────────────────────────┐
                    │              miftah/urls.py (Root Router)            │
                    │                                                       │
                    │  /accounts/  → accounts.urls                          │
                    │  /study/     → study.urls                             │
                    │  /posts/     → posts.urls                             │
                    │  /feed/      → posts.feed_urls                        │
                    │  /admin-panel/ → admin_panel.urls                     │
                    │  /           → landing page                           │
                    │  /home/      → home page                              │
                    └─────────────────────┬───────────────────────────────┘
                                          │
                    ┌─────────────────────┼───────────────────────────────┐
                    │                     │                                │
                    ▼                     ▼                                ▼
            ┌───────────────┐    ┌───────────────┐    ┌───────────────────┐
            │   accounts/   │    │    study/     │    │      posts/       │
            │               │    │               │    │                   │
            │ - login       │    │ - generate    │    │ - create post     │
            │ - signup      │    │ - view cards  │    │ - post detail     │
            │ - profile     │    │ - take quiz   │    │ - reactions       │
            │ - follow      │    │ - history     │    │ - comments        │
            └───────┬───────┘    └───────┬───────┘    └─────────┬─────────┘
                    │                    │                      │
                    └────────────────────┼──────────────────────┘
                                         │
                                         ▼
                    ┌─────────────────────────────────────────────────────┐
                    │                  PostgreSQL Database                 │
                    │                                                       │
                    │  Users, Profiles, Follow, StudySets, Flashcards,     │
                    │  QuizQuestions, Posts, Tags, Reactions, Comments,    │
                    │  Reports                                              │
                    └─────────────────────────────────────────────────────┘
```

---

# 4. Docker Configuration

## docker-compose.yml

This file defines two services that work together:

```yaml
version: '3.8'

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "${DB_HOST_PORT}:5432"

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "${WEB_PORT}:8000"
    depends_on:
      - db
    env_file:
      - .env

volumes:
  postgres_data:
```

### How It Works:

1. **db service**:
   - Uses official PostgreSQL 16 image
   - Creates database from environment variables
   - Stores data in `postgres_data` volume (persists across restarts)
   - Exposes port 5433 on host (maps to 5432 in container)

2. **web service**:
   - Builds from local Dockerfile
   - Runs Django development server
   - Mounts current directory as `/app` (live code changes)
   - Waits for `db` to start first (`depends_on`)
   - Reads environment variables from `.env`

3. **volumes**:
   - `postgres_data`: Named volume for database persistence

## Dockerfile

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Run entrypoint
ENTRYPOINT ["./entrypoint.sh"]
```

### Line-by-Line Explanation:

1. `FROM python:3.11-slim`: Use Python 3.11 as base (slim = smaller size)
2. `ENV PYTHONDONTWRITEBYTECODE=1`: Don't create .pyc bytecode files
3. `ENV PYTHONUNBUFFERED=1`: Print output immediately (for logs)
4. `WORKDIR /app`: Set working directory in container
5. `COPY requirements.txt .`: Copy requirements first (for caching)
6. `RUN pip install`: Install Python packages
7. `COPY . .`: Copy all project files
8. `RUN chmod +x`: Make entrypoint script executable
9. `ENTRYPOINT`: Run entrypoint script on container start

## entrypoint.sh

```bash
#!/bin/bash

echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Apply migrations
python manage.py migrate --noinput

# Start server
exec "$@"
```

### What It Does:

1. **Waits for database**: Uses `nc` (netcat) to check if PostgreSQL is accepting connections on port 5432
2. **Applies migrations**: Runs `manage.py migrate` to create/update database tables
3. **Starts the app**: `exec "$@"` runs the command passed to the container (Django server)

## .env File

```
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=miftah_db
DB_USER=miftah_user
DB_PASSWORD=miftah_password
DB_HOST_PORT=5433
WEB_PORT=8000
DEEPSEEK_API_KEY=sk-...
```

These variables are used by both Docker Compose and Django settings.

## requirements.txt

```
Django>=5.0
psycopg2-binary
pypdf
requests
Pillow
```

- **Django>=5.0**: Web framework
- **psycopg2-binary**: PostgreSQL adapter for Python
- **pypdf**: PDF text extraction library
- **requests**: HTTP client for API calls
- **Pillow**: Image processing (for potential future features)

---

# 5. Django Project Configuration (miftah/)

The `miftah/` directory contains the Django project settings and root configuration.

## miftah/__init__.py

Empty file that marks this directory as a Python package.

## miftah/settings.py

This is the central configuration file for Django. Let me explain each section:

### Installed Apps

```python
INSTALLED_APPS = [
    'django.contrib.admin',       # Django's built-in admin interface
    'django.contrib.auth',        # User authentication system
    'django.contrib.contenttypes',# Content type framework (for generic relations)
    'django.contrib.sessions',    # Session handling
    'django.contrib.messages',    # Flash messages
    'django.contrib.staticfiles', # Static file serving

    # Our custom apps
    'accounts',      # User profiles and follow system
    'study',         # AI-generated study materials
    'posts',         # Social posting
    'admin_panel',   # Custom admin dashboard
]
```

### Database Configuration

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'miftah_db'),
        'USER': os.environ.get('DB_USER', 'miftah_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'miftah_password'),
        'HOST': 'db',  # Docker service name
        'PORT': '5432',
    }
}
```

The `HOST: 'db'` refers to the Docker service name - Docker networking resolves this to the database container's IP.

### Authentication Settings

```python
LOGIN_URL = 'accounts:login'           # Redirect here if not logged in
LOGIN_REDIRECT_URL = 'home'            # After login, go to home
LOGOUT_REDIRECT_URL = 'landing'        # After logout, go to landing page
```

### DeepSeek API Configuration

```python
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'
```

## miftah/urls.py

The root URL configuration routes requests to the appropriate app:

```python
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # Django's built-in admin (separate from our custom admin panel)
    path('admin/', admin.site.urls),

    # Public pages (no app prefix)
    path('', views.landing_page, name='landing'),
    path('home/', views.home_page, name='home'),

    # App URLs
    path('accounts/', include('accounts.urls')),
    path('study/', include('study.urls')),
    path('posts/', include('posts.urls')),
    path('feed/', include('posts.feed_urls')),
    path('admin-panel/', include('admin_panel.urls')),
]
```

### URL Resolution Process:

1. Request comes in for `/posts/5/`
2. Django checks `urlpatterns` from top to bottom
3. Matches `path('posts/', include('posts.urls'))`
4. Strips `posts/` prefix, passes `5/` to posts.urls
5. posts.urls matches `path('<int:pk>/', views.post_detail)`
6. Calls `post_detail` view with `pk=5`

## miftah/views.py

Contains views for the landing and home pages:

```python
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def landing_page(request):
    """Public landing page for unauthenticated users."""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'landing.html')

@login_required
def home_page(request):
    """Main dashboard for authenticated users."""
    return render(request, 'home.html')
```

### The `@login_required` Decorator:

This decorator checks if the user is logged in. If not, it redirects to `LOGIN_URL` (accounts:login). After logging in, the user is returned to their original destination.

## miftah/wsgi.py

WSGI (Web Server Gateway Interface) configuration for production deployment:

```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miftah.settings')
application = get_wsgi_application()
```

This file is the entry point for production servers like Gunicorn or uWSGI.

---

# 6. Accounts App - Authentication & Social

The `accounts` app handles user registration, login, profiles, and the follow system.

## accounts/models.py

### Profile Model

```python
class Profile(models.Model):
    """Extended user profile with bio and timestamps."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name='نبذة عني')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def followers_count(self):
        return self.user.followers.count()

    @property
    def following_count(self):
        return self.user.following.count()
```

**Key Points:**
- `OneToOneField`: Each User has exactly one Profile
- `on_delete=models.CASCADE`: If User is deleted, Profile is deleted too
- `related_name='profile'`: Access profile via `user.profile`
- `@property`: Calculated fields (not stored in database)

**How OneToOne Works:**
```python
# Get profile from user
user = User.objects.get(username='ahmed')
profile = user.profile  # Uses related_name

# Get user from profile
profile = Profile.objects.get(pk=1)
user = profile.user
```

### Follow Model

```python
class Follow(models.Model):
    """Follow relationship between users."""
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='المتابِع'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='المتابَع'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        constraints = [
            models.CheckConstraint(
                check=~models.Q(follower=models.F('following')),
                name='prevent_self_follow'
            )
        ]
```

**Key Points:**
- Two ForeignKeys to User create a self-referential many-to-many relationship
- `unique_together`: Prevents duplicate follows
- `CheckConstraint`: Database-level prevention of self-following

**Related Name Trick:**
```python
# Get users that ahmed follows
ahmed = User.objects.get(username='ahmed')
ahmed.following.all()  # Returns Follow objects where ahmed is follower

# Get users that follow ahmed
ahmed.followers.all()  # Returns Follow objects where ahmed is being followed
```

## accounts/views.py

### Signup View

```python
def signup_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after signup
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})
```

**Flow:**
1. Check if already logged in → redirect to home
2. POST request → validate form, create user, login, redirect
3. GET request → show empty form

### Toggle Follow View (HTMX)

```python
@login_required
@require_POST
def toggle_follow(request, username):
    """Toggle follow/unfollow a user. Returns partial HTML for HTMX."""
    user_to_follow = get_object_or_404(User, username=username)

    if user_to_follow == request.user:
        return HttpResponse(status=400)

    follow_exists = Follow.objects.filter(
        follower=request.user,
        following=user_to_follow
    ).exists()

    if follow_exists:
        Follow.objects.filter(
            follower=request.user,
            following=user_to_follow
        ).delete()
        is_following = False
    else:
        Follow.objects.create(
            follower=request.user,
            following=user_to_follow
        )
        is_following = True

    # Check if target user follows back
    follows_me = Follow.objects.filter(
        follower=user_to_follow,
        following=request.user
    ).exists()

    return render(request, 'accounts/partials/follow_button.html', {
        'profile_user': user_to_follow,
        'is_following': is_following,
        'follows_me': follows_me,
    })
```

**HTMX Integration:**
- Button sends POST to `/accounts/u/username/toggle-follow/`
- View returns HTML snippet (not full page)
- HTMX replaces button element with new HTML
- No page reload needed!

## accounts/forms.py

### SignUpForm

```python
class SignUpForm(UserCreationForm):
    """Custom signup form with email field."""
    email = forms.EmailField(
        required=True,
        label='البريد الإلكتروني',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'اسم المستخدم',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(user=user)  # Auto-create profile!
        return user
```

**Key Points:**
- Extends Django's `UserCreationForm` (handles password validation)
- Adds required email field
- `save()` method also creates the Profile

## accounts/urls.py

```python
app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('u/<str:username>/', views.profile_view, name='profile'),
    path('u/<str:username>/toggle-follow/', views.toggle_follow, name='toggle_follow'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('following/', views.following_list, name='following_list'),
]
```

**The `app_name`:**
This creates a namespace. URLs are referenced as `'accounts:login'` not just `'login'`. This prevents conflicts between apps.

## accounts/admin.py

```python
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'created_at')
    search_fields = ('user__username', 'bio')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
```

This registers models in Django's built-in admin at `/admin/`.

## accounts/signals.py (Conceptual)

While not explicitly in a signals.py file, the Profile creation happens in the form's `save()` method. An alternative approach uses Django signals:

```python
# Alternative: Using signals
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
```

---

# 7. Study App - AI-Powered Learning

The `study` app handles AI content generation, the core feature of Miftah.

## study/models.py

### StudySet Model

```python
class StudySet(models.Model):
    """Container for flashcards or quiz questions."""
    SET_TYPE_CHOICES = [
        ('flashcards', 'بطاقات تعليمية'),
        ('quiz', 'اختبار'),
    ]
    LANGUAGE_CHOICES = [
        ('ar', 'العربية'),
        ('en', 'English'),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='study_sets',
        verbose_name='المالك'
    )
    set_type = models.CharField(
        max_length=20,
        choices=SET_TYPE_CHOICES,
        verbose_name='نوع المجموعة'
    )
    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        verbose_name='اللغة'
    )
    title = models.CharField(max_length=200, blank=True, verbose_name='العنوان')
    source_text = models.TextField(
        verbose_name='النص المصدر',
        help_text='النص الأصلي المستخدم لإنشاء المجموعة'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def item_count(self):
        """Return number of cards or questions."""
        if self.set_type == 'flashcards':
            return self.flashcards.count()
        return self.questions.count()

    @property
    def is_shared(self):
        """Check if this study set has been shared in a post."""
        return self.posts.filter(deleted_at__isnull=True).exists()
```

### Flashcard Model

```python
class Flashcard(models.Model):
    """Single flashcard with question and answer."""
    study_set = models.ForeignKey(
        StudySet,
        on_delete=models.CASCADE,
        related_name='flashcards'
    )
    index = models.PositiveIntegerField(verbose_name='الترتيب')
    question = models.TextField(verbose_name='السؤال')
    answer = models.TextField(verbose_name='الإجابة')

    class Meta:
        ordering = ['index']
        unique_together = ('study_set', 'index')
```

### QuizQuestion Model

```python
class QuizQuestion(models.Model):
    """Multiple choice question with explanation."""
    study_set = models.ForeignKey(
        StudySet,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    index = models.PositiveIntegerField(verbose_name='الترتيب')
    question = models.TextField(verbose_name='السؤال')
    options = models.JSONField(
        verbose_name='الخيارات',
        help_text='قائمة من 4 خيارات'
    )
    correct_index = models.PositiveSmallIntegerField(
        verbose_name='رقم الإجابة الصحيحة',
        help_text='0-3'
    )
    explanation = models.TextField(
        verbose_name='الشرح',
        help_text='شرح للإجابة الصحيحة والخاطئة'
    )

    class Meta:
        ordering = ['index']
        unique_together = ('study_set', 'index')
```

**JSONField for Options:**
```python
# Stored as JSON array
options = ["Option A", "Option B", "Option C", "Option D"]
# Accessed in Python as list
question.options[0]  # "Option A"
```

## study/ai_service.py

This is the heart of the AI functionality:

### Language Detection

```python
def detect_language(text):
    """Detect if text is primarily Arabic or English."""
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    arabic_chars = len(arabic_pattern.findall(text))
    total_alpha = sum(1 for c in text if c.isalpha())

    if total_alpha == 0:
        return 'ar'  # Default to Arabic

    arabic_ratio = arabic_chars / total_alpha
    return 'ar' if arabic_ratio > 0.3 else 'en'
```

### PDF Text Extraction

```python
def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file."""
    try:
        reader = pypdf.PdfReader(pdf_file)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return ' '.join(text_parts)
    except Exception as e:
        raise ValueError(f"فشل استخراج النص من الملف: {str(e)}")
```

### Flashcard Generation

```python
def generate_flashcards(text, count=10):
    """Generate flashcards from text using DeepSeek API."""
    language = detect_language(text)

    if language == 'ar':
        prompt = f"""أنت مساعد تعليمي. قم بإنشاء {count} بطاقة تعليمية من النص التالي.

لكل بطاقة، اكتب سؤال وجواب مختصر.

النص:
{text}

أعد النتيجة بصيغة JSON:
[
  {{"question": "السؤال", "answer": "الجواب"}},
  ...
]"""
    else:
        prompt = f"""You are an educational assistant. Create {count} flashcards from the following text.

For each card, write a question and a brief answer.

Text:
{text}

Return the result in JSON format:
[
  {{"question": "Question", "answer": "Answer"}},
  ...
]"""

    response = call_deepseek_api(prompt)
    return parse_flashcards_response(response), language
```

### DeepSeek API Call

```python
def call_deepseek_api(prompt):
    """Make request to DeepSeek API."""
    headers = {
        'Authorization': f'Bearer {settings.DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.7
    }

    response = requests.post(
        settings.DEEPSEEK_API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        raise ValueError(f"API Error: {response.status_code}")

    data = response.json()
    return data['choices'][0]['message']['content']
```

## study/views.py

### Generate View

```python
@login_required
def generate_view(request, set_type):
    """Generate flashcards or quiz from text/PDF."""
    if set_type not in ['flashcards', 'quiz']:
        raise Http404("Invalid set type")

    if request.method == 'POST':
        form = GenerateStudySetForm(request.POST, request.FILES)
        if form.is_valid():
            # Get text from input or PDF
            if form.cleaned_data['input_type'] == 'pdf':
                text = extract_text_from_pdf(form.cleaned_data['pdf_file'])
            else:
                text = form.cleaned_data['text_content']

            count = form.cleaned_data['count']

            # Generate content via AI
            if set_type == 'flashcards':
                items, language = generate_flashcards(text, count)
            else:
                items, language = generate_quiz(text, count)

            # Create StudySet
            study_set = StudySet.objects.create(
                owner=request.user,
                set_type=set_type,
                language=language,
                title=form.cleaned_data['title'],
                source_text=text[:5000]  # Store first 5000 chars
            )

            # Create items
            if set_type == 'flashcards':
                for i, item in enumerate(items):
                    Flashcard.objects.create(
                        study_set=study_set,
                        index=i,
                        question=item['question'],
                        answer=item['answer']
                    )
            else:
                for i, item in enumerate(items):
                    QuizQuestion.objects.create(
                        study_set=study_set,
                        index=i,
                        question=item['question'],
                        options=item['options'],
                        correct_index=item['correct_index'],
                        explanation=item['explanation']
                    )

            return redirect('study:detail', pk=study_set.pk)
    else:
        form = GenerateStudySetForm()

    return render(request, 'study/generate.html', {
        'form': form,
        'set_type': set_type,
    })
```

### Study Set Detail View

```python
@login_required
def study_set_detail(request, pk):
    """View flashcards or quiz."""
    study_set = get_object_or_404(StudySet, pk=pk)

    # Check access: owner OR shared via public post
    is_owner = study_set.owner == request.user
    is_shared = study_set.posts.filter(deleted_at__isnull=True).exists()

    if not is_owner and not is_shared:
        raise Http404("Study set not found")

    context = {
        'study_set': study_set,
        'is_owner': is_owner,
    }

    if study_set.set_type == 'flashcards':
        context['flashcards'] = study_set.flashcards.all()
        return render(request, 'study/flashcards_view.html', context)
    else:
        context['questions'] = study_set.questions.all()
        return render(request, 'study/quiz_view.html', context)
```

## study/forms.py

```python
class GenerateStudySetForm(forms.Form):
    """Form for generating new study set."""
    title = forms.CharField(
        max_length=200,
        label='العنوان',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    input_type = forms.ChoiceField(
        choices=[('text', 'نص'), ('pdf', 'ملف PDF')],
        initial='text',
        label='نوع المدخلات'
    )
    text_content = forms.CharField(
        required=False,
        label='النص',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8
        })
    )
    pdf_file = forms.FileField(
        required=False,
        label='ملف PDF'
    )
    count = forms.IntegerField(
        min_value=5,
        max_value=20,
        initial=10,
        label='العدد',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        input_type = cleaned_data.get('input_type')

        if input_type == 'text':
            text = cleaned_data.get('text_content', '')
            if len(text) < 50:
                raise forms.ValidationError('النص يجب أن يكون 50 حرفاً على الأقل')
        else:
            pdf = cleaned_data.get('pdf_file')
            if not pdf:
                raise forms.ValidationError('يرجى رفع ملف PDF')
            if pdf.size > 10 * 1024 * 1024:  # 10MB
                raise forms.ValidationError('حجم الملف يجب أن يكون أقل من 10 ميجابايت')

        return cleaned_data
```

---

# 8. Posts App - Social Sharing

The `posts` app handles sharing study sets, reactions, comments, and search.

## posts/models.py

### Tag Model

```python
class Tag(models.Model):
    """Predefined tag for categorizing posts."""
    name = models.CharField(max_length=50, unique=True, verbose_name='اسم الوسم')
    color = models.CharField(max_length=7, default='#94a3b8', verbose_name='اللون')

    class Meta:
        verbose_name = 'وسم'
        verbose_name_plural = 'الوسوم'

    def __str__(self):
        return self.name
```

**Important:** Tags are predefined via the `seed_tags` management command. Users cannot create new tags.

### Post Model

```python
class Post(models.Model):
    """Shared study set with metadata."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='الكاتب'
    )
    study_set = models.ForeignKey(
        'study.StudySet',
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='المجموعة الدراسية'
    )
    title = models.CharField(max_length=200, verbose_name='العنوان')
    caption = models.TextField(blank=True, null=True, verbose_name='وصف قصير')
    tags = models.ManyToManyField(Tag, through='PostTag', related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # Soft delete!

    @property
    def likes_count(self):
        return self.reactions.filter(value='like').count()

    @property
    def dislikes_count(self):
        return self.reactions.filter(value='dislike').count()
```

**Soft Delete Pattern:**
Instead of actually deleting posts, we set `deleted_at` to the current time. This:
- Preserves data for audit/recovery
- Maintains referential integrity
- Allows "undelete" functionality

When querying, always filter: `Post.objects.filter(deleted_at__isnull=True)`

### PostTag Model (Through Table)

```python
class PostTag(models.Model):
    """Through model for Post-Tag M2M relationship."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'tag')
```

This explicit through model allows adding extra fields to the relationship if needed later.

### Reaction Model

```python
class Reaction(models.Model):
    """Like or dislike on a post."""
    VALUE_CHOICES = [
        ('like', 'إعجاب'),
        ('dislike', 'عدم إعجاب'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    value = models.CharField(max_length=10, choices=VALUE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # One reaction per user per post
```

**Mutually Exclusive Reactions:**
If a user likes a post and then clicks dislike, the reaction value is updated (not a second reaction created).

### Comment Model

```python
class Comment(models.Model):
    """Comment on a post."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField(verbose_name='التعليق')
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # Soft delete

    class Meta:
        ordering = ['-created_at']
```

## posts/views.py

### Create Post View

```python
@login_required
def create_post(request):
    """Create a new post sharing a study set."""
    # Get user's unshared study sets
    study_sets = StudySet.objects.filter(owner=request.user)

    # Check for preselected study set from URL
    preselected_id = request.GET.get('study_set')
    preselected = None
    if preselected_id:
        preselected = study_sets.filter(pk=preselected_id).first()

    if request.method == 'POST':
        form = PostForm(request.POST)
        study_set_id = request.POST.get('study_set')

        if form.is_valid() and study_set_id:
            study_set = get_object_or_404(StudySet, pk=study_set_id, owner=request.user)
            post = form.save(author=request.user, study_set=study_set)
            return redirect('posts:detail', pk=post.pk)
    else:
        form = PostForm()

    return render(request, 'posts/create.html', {
        'form': form,
        'study_sets': study_sets,
        'preselected_study_set': preselected,
        'all_tags': Tag.objects.all().order_by('name'),
    })
```

### Toggle Reaction View (HTMX)

```python
@login_required
@require_POST
def toggle_reaction(request, pk):
    """Toggle like/dislike on a post. Returns updated buttons HTML."""
    post = get_object_or_404(Post, pk=pk, deleted_at__isnull=True)
    reaction_type = request.POST.get('type')  # 'like' or 'dislike'

    existing = Reaction.objects.filter(user=request.user, post=post).first()

    if existing:
        if existing.value == reaction_type:
            # Same reaction = remove it
            existing.delete()
        else:
            # Different reaction = switch it
            existing.value = reaction_type
            existing.save()
    else:
        # New reaction
        Reaction.objects.create(user=request.user, post=post, value=reaction_type)

    # Get current user's reaction for UI state
    current_reaction = Reaction.objects.filter(user=request.user, post=post).first()
    user_reaction = current_reaction.value if current_reaction else None

    return render(request, 'posts/partials/reaction_buttons.html', {
        'post': post,
        'user_reaction': user_reaction,
    })
```

### Search View

```python
@login_required
def search_posts(request):
    """Search posts by keywords and tags."""
    query = request.GET.get('q', '').strip()
    tag_filter = request.GET.getlist('tags')  # Multiple tags possible

    posts = Post.objects.filter(deleted_at__isnull=True)

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(caption__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    if tag_filter:
        for tag_name in tag_filter:
            posts = posts.filter(tags__name=tag_name)

    posts = posts.select_related('author', 'study_set').prefetch_related('tags')
    posts = posts.order_by('-created_at')

    return render(request, 'posts/search.html', {
        'posts': posts,
        'query': query,
        'tag_filter': tag_filter,
        'all_tags': Tag.objects.all().order_by('name'),
    })
```

**Query Optimization:**
- `select_related()`: Joins related tables in single query (one-to-one, foreign key)
- `prefetch_related()`: Separate query for many-to-many (more efficient than N+1 queries)

## posts/forms.py

### PostForm

```python
class PostForm(forms.ModelForm):
    """Form for creating a new post."""
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by('name'),
        label='التصنيفات',
        help_text='اختر من 1 إلى 4 تصنيفات',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'tag-checkbox-list'})
    )

    class Meta:
        model = Post
        fields = ['title', 'caption']
        labels = {
            'title': 'العنوان',
            'caption': 'وصف قصير (اختياري)',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'caption': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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
            post.tags.set(self.cleaned_data.get('tags', []))
        return post
```

## posts/management/commands/seed_tags.py

This Django management command populates the 52 predefined tags:

```python
class Command(BaseCommand):
    help = 'Seeds the database with predefined educational tags'

    def handle(self, *args, **options):
        tags_data = [
            # العلوم الطبيعية - Natural Sciences
            {'name': 'فيزياء', 'color': '#6366f1'},
            {'name': 'كيمياء', 'color': '#8b5cf6'},
            {'name': 'أحياء', 'color': '#22c55e'},
            # ... (52 total tags)
        ]

        for tag_data in tags_data:
            tag, created = Tag.objects.update_or_create(
                name=tag_data['name'],
                defaults={'color': tag_data['color']}
            )
```

**Run with:** `docker compose exec web python manage.py seed_tags`

---

# 9. Feed App - Content Discovery

The feed app provides views for browsing posts. It's structured as separate URL file but uses views from posts app.

## posts/feed_views.py

### Recent Feed

```python
@login_required
def recent_feed(request):
    """Show most recent posts from all users."""
    query = request.GET.get('q', '').strip()
    tag_filter = request.GET.getlist('tags')

    posts = Post.objects.filter(deleted_at__isnull=True)

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(caption__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    if tag_filter:
        for tag_name in tag_filter:
            posts = posts.filter(tags__name=tag_name)

    posts = posts.select_related('author', 'study_set').prefetch_related('tags')
    posts = posts.order_by('-created_at')

    context = {
        'posts': posts,
        'query': query,
        'tag_filter': tag_filter,
        'all_tags': Tag.objects.all().order_by('name'),
        'feed_type': 'recent',
    }

    return render(request, 'posts/feed.html', context)
```

### Following Feed

```python
@login_required
def following_feed(request):
    """Show posts from users that the current user follows."""
    # Get users that current user follows
    following_users = Follow.objects.filter(
        follower=request.user
    ).values_list('following', flat=True)

    posts = Post.objects.filter(
        author__in=following_users,
        deleted_at__isnull=True
    )

    # ... same filtering logic as recent_feed ...

    context = {
        'posts': posts,
        'feed_type': 'following',
        'following_count': len(following_users),
    }

    return render(request, 'posts/feed.html', context)
```

**The `values_list('following', flat=True)` trick:**
Returns a flat list of user IDs instead of Follow objects:
```python
[1, 5, 12, 34]  # User IDs
# Instead of
[<Follow: ...>, <Follow: ...>, ...]
```

## posts/feed_urls.py

```python
app_name = 'feed'

urlpatterns = [
    path('recent/', feed_views.recent_feed, name='recent'),
    path('following/', feed_views.following_feed, name='following'),
]
```

---

# 10. Admin Panel App - Moderation

The `admin_panel` app provides a custom dashboard for staff members to moderate content.

## admin_panel/models.py

### Report Model

```python
class Report(models.Model):
    """Report submitted by users against inappropriate content."""
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

    # Who reported
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports_submitted'
    )

    # What was reported (Generic Foreign Key)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Report details
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Resolution
    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reports_reviewed'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reporter', 'content_type', 'object_id')
```

**GenericForeignKey Explained:**

A GenericForeignKey allows relating to ANY model, not just one:

```python
# Traditional ForeignKey - only relates to Post
reported_post = models.ForeignKey(Post, ...)

# GenericForeignKey - relates to Post OR Comment OR anything
content_type = models.ForeignKey(ContentType, ...)  # Which model?
object_id = models.PositiveIntegerField()            # Which instance?
content_object = GenericForeignKey(...)              # The actual object
```

Usage:
```python
# Create report for a Post
report = Report.objects.create(
    reporter=user,
    content_type=ContentType.objects.get_for_model(Post),
    object_id=post.pk,
    reason='spam'
)
report.content_object  # Returns the Post instance

# Create report for a Comment
report = Report.objects.create(
    reporter=user,
    content_type=ContentType.objects.get_for_model(Comment),
    object_id=comment.pk,
    reason='harassment'
)
report.content_object  # Returns the Comment instance
```

## admin_panel/views.py

### Staff-Only Access

```python
def staff_required(user):
    """Check if user is staff."""
    return user.is_authenticated and user.is_staff

# Usage with decorator
@login_required
@user_passes_test(staff_required, login_url='home')
def dashboard(request):
    ...
```

### Dashboard View

```python
@login_required
@user_passes_test(staff_required, login_url='home')
def dashboard(request):
    """Main admin dashboard with statistics."""
    now = timezone.now()

    context = {
        # Basic counts
        'total_users': User.objects.count(),
        'total_posts': Post.objects.filter(deleted_at__isnull=True).count(),
        'total_comments': Comment.objects.filter(deleted_at__isnull=True).count(),

        # Posts in timeframes
        'posts_24h': Post.objects.filter(
            deleted_at__isnull=True,
            created_at__gte=now - timedelta(hours=24)
        ).count(),
        'posts_7d': Post.objects.filter(
            deleted_at__isnull=True,
            created_at__gte=now - timedelta(days=7)
        ).count(),

        # Top 5 most liked posts
        'top_posts': Post.objects.filter(deleted_at__isnull=True).annotate(
            like_count=Count('reactions', filter=Q(reactions__value='like'))
        ).order_by('-like_count')[:5],

        # Most used tags
        'top_tags': Tag.objects.annotate(
            post_count=Count('posts', filter=Q(posts__deleted_at__isnull=True))
        ).order_by('-post_count')[:10],

        # Pending reports
        'pending_reports_count': Report.objects.filter(status='pending').count(),
        'recent_reports': Report.objects.filter(status='pending').order_by('-created_at')[:5],
    }

    return render(request, 'admin_panel/dashboard.html', context)
```

**Annotation Magic:**

`annotate()` adds calculated fields to each object in the queryset:

```python
# Without annotate - N+1 queries problem
for post in posts:
    likes = post.reactions.filter(value='like').count()  # Extra query per post!

# With annotate - single query
posts = Post.objects.annotate(
    like_count=Count('reactions', filter=Q(reactions__value='like'))
)
for post in posts:
    print(post.like_count)  # Already calculated, no extra query
```

### Approve Report View

```python
@login_required
@user_passes_test(staff_required, login_url='home')
@require_POST
def approve_report(request, pk):
    """Approve report and soft-delete the content."""
    report = get_object_or_404(Report, pk=pk)

    # Soft delete the reported content
    content = report.content_object
    if content and hasattr(content, 'deleted_at'):
        content.deleted_at = timezone.now()
        content.save()

    # Update report status
    report.status = 'approved'
    report.reviewed_by = request.user
    report.reviewed_at = timezone.now()
    report.save()

    messages.success(request, 'تم قبول البلاغ وحذف المحتوى.')
    return redirect('admin_panel:reports_list')
```

### Submit Report View (For Users)

```python
@login_required
@require_POST
def submit_report(request):
    """Submit a report for content."""
    content_type_str = request.POST.get('content_type')
    object_id = request.POST.get('object_id')
    reason = request.POST.get('reason')
    details = request.POST.get('details', '')

    # Validate content type
    if content_type_str == 'post':
        content_type = ContentType.objects.get_for_model(Post)
        content = Post.objects.filter(pk=object_id, deleted_at__isnull=True).first()
    else:
        content_type = ContentType.objects.get_for_model(Comment)
        content = Comment.objects.filter(pk=object_id, deleted_at__isnull=True).first()

    # Prevent self-reporting
    if hasattr(content, 'author') and content.author == request.user:
        return HttpResponse('<div class="alert alert-warning">لا يمكنك الإبلاغ عن محتواك.</div>')

    # Check for duplicate report
    if Report.objects.filter(
        reporter=request.user,
        content_type=content_type,
        object_id=object_id
    ).exists():
        return HttpResponse('<div class="alert alert-info">لقد قمت بالإبلاغ مسبقاً.</div>')

    # Create report
    Report.objects.create(
        reporter=request.user,
        content_type=content_type,
        object_id=object_id,
        reason=reason,
        details=details
    )

    return HttpResponse(
        '<div class="alert alert-success">تم إرسال البلاغ بنجاح.</div>'
    )
```

---

# 11. Templates - The UI Layer

## Template Inheritance

Django templates use inheritance to avoid duplication:

```
base.html (Master Layout)
├── landing.html
├── home.html
├── accounts/login.html
├── accounts/signup.html
├── accounts/profile.html
├── study/generate.html
├── study/flashcards_view.html
├── study/quiz_view.html
├── posts/create.html
├── posts/detail.html
├── posts/feed.html
├── posts/search.html
└── admin_panel/base_admin.html (Admin Layout)
    ├── admin_panel/dashboard.html
    ├── admin_panel/reports/list.html
    └── admin_panel/reports/detail.html
```

## templates/base.html

The master template that all others extend:

```html
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}مفتاح{% endblock %}</title>

    <!-- Bootstrap 5 RTL -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/.../bootstrap.rtl.min.css">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/.../bootstrap-icons.css">
    <!-- Google Fonts - Arabic -->
    <link href="https://fonts.googleapis.com/.../Tajawal..." rel="stylesheet">
    <!-- HTMX -->
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>

    <style>
        /* CSS Variables */
        :root {
            --primary-color: #2563eb;
            --primary-hover: #1d4ed8;
            /* ... */
        }

        /* Global styles */
        body {
            font-family: 'Tajawal', sans-serif;
            background-color: var(--bg-color);
        }

        /* Component styles */
        .tag-badge { /* Tag display */ }
        .flashcard { /* Flip card animation */ }
        .quiz-option { /* Quiz choices */ }
        .reaction-btn { /* Like/dislike buttons */ }
    </style>

    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navbar (only for authenticated users) -->
    {% if user.is_authenticated %}
    <nav class="navbar navbar-expand-lg sticky-top">
        <!-- Logo, navigation links, user dropdown -->
    </nav>
    {% endif %}

    <!-- Flash Messages -->
    {% if messages %}
    <div class="container mt-3">
        {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
            {{ message }}
            <button class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <!-- Main Content -->
    <main class="{% if user.is_authenticated %}py-4{% endif %}">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    {% if user.is_authenticated %}
    <footer class="py-4 mt-5 border-top">
        <div class="container text-center text-muted">
            <p class="mb-0">مفتاح - منصة تعليمية للطلاب العرب</p>
        </div>
    </footer>
    {% endif %}

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/.../bootstrap.bundle.min.js"></script>

    <!-- HTMX CSRF Configuration -->
    <script>
        document.body.addEventListener('htmx:configRequest', function(event) {
            event.detail.headers['X-CSRFToken'] = '{{ csrf_token }}';
        });
    </script>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

**Key Template Tags:**

- `{% block name %}...{% endblock %}`: Define overridable sections
- `{% if condition %}...{% endif %}`: Conditional rendering
- `{% for item in list %}...{% endfor %}`: Loops
- `{{ variable }}`: Output variable value
- `{{ variable|filter }}`: Apply filter (e.g., `|date:"Y/m/d"`)
- `{% url 'name' %}`: Generate URL from name
- `{% csrf_token %}`: Security token for forms
- `{% include 'template.html' %}`: Include another template

## templates/study/flashcards_view.html

Interactive flashcard viewer with flip animation:

```html
{% extends 'base.html' %}

{% block content %}
<div class="container">
    <!-- Header with title and actions -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h4>{{ study_set.title }}</h4>
            <div class="text-muted">{{ flashcards|length }} بطاقة</div>
        </div>
        {% if is_owner %}
        <a href="{% url 'posts:create' %}?study_set={{ study_set.pk }}" class="btn btn-primary">
            مشاركة
        </a>
        {% endif %}
    </div>

    <!-- Navigation -->
    <div class="d-flex justify-content-between mb-3">
        <button onclick="prevCard()" id="prev-btn">السابق</button>
        <span id="card-counter">1 / {{ flashcards|length }}</span>
        <button onclick="nextCard()" id="next-btn">التالي</button>
    </div>

    <!-- Flashcards (CSS 3D flip) -->
    {% for card in flashcards %}
    <div class="flashcard {% if not forloop.first %}d-none{% endif %}"
         data-index="{{ forloop.counter0 }}"
         onclick="flipCard(this)">
        <div class="flashcard-inner">
            <div class="flashcard-front">
                <div>{{ card.question }}</div>
            </div>
            <div class="flashcard-back">
                <div>{{ card.answer }}</div>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}

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
    }

    function nextCard() {
        if (currentIndex < totalCards - 1) {
            currentIndex++;
            showCard(currentIndex);
        }
    }

    function prevCard() {
        if (currentIndex > 0) {
            currentIndex--;
            showCard(currentIndex);
        }
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
```

## templates/posts/partials/reaction_buttons.html

HTMX-powered like/dislike buttons:

```html
<div class="d-flex gap-3">
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

**HTMX Attributes Explained:**

- `hx-post`: Send POST request to this URL
- `hx-vals`: Include this JSON data in the request
- `hx-headers`: Add these headers (CSRF token)
- `hx-target`: Replace content of this element with response
- `hx-swap`: How to replace (`innerHTML` = replace children, `outerHTML` = replace entire element)

## templates/admin_panel/partials/report_modal.html

Bootstrap modal for submitting reports:

```html
<!-- Report Modal -->
<div class="modal fade" id="reportModal{% if modal_id %}-{{ modal_id }}{% endif %}" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">الإبلاغ عن محتوى</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form hx-post="{% url 'admin_panel:submit_report' %}"
                  hx-target="#report-result{% if modal_id %}-{{ modal_id }}{% endif %}"
                  hx-swap="innerHTML">
                {% csrf_token %}
                <input type="hidden" name="content_type" value="{{ content_type }}">
                <input type="hidden" name="object_id" value="{{ object_id }}">

                <div class="modal-body">
                    <div id="report-result{% if modal_id %}-{{ modal_id }}{% endif %}"></div>

                    <div class="mb-3">
                        <label class="form-label">سبب البلاغ</label>
                        <select name="reason" class="form-select" required>
                            <option value="">اختر السبب...</option>
                            <option value="hate_speech">خطاب كراهية</option>
                            <option value="spam">محتوى مزعج</option>
                            <option value="inappropriate">محتوى غير لائق</option>
                            <option value="misinformation">معلومات مضللة</option>
                            <option value="harassment">تحرش أو إساءة</option>
                            <option value="other">أخرى</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">تفاصيل إضافية (اختياري)</label>
                        <textarea name="details" class="form-control" rows="3"></textarea>
                    </div>
                </div>

                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                    <button type="submit" class="btn btn-danger">إرسال البلاغ</button>
                </div>
            </form>
        </div>
    </div>
</div>
```

**Template Context Variables:**

When including this modal:
```html
{% include 'admin_panel/partials/report_modal.html' with content_type='post' object_id=post.pk %}
{% include 'admin_panel/partials/report_modal.html' with content_type='comment' object_id=comment.pk modal_id=comment.pk %}
```

The `modal_id` creates unique IDs when multiple modals are needed (one per comment).

---

# 12. Database Schema

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│      User       │       │     Profile     │
│ (Django built-in)│       │                 │
├─────────────────┤       ├─────────────────┤
│ id              │───────│ user_id (1:1)   │
│ username        │       │ bio             │
│ email           │       │ created_at      │
│ password        │       └─────────────────┘
│ is_staff        │
│ is_superuser    │
└────────┬────────┘
         │
         │ ┌───────────────────────────────────────┐
         │ │              Follow                    │
         │ ├───────────────────────────────────────┤
         ├─│ follower_id (FK to User)              │
         └─│ following_id (FK to User)             │
           │ created_at                            │
           │ UNIQUE(follower, following)           │
           │ CHECK(follower != following)          │
           └───────────────────────────────────────┘
         │
         │
┌────────┴────────┐       ┌─────────────────┐
│    StudySet     │       │    Flashcard    │
├─────────────────┤       ├─────────────────┤
│ id              │───┬───│ study_set_id    │
│ owner_id (FK)   │   │   │ index           │
│ set_type        │   │   │ question        │
│ language        │   │   │ answer          │
│ title           │   │   └─────────────────┘
│ source_text     │   │
│ created_at      │   │   ┌─────────────────┐
└────────┬────────┘   │   │  QuizQuestion   │
         │            │   ├─────────────────┤
         │            └───│ study_set_id    │
         │                │ index           │
         │                │ question        │
         │                │ options (JSON)  │
         │                │ correct_index   │
         │                │ explanation     │
         │                └─────────────────┘
         │
┌────────┴────────┐       ┌─────────────────┐
│      Post       │       │      Tag        │
├─────────────────┤       ├─────────────────┤
│ id              │───┬───│ id              │
│ author_id (FK)  │   │   │ name (unique)   │
│ study_set_id(FK)│   │   │ color           │
│ title           │   │   └─────────────────┘
│ caption         │   │
│ created_at      │   │   ┌─────────────────┐
│ deleted_at      │   │   │    PostTag      │
└────────┬────────┘   │   ├─────────────────┤
         │            └───│ post_id         │
         │                │ tag_id          │
         │                │ UNIQUE(post,tag)│
         │                └─────────────────┘
         │
         │            ┌─────────────────┐
         ├────────────│    Reaction     │
         │            ├─────────────────┤
         │            │ user_id (FK)    │
         │            │ post_id (FK)    │
         │            │ value (like/dis)│
         │            │ UNIQUE(user,post)│
         │            └─────────────────┘
         │
         │            ┌─────────────────┐
         └────────────│    Comment      │
                      ├─────────────────┤
                      │ post_id (FK)    │
                      │ author_id (FK)  │
                      │ body            │
                      │ created_at      │
                      │ deleted_at      │
                      └─────────────────┘

┌───────────────────────────────────────┐
│              Report                    │
├───────────────────────────────────────┤
│ reporter_id (FK to User)              │
│ content_type_id (FK to ContentType)   │
│ object_id (Generic FK)                │
│ reason                                │
│ details                               │
│ status                                │
│ reviewed_by_id (FK to User)           │
│ reviewed_at                           │
│ created_at                            │
│ UNIQUE(reporter, content_type, object)│
└───────────────────────────────────────┘
```

## Migrations Explained

Django migrations are Python files that describe database changes:

### accounts/migrations/0001_initial.py

Creates Profile and Follow tables:

```python
operations = [
    migrations.CreateModel(
        name='Profile',
        fields=[
            ('id', models.BigAutoField(...)),
            ('bio', models.TextField(blank=True, max_length=500)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('user', models.OneToOneField(...)),
        ],
    ),
    migrations.CreateModel(
        name='Follow',
        fields=[
            ('id', models.BigAutoField(...)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('follower', models.ForeignKey(..., related_name='following')),
            ('following', models.ForeignKey(..., related_name='followers')),
        ],
        options={
            'unique_together': {('follower', 'following')},
            'constraints': [
                models.CheckConstraint(
                    check=~models.Q(follower=models.F('following')),
                    name='prevent_self_follow'
                )
            ],
        },
    ),
]
```

### posts/migrations/0002_add_color_to_tag.py

Adds color field to existing Tag table:

```python
operations = [
    migrations.AddField(
        model_name='tag',
        name='color',
        field=models.CharField(default='#94a3b8', max_length=7),
    ),
]
```

**Migration Commands:**
```bash
# Create migrations from model changes
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

---

# 13. URL Routing System

## Complete URL Map

```
/                           → miftah.views.landing_page
/home/                      → miftah.views.home_page

/accounts/
├── login/                  → accounts.views.login_view
├── signup/                 → accounts.views.signup_view
├── logout/                 → accounts.views.logout_view
├── edit/                   → accounts.views.edit_profile
├── following/              → accounts.views.following_list
└── u/<username>/           → accounts.views.profile_view
    └── toggle-follow/      → accounts.views.toggle_follow

/study/
├── generate/<set_type>/    → study.views.generate_view
│   (set_type: flashcards or quiz)
├── <pk>/                   → study.views.study_set_detail
├── <pk>/delete/            → study.views.delete_study_set
└── history/                → study.views.history_view

/posts/
├── new/                    → posts.views.create_post
├── search/                 → posts.views.search_posts
├── <pk>/                   → posts.views.post_detail
├── <pk>/delete/            → posts.views.delete_post
├── <pk>/react/             → posts.views.toggle_reaction
└── comment/<pk>/delete/    → posts.views.delete_comment

/feed/
├── recent/                 → posts.feed_views.recent_feed
└── following/              → posts.feed_views.following_feed

/admin-panel/
├── /                       → admin_panel.views.dashboard
├── reports/                → admin_panel.views.reports_list
├── reports/<pk>/           → admin_panel.views.report_detail
├── reports/<pk>/approve/   → admin_panel.views.approve_report
├── reports/<pk>/dismiss/   → admin_panel.views.dismiss_report
└── report/submit/          → admin_panel.views.submit_report

/admin/                     → Django built-in admin
```

## URL Namespaces

Each app has a namespace (`app_name`):

```python
# In template
{% url 'accounts:login' %}              → /accounts/login/
{% url 'posts:detail' pk=5 %}           → /posts/5/
{% url 'admin_panel:dashboard' %}       → /admin-panel/

# In Python view
from django.urls import reverse
reverse('accounts:login')               → '/accounts/login/'
reverse('posts:detail', kwargs={'pk': 5})  → '/posts/5/'
```

---

# 14. Data Flow Examples

## Example 1: User Creates Flashcards and Shares Them

```
1. User clicks "إنشاء بطاقات" on home page
   ↓
2. GET /study/generate/flashcards/
   → study.views.generate_view
   → Renders study/generate.html with empty form
   ↓
3. User pastes text, sets count=10, clicks submit
   ↓
4. POST /study/generate/flashcards/
   → study.views.generate_view
   → form.is_valid() → True
   → ai_service.generate_flashcards(text, 10)
     → detect_language() → 'ar'
     → call_deepseek_api() → JSON response
     → parse_flashcards_response() → [{'question': ..., 'answer': ...}, ...]
   → Create StudySet (owner=user, set_type='flashcards', language='ar')
   → Create 10 Flashcard objects
   → redirect('study:detail', pk=study_set.pk)
   ↓
5. GET /study/123/
   → study.views.study_set_detail
   → Check access: is_owner=True
   → Renders study/flashcards_view.html
   ↓
6. User clicks "مشاركة" button
   ↓
7. GET /posts/new/?study_set=123
   → posts.views.create_post
   → Preselects study set with pk=123
   → Renders posts/create.html
   ↓
8. User fills title, selects tags, clicks submit
   ↓
9. POST /posts/new/
   → posts.views.create_post
   → form.is_valid() → True
   → Create Post (author=user, study_set=study_set, title=...)
   → post.tags.set(selected_tags)
   → redirect('posts:detail', pk=post.pk)
   ↓
10. GET /posts/456/
    → posts.views.post_detail
    → Renders posts/detail.html
```

## Example 2: User Reports a Comment

```
1. User views post detail page
   GET /posts/456/
   → Renders posts/detail.html with comments
   → Each comment (not own) has report button
   ↓
2. User clicks report button on comment #789
   → Bootstrap modal opens (#reportModal-789)
   ↓
3. User selects reason "spam", clicks submit
   ↓
4. HTMX POST /admin-panel/report/submit/
   Headers: X-CSRFToken: ...
   Body: content_type=comment, object_id=789, reason=spam
   → admin_panel.views.submit_report
   → Validate content_type
   → Get ContentType for Comment model
   → Check comment exists and not deleted
   → Check not self-reporting
   → Check no duplicate report
   → Create Report object
   → Return HTML: '<div class="alert alert-success">تم إرسال البلاغ</div>'
   ↓
5. HTMX replaces #report-result-789 with success message
   → Modal shows success message
```

## Example 3: Admin Reviews Report

```
1. Admin clicks "لوحة الإدارة" in navbar dropdown
   ↓
2. GET /admin-panel/
   → admin_panel.views.dashboard
   → Check user.is_staff → True
   → Query metrics (counts, top posts, top tags)
   → Renders admin_panel/dashboard.html
   ↓
3. Admin sees pending report, clicks "عرض"
   ↓
4. GET /admin-panel/reports/101/
   → admin_panel.views.report_detail
   → Get report with pk=101
   → report.content_object → The Comment
   → Renders admin_panel/reports/detail.html
   ↓
5. Admin reads reported comment, decides to approve
   ↓
6. POST /admin-panel/reports/101/approve/
   → admin_panel.views.approve_report
   → Get report
   → report.content_object.deleted_at = now()  (Soft delete comment)
   → report.status = 'approved'
   → report.reviewed_by = admin_user
   → report.reviewed_at = now()
   → messages.success('تم قبول البلاغ وحذف المحتوى')
   → redirect('admin_panel:reports_list')
   ↓
7. GET /admin-panel/reports/
   → Shows success message
   → Report now in "approved" tab
```

---

# 15. File-by-File Reference

## Root Directory Files

| File | Purpose |
|------|---------|
| `manage.py` | Django CLI entry point. Run commands like `python manage.py runserver` |
| `requirements.txt` | Python package dependencies |
| `Dockerfile` | Instructions to build Django container |
| `docker-compose.yml` | Multi-container setup (web + database) |
| `entrypoint.sh` | Container startup script (wait for DB, migrate) |
| `.env` | Environment variables (secrets, config) |
| `README.md` | Arabic project setup instructions |
| `CLAUDE_CONTEXT.md` | Quick reference for AI assistants |
| `PROJECT_DOCUMENTATION.md` | This comprehensive guide |

## miftah/ (Django Project)

| File | Purpose |
|------|---------|
| `__init__.py` | Marks directory as Python package |
| `settings.py` | All Django configuration (database, apps, auth, etc.) |
| `urls.py` | Root URL router - dispatches to app URLs |
| `views.py` | Landing page and home page views |
| `wsgi.py` | WSGI entry point for production deployment |

## accounts/ (Authentication App)

| File | Purpose |
|------|---------|
| `__init__.py` | Python package marker |
| `models.py` | Profile and Follow models |
| `views.py` | Login, signup, profile, follow toggle views |
| `forms.py` | SignUpForm, LoginForm, ProfileForm |
| `urls.py` | URL patterns for accounts |
| `admin.py` | Register models in Django admin |
| `apps.py` | App configuration |
| `migrations/` | Database schema changes |

## study/ (AI Generation App)

| File | Purpose |
|------|---------|
| `__init__.py` | Python package marker |
| `models.py` | StudySet, Flashcard, QuizQuestion models |
| `views.py` | Generate, view, history, delete views |
| `forms.py` | GenerateStudySetForm |
| `urls.py` | URL patterns for study |
| `ai_service.py` | DeepSeek API integration, PDF extraction |
| `admin.py` | Register models in Django admin |
| `apps.py` | App configuration |
| `migrations/` | Database schema changes |

## posts/ (Social Posting App)

| File | Purpose |
|------|---------|
| `__init__.py` | Python package marker |
| `models.py` | Post, Tag, PostTag, Reaction, Comment models |
| `views.py` | Create, detail, delete, reaction, search views |
| `feed_views.py` | Recent and following feed views |
| `forms.py` | PostForm, CommentForm |
| `urls.py` | URL patterns for posts |
| `feed_urls.py` | URL patterns for feed |
| `admin.py` | Register models in Django admin |
| `apps.py` | App configuration |
| `management/commands/seed_tags.py` | Populate predefined tags |
| `migrations/` | Database schema changes |

## admin_panel/ (Moderation App)

| File | Purpose |
|------|---------|
| `__init__.py` | Python package marker |
| `models.py` | Report model with GenericForeignKey |
| `views.py` | Dashboard, reports list/detail, approve/dismiss |
| `forms.py` | ReportForm |
| `urls.py` | URL patterns for admin panel |
| `admin.py` | Register Report in Django admin |
| `apps.py` | App configuration |
| `migrations/` | Database schema changes |

## templates/ (HTML Templates)

| File | Purpose |
|------|---------|
| `base.html` | Master layout with navbar, CSS, JS |
| `landing.html` | Public landing page for guests |
| `home.html` | Dashboard for logged-in users |
| `accounts/login.html` | Login form |
| `accounts/signup.html` | Registration form |
| `accounts/profile.html` | User profile page |
| `accounts/edit_profile.html` | Edit profile form |
| `accounts/following_list.html` | List of followed users |
| `accounts/partials/follow_button.html` | HTMX follow/unfollow button |
| `study/generate.html` | AI generation form |
| `study/flashcards_view.html` | Interactive flashcard viewer |
| `study/quiz_view.html` | Quiz with scoring |
| `study/history.html` | User's study sets list |
| `study/confirm_delete.html` | Delete confirmation |
| `posts/create.html` | Create post form with tag selector |
| `posts/detail.html` | Post detail with comments |
| `posts/search.html` | Search results page |
| `posts/feed.html` | Feed page (recent/following tabs) |
| `posts/partials/post_card.html` | Reusable post card component |
| `posts/partials/post_list.html` | List of post cards |
| `posts/partials/reaction_buttons.html` | HTMX like/dislike buttons |
| `admin_panel/base_admin.html` | Admin layout with sidebar |
| `admin_panel/dashboard.html` | Metrics and stats |
| `admin_panel/reports/list.html` | Reports table |
| `admin_panel/reports/detail.html` | Single report view |
| `admin_panel/partials/report_modal.html` | Report submission modal |

---

# Appendix A: Common Commands

```bash
# Start the project
docker compose up -d --build

# View logs
docker compose logs -f web

# Run Django shell
docker compose exec web python manage.py shell

# Create migrations
docker compose exec web python manage.py makemigrations

# Apply migrations
docker compose exec web python manage.py migrate

# Seed tags
docker compose exec web python manage.py seed_tags

# Create superuser
docker compose exec web python manage.py createsuperuser

# Make user staff
docker compose exec web python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.get(username='USERNAME'); u.is_staff=True; u.save()"

# Stop containers
docker compose down

# Stop and remove volumes (WARNING: deletes database!)
docker compose down -v
```

---

# Appendix B: Glossary

| Term | Definition |
|------|------------|
| **Django** | Python web framework following MVT pattern |
| **ORM** | Object-Relational Mapping - interact with database using Python objects |
| **Migration** | Versioned database schema change |
| **View** | Function that handles HTTP request and returns response |
| **Template** | HTML file with Django template language |
| **Model** | Python class representing a database table |
| **ForeignKey** | Database relationship pointing to another table |
| **ManyToMany** | Relationship where multiple rows can relate to multiple rows |
| **HTMX** | JavaScript library for AJAX without writing JS |
| **CSRF** | Cross-Site Request Forgery protection |
| **RTL** | Right-to-Left text direction (for Arabic) |
| **Soft Delete** | Mark as deleted instead of actually removing |
| **GenericForeignKey** | Relationship that can point to any model |

---

**End of Documentation**

*This document was generated to provide complete understanding of the Miftah project. For updates, regenerate after significant changes.*
