# Claude Context File - Miftah Project

> This file contains all context needed for Claude to continue working on this project in a new chat.

## Project Overview

**Name:** مفتاح (Miftah) - meaning "Key" in Arabic
**Type:** Graduation project - educational website for Arab students
**Owner:** University student, beginner in backend development
**Status:** Core implementation complete, ready for testing and refinements

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
│   ├── models.py        # Post, Tag, Reaction, Comment
│   ├── views.py         # Create, detail, delete, reactions
│   ├── feed_views.py    # Recent feed, following feed
│   └── forms.py         # PostForm, CommentForm
├── templates/           # All HTML templates (Arabic RTL)
│   ├── base.html        # Main layout with navbar
│   ├── landing.html     # Public landing page
│   ├── home.html        # Main hub (flashcards/quiz options)
│   ├── accounts/        # Auth & profile templates
│   ├── study/           # Flashcard & quiz templates
│   └── posts/           # Post & feed templates
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
- **Tag**: name (unique), color derived from hash
- **Post**: author, study_set (required), title, caption, tags M2M, deleted_at (soft delete)
- **Reaction**: user, post, value (like/dislike) - unique per user/post
- **Comment**: post, author, body, deleted_at (soft delete)

## Key Features Implemented

1. ✅ User auth (signup, login, logout) - email/password only
2. ✅ Profile pages with bio
3. ✅ Follow system with "Follow Back" logic
4. ✅ AI flashcard generation from text/PDF
5. ✅ AI quiz generation (4 options, explanations)
6. ✅ Language detection (Arabic/English) - output matches input
7. ✅ Study set history page with filters
8. ✅ Posts (must include a study set)
9. ✅ Tags with deterministic colors
10. ✅ Like/Dislike reactions (mutually exclusive)
11. ✅ Comments (simple, no replies/reactions)
12. ✅ Feed pages (recent, following)
13. ✅ Search by keywords and tags
14. ✅ Arabic RTL UI throughout

## Important Design Decisions

1. **Posts MUST have a study set** - no standalone text posts
2. **UI is always Arabic** - only AI output matches input language
3. **Soft delete** for posts and comments (deleted_at field)
4. **Study set access**: owner always, others only if shared via post
5. **Single "تصفح" (Browse) button** in navbar goes to /feed/recent, then tabs for recent/following

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
- `/posts/new/` - Create post
- `/posts/<id>/` - Post detail
- `/feed/recent/`, `/feed/following/`

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
- Report system
- Edit posts (currently only delete)

## Known Issues / Notes

- None reported yet - project just completed initial implementation
- Test the AI generation once DeepSeek API key is added to .env

---

**Last Updated:** Initial implementation complete
**Chat Status:** Context memory near full, continuing in new chat
