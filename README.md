# مفتاح (Miftah) - منصة تعليمية للطلاب العرب

منصة تعليمية ذكية تساعد الطلاب على تحويل النصوص وملفات PDF إلى بطاقات تعليمية واختبارات تفاعلية باستخدام الذكاء الاصطناعي.

## المميزات

- **بطاقات تعليمية (Flashcards)**: إنشاء بطاقات بتأثير القلب للمراجعة
- **اختبارات متعددة الخيارات (Quiz)**: أسئلة مع 4 خيارات وشرح لكل إجابة
- **دعم ثنائي اللغة**: يدعم العربية والإنجليزية (يكتشف اللغة تلقائياً)
- **نظام المتابعة**: متابعة المستخدمين ومشاهدة منشوراتهم
- **التفاعلات**: إعجاب وعدم إعجاب على المنشورات
- **التعليقات**: التعليق على المنشورات
- **البحث**: البحث بالكلمات والوسوم

---

## متطلبات التشغيل

1. **Docker Desktop**: يجب أن يكون مثبتاً وقيد التشغيل
2. **مفتاح DeepSeek API**: احصل عليه من https://platform.deepseek.com/

---

## طريقة التشغيل

### الخطوة 1: التحقق من Docker

افتح PowerShell أو Command Prompt واكتب:

```bash
docker version
```

إذا ظهرت معلومات الإصدار، فـ Docker يعمل. إذا ظهر خطأ، تأكد أن Docker Desktop قيد التشغيل.

### الخطوة 2: إعداد ملف البيئة

1. افتح الملف `.env` في المشروع
2. أضف مفتاح DeepSeek API الخاص بك:

```
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

### الخطوة 3: تشغيل المشروع

من مجلد المشروع، اكتب:

```bash
docker compose up -d --build
```

انتظر حتى يكتمل البناء (قد يستغرق عدة دقائق في المرة الأولى).

### الخطوة 4: التحقق من التشغيل

```bash
docker compose ps
```

يجب أن ترى حاويتين (containers) تعملان:
- `miftah_web` - تطبيق Django
- `miftah_db` - قاعدة البيانات PostgreSQL

### الخطوة 5: إنشاء حساب مدير (اختياري)

```bash
docker compose exec web python manage.py createsuperuser
```

### الخطوة 6: فتح التطبيق

افتح المتصفح واذهب إلى:

```
http://localhost:8000
```

---

## الأوامر المفيدة

### عرض سجلات التطبيق (Logs)

```bash
# سجلات Django
docker compose logs -f web

# سجلات قاعدة البيانات
docker compose logs -f db
```

### إيقاف التطبيق

```bash
docker compose down
```

### إعادة تشغيل التطبيق

```bash
docker compose restart
```

### حذف كل شيء والبدء من جديد

```bash
docker compose down -v
docker compose up -d --build
```

⚠️ **تحذير**: هذا سيحذف جميع البيانات في قاعدة البيانات!

---

## حل المشاكل الشائعة

### المنفذ 8000 مستخدم

غيّر `WEB_PORT` في ملف `.env`:

```
WEB_PORT=8001
```

ثم أعد التشغيل:

```bash
docker compose down
docker compose up -d
```

### المنفذ 5433 مستخدم

غيّر `DB_HOST_PORT` في ملف `.env`:

```
DB_HOST_PORT=5434
```

### قاعدة البيانات غير جاهزة

انتظر بضع ثوانٍ ثم حاول مرة أخرى. البرنامج ينتظر تلقائياً حتى تكون قاعدة البيانات جاهزة.

### خطأ في الاتصال بـ DeepSeek

تأكد من:
1. مفتاح API صحيح في ملف `.env`
2. لديك اتصال بالإنترنت
3. حسابك في DeepSeek نشط ولديه رصيد

---

## هيكل المشروع

```
graduation_project/
├── miftah/              # إعدادات Django الرئيسية
│   ├── settings.py      # الإعدادات
│   ├── urls.py          # الروابط الرئيسية
│   └── views.py         # الصفحة الرئيسية
├── accounts/            # نظام المستخدمين
│   ├── models.py        # Profile, Follow
│   ├── views.py         # تسجيل الدخول، الملف الشخصي
│   └── forms.py         # نماذج التسجيل
├── study/               # المجموعات الدراسية
│   ├── models.py        # StudySet, Flashcard, QuizQuestion
│   ├── ai_service.py    # التكامل مع DeepSeek
│   └── views.py         # إنشاء وعرض المجموعات
├── posts/               # المنشورات
│   ├── models.py        # Post, Tag, Reaction, Comment
│   ├── views.py         # إنشاء وعرض المنشورات
│   └── feed_views.py    # صفحات التغذية
├── templates/           # قوالب HTML
├── static/              # ملفات CSS و JS
├── docker-compose.yml   # إعدادات Docker
├── Dockerfile           # بناء الصورة
└── requirements.txt     # المكتبات المطلوبة
```

---

## قاعدة البيانات

### الجداول الرئيسية

| الجدول | الوصف |
|--------|-------|
| `User` | المستخدمون (من Django) |
| `Profile` | معلومات إضافية للمستخدم |
| `Follow` | علاقات المتابعة |
| `StudySet` | المجموعات الدراسية |
| `Flashcard` | البطاقات التعليمية |
| `QuizQuestion` | أسئلة الاختبار |
| `Post` | المنشورات |
| `Tag` | الوسوم |
| `Reaction` | الإعجابات |
| `Comment` | التعليقات |

### الدخول لقاعدة البيانات

```bash
docker compose exec db psql -U miftah_user -d miftah_db
```

---

## التقنيات المستخدمة

- **Backend**: Django 5
- **Database**: PostgreSQL 16
- **AI**: DeepSeek API
- **Frontend**: Bootstrap 5 RTL + HTMX
- **Containerization**: Docker

---

## للمطورين

### تشغيل الأوامر داخل الحاوية

```bash
# تشغيل migrations
docker compose exec web python manage.py migrate

# إنشاء migration جديد
docker compose exec web python manage.py makemigrations

# فتح Django shell
docker compose exec web python manage.py shell
```

### الوصول لـ Django Admin

1. أنشئ superuser (انظر الخطوة 5 أعلاه)
2. اذهب إلى: http://localhost:8000/admin/

---

## الترخيص

مشروع تخرج - للاستخدام التعليمي فقط
