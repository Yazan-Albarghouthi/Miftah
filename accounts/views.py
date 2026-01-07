"""
Views for user authentication, profiles, and follow system.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.http import require_POST

from .forms import SignUpForm, LoginForm, ProfileForm, UserUpdateForm
from .models import Follow


def signup_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'تم إنشاء حسابك بنجاح! مرحباً بك في مفتاح.')
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'مرحباً {user.username}!')
            # Redirect to next page if specified, otherwise home
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, 'تم تسجيل خروجك بنجاح.')
    return redirect('landing')


@login_required
def profile_view(request, username):
    """View a user's profile."""
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user == profile_user

    # Get follow status
    is_following = False
    follows_me = False

    if not is_own_profile:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile_user
        ).exists()
        follows_me = Follow.objects.filter(
            follower=profile_user,
            following=request.user
        ).exists()

    # Get user's posts (non-deleted)
    from posts.models import Post
    posts = Post.objects.filter(
        author=profile_user,
        deleted_at__isnull=True
    ).order_by('-created_at')

    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'is_following': is_following,
        'follows_me': follows_me,
        'posts': posts,
    }

    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    """Edit own profile."""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'تم تحديث ملفك الشخصي بنجاح.')
            return redirect('accounts:profile', username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
@require_POST
def toggle_follow(request, username):
    """Toggle follow/unfollow a user. Returns HTMX partial."""
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        return HttpResponse('لا يمكنك متابعة نفسك', status=400)

    follow_exists = Follow.objects.filter(
        follower=request.user,
        following=target_user
    ).exists()

    if follow_exists:
        # Unfollow
        Follow.objects.filter(
            follower=request.user,
            following=target_user
        ).delete()
        is_following = False
    else:
        # Follow
        Follow.objects.create(
            follower=request.user,
            following=target_user
        )
        is_following = True

    # Check if they follow me (for follow back button)
    follows_me = Follow.objects.filter(
        follower=target_user,
        following=request.user
    ).exists()

    # Return updated button HTML for HTMX
    return render(request, 'accounts/partials/follow_button.html', {
        'profile_user': target_user,
        'is_following': is_following,
        'follows_me': follows_me,
    })


@login_required
def following_list(request):
    """Show list of users the current user follows."""
    following = Follow.objects.filter(
        follower=request.user
    ).select_related('following', 'following__profile').order_by('-created_at')

    return render(request, 'accounts/following_list.html', {
        'following': following,
    })


@login_required
def followers_list(request, username):
    """Show list of users following a specific user."""
    profile_user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(
        following=profile_user
    ).select_related('follower', 'follower__profile').order_by('-created_at')

    return render(request, 'accounts/followers_list.html', {
        'profile_user': profile_user,
        'followers': followers,
    })
