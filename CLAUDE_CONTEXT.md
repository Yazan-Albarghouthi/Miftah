# Claude Context File - Miftah Project

> This file contains all context needed for Claude to continue working on this project in a new chat.

## Project Overview

**Name:** مفتاح (Miftah) - meaning "Key" in Arabic
**Type:** Graduation project - educational website for Arab students
**Owner:** University student, beginner in backend development
**Status:** Core implementation complete with tag system, HTMX interactions, and admin dashboard

## Tech Stack

- **Backend:** Django 5 (Python)
- **Database:** PostgreSQL 16 (Docker container)
- **Frontend:** Django templates + Bootstrap 5 RTL + HTMX
- **AI:** DeepSeek API (not OpenAI) - configured in `study/ai_service.py`
- **Containerization:** Docker + Docker Compose
- **Environment:** Windows + Docker Desktop + VSCode

## How to Run

```bash
# Start the project
docker compose up -d --build

# View logs
docker compose logs -f web

# Seed predefined tags (REQUIRED after fresh setup)
docker compose exec web python manage.py seed_tags

# Access at http://localhost:8000
```

## Project Structure

```
graduation_project/
├── miftah/              # Django project settings
│   ├── settings.py      # Main config, DB, DeepSeek API key
│   ├── urls.py          # Root URL routing
│   └── views.py         # Landing page, home page
├── accounts/            # User authentication & social
│   ├── models.py        # Profile, Follow
│   ├── views.py         # Login, signup, profile, follow toggle
│   └── forms.py         # SignUpForm, LoginForm, ProfileForm
├── study/               # AI-generated study sets
│   ├── models.py        # StudySet, Flashcard, QuizQuestion
│   ├── ai_service.py    # DeepSeek integration, PDF extraction
│   ├── views.py         # Generate, view, history, delete
│   └── forms.py         # GenerateStudySetForm
├── posts/               # Social posting system
│   ├── models.py        # Post, Tag, Reaction, Comment, PostTag
│   ├── views.py         # Create, detail, delete, reactions, search
│   ├── forms.py         # PostForm (with tag selection), CommentForm
│   └── management/commands/
│       └── seed_tags.py # Populates 52 predefined tags
├── feed/                # Feed views
│   └── views.py         # Recent feed, following feed
├── admin_panel/         # Admin dashboard & reporting
│   ├── models.py        # Report model (GenericForeignKey)
│   ├── views.py         # Dashboard, reports list/detail, approve/dismiss
│   ├── urls.py          # Admin panel URL routing
│   └── forms.py         # ReportForm
├── templates/           # All HTML templates (Arabic RTL)
│   ├── base.html        # Main layout with navbar + HTMX CSRF config + CSS
│   ├── landing.html     # Public landing page
│   ├── home.html        # Main hub (flashcards/quiz options)
│   ├── accounts/        # Auth & profile templates
│   │   └── partials/follow_button.html  # HTMX follow toggle
│   ├── study/           # Flashcard & quiz templates
│   │   └── generate.html # PDF warnings included
│   ├── posts/           # Post & feed templates
│   │   ├── search.html  # Compact tag filter chips
│   │   └── partials/
│   │       ├── post_card.html      # Clickable post card
│   │       └── reaction_buttons.html # Like/dislike HTMX
│   └── admin_panel/     # Admin dashboard templates
│       ├── base_admin.html         # Admin layout with sidebar
│       ├── dashboard.html          # Stats and metrics
│       ├── reports/list.html       # Reports list with filters
│       ├── reports/detail.html     # Report detail + actions
│       └── partials/report_modal.html # User report submission modal
├── docker-compose.yml   # Docker services config
├── Dockerfile           # Django container
├── entrypoint.sh        # Wait-for-db + migrations
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (API keys)
└── README.md            # Arabic setup instructions
```

## Database Models

### accounts app
- **Profile**: OneToOne with User, bio, created_at
- **Follow**: follower → following (unique together, no self-follow)

### study app
- **StudySet**: owner, set_type (flashcards/quiz), language (ar/en), title, source_text
- **Flashcard**: study_set FK, index, question, answer
- **QuizQuestion**: study_set FK, index, question, options (JSON), correct_index, explanation

### posts app
- **Tag**: name (unique), color (CharField, stored in DB) - predefined tags only
- **Post**: author, study_set (required), title, caption, tags M2M through PostTag, deleted_at
- **PostTag**: Through model for Post-Tag M2M
- **Reaction**: user, post, value (like/dislike) - unique per user/post
- **Comment**: post, author, body, deleted_at (soft delete)

### admin_panel app
- **Report**: reporter, content_type (GenericFK), object_id, reason (choices), details, status (pending/approved/dismissed), reviewed_by, reviewed_at, created_at
  - Uses GenericForeignKey to support reporting both Posts and Comments
  - unique_together on (reporter, content_type, object_id) prevents duplicate reports

## Key Features Implemented

1. ✅ User auth (signup, login, logout) - email/password only
2. ✅ Profile pages with bio
3. ✅ Follow system with "Follow Back" logic
4. ✅ AI flashcard generation from text/PDF
5. ✅ AI quiz generation (4 options, explanations)
6. ✅ Language detection (Arabic/English) - output matches input
7. ✅ Study set history page with filters
8. ✅ Posts (must include a study set)
9. ✅ **Predefined tag system** - 52 tags, searchable selector, 1-4 per post
10. ✅ Like/Dislike reactions (HTMX, mutually exclusive)
11. ✅ Comments (simple, no replies/reactions)
12. ✅ Feed pages (recent, following)
13. ✅ Search by keywords and tags (compact tag chips, auto-submit)
14. ✅ Arabic RTL UI throughout
15. ✅ HTMX CSRF handling (global config in base.html)
16. ✅ PDF upload warnings (OCR, large files)
17. ✅ **Report system** - users can report posts/comments with reasons
18. ✅ **Admin dashboard** - staff-only panel with metrics and report management

## Tag System (Important!)

Tags are **predefined** - users select from existing tags, they cannot create new ones.

**52 predefined tags** organized by category:
- العلوم الطبيعية: فيزياء، كيمياء، أحياء، رياضيات، علوم الأرض، فلك
- لغات: (single consolidated tag for all languages)
- العلوم الإنسانية: تاريخ، جغرافيا، فلسفة، علم النفس، علم الاجتماع، تربية
- التقنية وIT: برمجة، ذكاء اصطناعي، أمن سيبراني، شبكات، قواعد بيانات، تصميم، تطوير الويب، تطوير التطبيقات، علم البيانات، تعلم الآلة، الحوسبة السحابية، نظم التشغيل، إنترنت الأشياء، الواقع الافتراضي، تحليل النظم، إدارة المشاريع التقنية
- العلوم الإسلامية: قرآن كريم، حديث شريف، فقه، عقيدة، سيرة نبوية، تجويد
- إدارة الأعمال: إدارة أعمال، محاسبة، اقتصاد، تسويق، ريادة أعمال
- الطب والصحة: طب، تمريض، صيدلة، تغذية، صحة عامة
- هندسة: (single consolidated tag for all engineering types)
- أخرى: فنون، موسيقى، رياضة، قانون، إعلام، أخرى

**To add/update tags:**
```bash
docker compose exec web python manage.py seed_tags
```

**Tag selection UI (Create Post):**
- Searchable filter input
- Clickable chips with colors from DB
- Selected tags shown at top with X to remove
- Max 4 tags, min 1 tag per post

**Tag filter UI (Search Page):**
- Compact pill-shaped chips (smaller than create post)
- Click to toggle filter (auto-submits form)
- Selected tags show their color, unselected are gray

## HTMX Configuration

HTMX is used for interactive features without page reload:
- Follow/unfollow button
- Like/dislike reactions
- Report submission (modal form)
- Comment deletion

**CSRF Token Handling** (in base.html):
```html
<script>
    document.body.addEventListener('htmx:configRequest', function(event) {
        event.detail.headers['X-CSRFToken'] = '{{ csrf_token }}';
    });
</script>
```

Individual HTMX elements also include `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'` as backup.

## Admin Dashboard & Report System

**Admin Panel** (`/admin-panel/`) - Staff only (user.is_staff):
- Dashboard with metrics (total users/posts/comments, posts in 24h/7d, top liked posts, popular tags)
- Reports list with status filters (pending, approved, dismissed, all)
- Report detail page with approve/dismiss actions
- Approve = soft-delete content + mark report approved
- Dismiss = mark report dismissed, no action on content

**Report System** (for all users):
- Report button on posts (if not owner) and comments (if not author)
- Bootstrap modal with reason selection (hate speech, spam, inappropriate, misinformation, harassment, other)
- Optional details field
- HTMX submission with success/error feedback
- Prevents duplicate reports from same user
- Prevents self-reporting

**Report Reasons:**
- خطاب كراهية (hate_speech)
- محتوى مزعج (spam)
- محتوى غير لائق (inappropriate)
- معلومات مضللة (misinformation)
- تحرش أو إساءة (harassment)
- أخرى (other)

**Staff Access:**
- Staff link in navbar dropdown (only visible to staff users)
- All admin views use `@user_passes_test(staff_required)` decorator

## Important Design Decisions

1. **Posts MUST have a study set** - no standalone text posts
2. **UI is always Arabic** - only AI output matches input language
3. **Soft delete** for posts and comments (deleted_at field)
4. **Study set access**: owner always, others only if shared via post
5. **Single "تصفح" (Browse) button** in navbar → /feed/recent with tabs
6. **Predefined tags only** - users cannot create new tags
7. **Post cards are fully clickable** using Bootstrap stretched-link
8. **Consolidated tags** - هندسة (all engineering), لغات (all languages)
9. **Staff-only admin** - uses Django's `is_staff` field for access control

## User Authority & Management

Django has three authority levels:
- **is_active**: Can login (True by default)
- **is_staff**: Can access admin panel (our custom dashboard + Django admin)
- **is_superuser**: Full permissions, can do everything

**Management commands:**
```bash
# Make user a staff member
docker compose exec web python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.get(username='USERNAME'); u.is_staff=True; u.save()"

# Remove staff status
docker compose exec web python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.get(username='USERNAME'); u.is_staff=False; u.save()"

# Make superuser (full authority)
docker compose exec web python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.get(username='USERNAME'); u.is_staff=True; u.is_superuser=True; u.save()"

# Create new superuser interactively
docker compose exec web python manage.py createsuperuser
```

## Environment Variables (.env)

```
DEBUG=True
SECRET_KEY=...
DB_NAME=miftah_db
DB_USER=miftah_user
DB_PASSWORD=miftah_password
DB_HOST_PORT=5433
WEB_PORT=8000
DEEPSEEK_API_KEY=sk-...  # Required for AI features
```

## URLs Structure

- `/` - Landing (unauthenticated)
- `/home/` - Main hub
- `/accounts/login/`, `/accounts/signup/`, `/accounts/logout/`
- `/accounts/u/<username>/` - Profile
- `/accounts/following/` - Who I follow
- `/study/generate/flashcards/`, `/study/generate/quiz/`
- `/study/history/` - My study sets
- `/study/<id>/` - View study set
- `/posts/new/` - Create post (with tag selector)
- `/posts/<id>/` - Post detail
- `/posts/search/` - Search posts
- `/feed/recent/`, `/feed/following/`
- `/admin-panel/` - Admin dashboard (staff only)
- `/admin-panel/reports/` - Reports list
- `/admin-panel/reports/<id>/` - Report detail
- `/admin-panel/report/submit/` - Submit report (POST)

## User Preferences (from conversation)

- Keep things simple - beginner friendly
- No production/deployment concerns
- Minimal README files but with sufficient info
- Ask questions when things are ambiguous
- DeepSeek API (not OpenAI)

## Potential Future Improvements (not implemented)

- Password reset
- Usage limits for AI generation
- Public/private toggle for study sets
- Bookmark/save others' posts
- Edit posts (currently only delete)

## PDF Handling

- Max file size: 10MB (client-side validation + server-side)
- Uses pypdf for text extraction
- Warnings displayed in UI:
  - OCR PDFs (scanned images) cannot extract text
  - Large files (>5MB) may take longer to process
  - Files >10MB are rejected with error message
- Extracted text must be at least 50 characters

## CSS Classes (in base.html)

- `.tag-badge` - Standard tag display (posts, cards)
- `.search-tag-chip` - Compact tags for search page filter
- `.study-card` - Hoverable card with shadow effect
- `.flashcard` / `.flashcard-inner` - Flip card animation
- `.quiz-option` - Quiz answer choices
- `.reaction-btn` / `.active-like` / `.active-dislike` - Reaction buttons

## Known Issues / Notes

- OCR PDF files may fail to extract text (shows warning to user)
- Test the AI generation once DeepSeek API key is added to .env

---

**Last Updated:** Admin dashboard & report system complete with bug fixes
**Recent Changes:**
- Added admin_panel app with Report model (GenericForeignKey for posts/comments)
- Created custom admin dashboard with metrics (users, posts, comments, top posts, popular tags)
- Implemented report system with reason choices and HTMX submission
- Added report buttons on posts (if not owner) and comments (if not author)
- Staff-only access using `is_staff` check
- Bootstrap modal for report submission
- Reports management: list, detail, approve (soft-delete), dismiss
- Staff link in navbar dropdown (لوحة الإدارة)
- Created admin test user: admin / admin123
- **Bug fix:** Comment report modal ID mismatch - fixed button target from `#reportModal-comment-{{ comment.pk }}` to `#reportModal-{{ comment.pk }}`
