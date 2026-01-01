"""
Views for admin panel and content moderation.
"""

from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.utils import timezone

from posts.models import Post, Comment, Tag
from .models import Report
from .forms import ReportForm


def staff_required(user):
    """Check if user is staff."""
    return user.is_authenticated and user.is_staff


# =============================================================================
# ADMIN DASHBOARD VIEWS (Staff only)
# =============================================================================

@login_required
@user_passes_test(staff_required, login_url='home')
def dashboard(request):
    """Main admin dashboard with statistics."""
    now = timezone.now()

    # Basic counts
    total_users = User.objects.count()
    total_posts = Post.objects.filter(deleted_at__isnull=True).count()
    total_comments = Comment.objects.filter(deleted_at__isnull=True).count()

    # Posts in timeframes
    posts_24h = Post.objects.filter(
        deleted_at__isnull=True,
        created_at__gte=now - timedelta(hours=24)
    ).count()

    posts_7d = Post.objects.filter(
        deleted_at__isnull=True,
        created_at__gte=now - timedelta(days=7)
    ).count()

    # Top 5 most liked posts
    top_posts = Post.objects.filter(
        deleted_at__isnull=True
    ).annotate(
        like_count=Count('reactions', filter=Q(reactions__value='like'))
    ).order_by('-like_count')[:5]

    # Most used tags (top 10)
    top_tags = Tag.objects.annotate(
        post_count=Count('posts', filter=Q(posts__deleted_at__isnull=True))
    ).order_by('-post_count')[:10]

    # Pending reports
    pending_reports_count = Report.objects.filter(status='pending').count()

    # Recent reports
    recent_reports = Report.objects.filter(status='pending').order_by('-created_at')[:5]

    context = {
        'total_users': total_users,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'posts_24h': posts_24h,
        'posts_7d': posts_7d,
        'top_posts': top_posts,
        'top_tags': top_tags,
        'pending_reports_count': pending_reports_count,
        'recent_reports': recent_reports,
    }

    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@user_passes_test(staff_required, login_url='home')
def reports_list(request):
    """List all reports with filtering."""
    status_filter = request.GET.get('status', 'pending')

    if status_filter == 'all':
        reports = Report.objects.all()
    else:
        reports = Report.objects.filter(status=status_filter)

    # Pending count for badge
    pending_reports_count = Report.objects.filter(status='pending').count()

    context = {
        'reports': reports,
        'status_filter': status_filter,
        'pending_reports_count': pending_reports_count,
    }

    return render(request, 'admin_panel/reports/list.html', context)


@login_required
@user_passes_test(staff_required, login_url='home')
def report_detail(request, pk):
    """View single report details."""
    report = get_object_or_404(Report, pk=pk)

    # Pending count for badge
    pending_reports_count = Report.objects.filter(status='pending').count()

    context = {
        'report': report,
        'pending_reports_count': pending_reports_count,
    }

    return render(request, 'admin_panel/reports/detail.html', context)


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

    # Check if HTMX request
    if request.headers.get('HX-Request'):
        return HttpResponse(
            '<div class="alert alert-success">تم قبول البلاغ وحذف المحتوى.</div>'
        )

    return redirect('admin_panel:reports_list')


@login_required
@user_passes_test(staff_required, login_url='home')
@require_POST
def dismiss_report(request, pk):
    """Dismiss report (mark as reviewed, no action)."""
    report = get_object_or_404(Report, pk=pk)

    # Update report status
    report.status = 'dismissed'
    report.reviewed_by = request.user
    report.reviewed_at = timezone.now()
    report.save()

    messages.success(request, 'تم رفض البلاغ.')

    # Check if HTMX request
    if request.headers.get('HX-Request'):
        return HttpResponse(
            '<div class="alert alert-secondary">تم رفض البلاغ.</div>'
        )

    return redirect('admin_panel:reports_list')


# =============================================================================
# REPORT SUBMISSION VIEWS (For users)
# =============================================================================

@login_required
@require_POST
def submit_report(request):
    """Submit a report for content."""
    content_type_str = request.POST.get('content_type')
    object_id = request.POST.get('object_id')
    reason = request.POST.get('reason')
    details = request.POST.get('details', '')

    # Validate content type
    if content_type_str not in ['post', 'comment']:
        if request.headers.get('HX-Request'):
            return HttpResponse(
                '<div class="alert alert-danger">نوع المحتوى غير صالح.</div>'
            )
        messages.error(request, 'نوع المحتوى غير صالح.')
        return redirect('home')

    # Get content type
    if content_type_str == 'post':
        content_type = ContentType.objects.get_for_model(Post)
        content = Post.objects.filter(pk=object_id, deleted_at__isnull=True).first()
    else:
        content_type = ContentType.objects.get_for_model(Comment)
        content = Comment.objects.filter(pk=object_id, deleted_at__isnull=True).first()

    # Validate content exists
    if not content:
        if request.headers.get('HX-Request'):
            return HttpResponse(
                '<div class="alert alert-danger">المحتوى غير موجود.</div>'
            )
        messages.error(request, 'المحتوى غير موجود.')
        return redirect('home')

    # Prevent self-reporting
    if hasattr(content, 'author') and content.author == request.user:
        if request.headers.get('HX-Request'):
            return HttpResponse(
                '<div class="alert alert-warning">لا يمكنك الإبلاغ عن محتواك.</div>'
            )
        messages.warning(request, 'لا يمكنك الإبلاغ عن محتواك.')
        return redirect('home')

    # Check for duplicate report
    existing_report = Report.objects.filter(
        reporter=request.user,
        content_type=content_type,
        object_id=object_id
    ).exists()

    if existing_report:
        if request.headers.get('HX-Request'):
            return HttpResponse(
                '<div class="alert alert-info">لقد قمت بالإبلاغ عن هذا المحتوى مسبقاً.</div>'
            )
        messages.info(request, 'لقد قمت بالإبلاغ عن هذا المحتوى مسبقاً.')
        return redirect('home')

    # Validate reason
    valid_reasons = [choice[0] for choice in Report.REASON_CHOICES]
    if reason not in valid_reasons:
        if request.headers.get('HX-Request'):
            return HttpResponse(
                '<div class="alert alert-danger">يرجى اختيار سبب صالح للبلاغ.</div>'
            )
        messages.error(request, 'يرجى اختيار سبب صالح للبلاغ.')
        return redirect('home')

    # Create report
    Report.objects.create(
        reporter=request.user,
        content_type=content_type,
        object_id=object_id,
        reason=reason,
        details=details
    )

    if request.headers.get('HX-Request'):
        return HttpResponse(
            '<div class="alert alert-success">'
            '<i class="bi bi-check-circle me-2"></i>'
            'تم إرسال البلاغ بنجاح. سيتم مراجعته من قبل الإدارة.'
            '</div>'
        )

    messages.success(request, 'تم إرسال البلاغ بنجاح. سيتم مراجعته من قبل الإدارة.')
    return redirect('home')
