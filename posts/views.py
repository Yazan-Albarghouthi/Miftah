"""
Views for posts, reactions, and comments.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q

from .models import Post, Tag, Reaction, Comment
from .forms import PostForm, CommentForm
from study.models import StudySet


@login_required
def create_post(request):
    """Create a new post."""
    # Get pre-selected study set if provided
    study_set_id = request.GET.get('study_set')
    preselected_study_set = None

    if study_set_id:
        preselected_study_set = get_object_or_404(
            StudySet, pk=study_set_id, owner=request.user
        )

    # Get all tags for the selector
    all_tags = Tag.objects.all().order_by('name')

    if request.method == 'POST':
        form = PostForm(request.POST)
        study_set_id = request.POST.get('study_set')

        if not study_set_id:
            messages.error(request, 'يرجى اختيار مجموعة دراسية.')
            return render(request, 'posts/create.html', {
                'form': form,
                'study_sets': StudySet.objects.filter(owner=request.user),
                'preselected_study_set': preselected_study_set,
                'all_tags': all_tags,
            })

        study_set = get_object_or_404(StudySet, pk=study_set_id, owner=request.user)

        if form.is_valid():
            post = form.save(author=request.user, study_set=study_set)
            messages.success(request, 'تم نشر المنشور بنجاح!')
            return redirect('posts:detail', pk=post.pk)
    else:
        form = PostForm()

    # Get user's study sets for picker
    study_sets = StudySet.objects.filter(owner=request.user).order_by('-created_at')

    return render(request, 'posts/create.html', {
        'form': form,
        'study_sets': study_sets,
        'preselected_study_set': preselected_study_set,
        'all_tags': all_tags,
    })


@login_required
def post_detail(request, pk):
    """View post details."""
    post = get_object_or_404(Post, pk=pk, deleted_at__isnull=True)

    # Handle comment submission
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'تم إضافة تعليقك.')
            return redirect('posts:detail', pk=pk)
    else:
        comment_form = CommentForm()

    # Get user's reaction
    user_reaction = post.get_user_reaction(request.user)

    # Get comments
    comments = post.comments.filter(deleted_at__isnull=True)

    return render(request, 'posts/detail.html', {
        'post': post,
        'comment_form': comment_form,
        'comments': comments,
        'user_reaction': user_reaction,
        'is_owner': post.author == request.user,
    })


@login_required
@require_POST
def delete_post(request, pk):
    """Soft delete a post."""
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.deleted_at = timezone.now()
    post.save()
    messages.success(request, 'تم حذف المنشور.')
    return redirect('feed:recent')


@login_required
@require_POST
def toggle_reaction(request, pk):
    """Toggle like/dislike on a post. Returns HTMX partial."""
    post = get_object_or_404(Post, pk=pk, deleted_at__isnull=True)
    reaction_type = request.POST.get('type')  # 'like' or 'dislike'

    if reaction_type not in ['like', 'dislike']:
        return HttpResponse('نوع تفاعل غير صالح', status=400)

    existing = Reaction.objects.filter(user=request.user, post=post).first()

    if existing:
        if existing.value == reaction_type:
            # Same reaction - remove it
            existing.delete()
        else:
            # Different reaction - update it
            existing.value = reaction_type
            existing.save()
    else:
        # New reaction
        Reaction.objects.create(user=request.user, post=post, value=reaction_type)

    # Return updated reaction buttons
    return render(request, 'posts/partials/reaction_buttons.html', {
        'post': post,
        'user_reaction': post.get_user_reaction(request.user),
    })


@login_required
@require_POST
def delete_comment(request, pk):
    """Soft delete a comment."""
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    comment.deleted_at = timezone.now()
    comment.save()

    if request.headers.get('HX-Request'):
        return HttpResponse('')  # HTMX will remove the element
    return redirect('posts:detail', pk=comment.post.pk)


@login_required
def search_posts(request):
    """Search posts by keywords and tags."""
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

    posts = posts.order_by('-created_at')

    # Get all tags for filter
    all_tags = Tag.objects.all().order_by('name')

    context = {
        'posts': posts,
        'query': query,
        'tag_filter': tag_filter,
        'all_tags': all_tags,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'posts/partials/post_list.html', context)

    return render(request, 'posts/search.html', context)
