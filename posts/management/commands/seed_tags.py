"""
Management command to seed predefined tags.
"""

from django.core.management.base import BaseCommand
from posts.models import Tag


class Command(BaseCommand):
    help = 'Seeds the database with predefined educational tags'

    def handle(self, *args, **options):
        tags_data = [
            # العلوم الطبيعية - Natural Sciences
            {'name': 'فيزياء', 'color': '#6366f1'},
            {'name': 'كيمياء', 'color': '#8b5cf6'},
            {'name': 'أحياء', 'color': '#22c55e'},
            {'name': 'رياضيات', 'color': '#3b82f6'},
            {'name': 'علوم الأرض', 'color': '#a16207'},
            {'name': 'فلك', 'color': '#1e3a5f'},

            # اللغات - Languages
            {'name': 'لغات', 'color': '#059669'},

            # العلوم الإنسانية - Humanities
            {'name': 'تاريخ', 'color': '#78350f'},
            {'name': 'جغرافيا', 'color': '#16a34a'},
            {'name': 'فلسفة', 'color': '#7c3aed'},
            {'name': 'علم النفس', 'color': '#ec4899'},
            {'name': 'علم الاجتماع', 'color': '#14b8a6'},
            {'name': 'تربية', 'color': '#f43f5e'},

            # التقنية وتكنولوجيا المعلومات - Technology & IT
            {'name': 'برمجة', 'color': '#0ea5e9'},
            {'name': 'ذكاء اصطناعي', 'color': '#6366f1'},
            {'name': 'أمن سيبراني', 'color': '#ef4444'},
            {'name': 'شبكات', 'color': '#0891b2'},
            {'name': 'قواعد بيانات', 'color': '#4f46e5'},
            {'name': 'تصميم', 'color': '#d946ef'},
            {'name': 'تطوير الويب', 'color': '#06b6d4'},
            {'name': 'تطوير التطبيقات', 'color': '#0284c7'},
            {'name': 'علم البيانات', 'color': '#7c3aed'},
            {'name': 'تعلم الآلة', 'color': '#8b5cf6'},
            {'name': 'الحوسبة السحابية', 'color': '#0369a1'},
            {'name': 'نظم التشغيل', 'color': '#475569'},
            {'name': 'إنترنت الأشياء', 'color': '#14b8a6'},
            {'name': 'الواقع الافتراضي', 'color': '#a855f7'},
            {'name': 'تحليل النظم', 'color': '#64748b'},
            {'name': 'إدارة المشاريع التقنية', 'color': '#1e40af'},

            # العلوم الإسلامية - Islamic Studies
            {'name': 'قرآن كريم', 'color': '#15803d'},
            {'name': 'حديث شريف', 'color': '#166534'},
            {'name': 'فقه', 'color': '#14532d'},
            {'name': 'عقيدة', 'color': '#0f766e'},
            {'name': 'سيرة نبوية', 'color': '#047857'},
            {'name': 'تجويد', 'color': '#0d9488'},

            # إدارة الأعمال - Business
            {'name': 'إدارة أعمال', 'color': '#0369a1'},
            {'name': 'محاسبة', 'color': '#1d4ed8'},
            {'name': 'اقتصاد', 'color': '#7e22ce'},
            {'name': 'تسويق', 'color': '#c026d3'},
            {'name': 'ريادة أعمال', 'color': '#db2777'},

            # الطب والصحة - Medical & Health
            {'name': 'طب', 'color': '#dc2626'},
            {'name': 'تمريض', 'color': '#e11d48'},
            {'name': 'صيدلة', 'color': '#9333ea'},
            {'name': 'تغذية', 'color': '#84cc16'},
            {'name': 'صحة عامة', 'color': '#22d3ee'},

            # الهندسة - Engineering (single consolidated tag)
            {'name': 'هندسة', 'color': '#ca8a04'},

            # أخرى - Other
            {'name': 'فنون', 'color': '#f472b6'},
            {'name': 'موسيقى', 'color': '#a78bfa'},
            {'name': 'رياضة', 'color': '#fb923c'},
            {'name': 'قانون', 'color': '#475569'},
            {'name': 'إعلام', 'color': '#38bdf8'},
            {'name': 'أخرى', 'color': '#94a3b8'},
        ]

        # Old tags to remove (consolidated into single tags)
        old_tags_to_remove = [
            # Old engineering tags (now 'هندسة')
            'هندسة مدنية', 'هندسة كهربائية', 'هندسة ميكانيكية', 'هندسة معمارية',
            'هندسة كيميائية', 'هندسة حاسوب', 'هندسة اتصالات', 'هندسة صناعية',
            'هندسة بيئية', 'هندسة نووية', 'هندسة بترول', 'هندسة طبية حيوية',
            'هندسة طيران', 'هندسة بحرية', 'هندسة زراعية', 'هندسة تعدين',
            'هندسة جيولوجية', 'ميكاترونكس', 'هندسة روبوتات', 'هندسة البرمجيات',
            # Old language tags (now 'لغات')
            'اللغة العربية', 'اللغة الإنجليزية', 'اللغة الفرنسية',
            'اللغة الألمانية', 'اللغة الإسبانية'
        ]

        # Delete old tags
        deleted_count = Tag.objects.filter(name__in=old_tags_to_remove).delete()[0]

        created_count = 0
        updated_count = 0

        for tag_data in tags_data:
            tag, created = Tag.objects.update_or_create(
                name=tag_data['name'],
                defaults={'color': tag_data['color']}
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'تم حذف {deleted_count} تصنيف قديم، إنشاء {created_count} تصنيف جديد، وتحديث {updated_count} تصنيف موجود.'
            )
        )
