"""
Views for feed pages (recent and following).
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Post, Tag
from accounts.models import Follow


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

    posts = posts.select_related('author', 'study_set').prefetch_related('tags').order_by('-created_at')

    # Get all tags for filter
    all_tags = Tag.objects.all().order_by('name')

    context = {
        'posts': posts,
        'query': query,
        'tag_filter': tag_filter,
        'all_tags': all_tags,
        'feed_type': 'recent',
    }

    if request.headers.get('HX-Request'):
        return render(request, 'posts/partials/post_list.html', context)

    return render(request, 'posts/feed.html', context)


@login_required
def following_feed(request):
    """Show posts from users that the current user follows."""
    query = request.GET.get('q', '').strip()
    tag_filter = request.GET.getlist('tags')

    # Get users that current user follows
    following_users = Follow.objects.filter(
        follower=request.user
    ).values_list('following', flat=True)

    posts = Post.objects.filter(
        author__in=following_users,
        deleted_at__isnull=True
    )

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(caption__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    if tag_filter:
        for tag_name in tag_filter:
            posts = posts.filter(tags__name=tag_name)

    posts = posts.select_related('author', 'study_set').prefetch_related('tags').order_by('-created_at')

    # Get all tags for filter
    all_tags = Tag.objects.all().order_by('name')

    context = {
        'posts': posts,
        'query': query,
        'tag_filter': tag_filter,
        'all_tags': all_tags,
        'feed_type': 'following',
        'following_count': len(following_users),
    }

    if request.headers.get('HX-Request'):
        return render(request, 'posts/partials/post_list.html', context)

    return render(request, 'posts/feed.html', context)
