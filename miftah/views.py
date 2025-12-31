"""
Main views for Miftah project.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def landing(request):
    """Landing page - shown to non-authenticated users."""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'landing.html')


@login_required
def home(request):
    """Home page - main hub for generating study sets."""
    return render(request, 'home.html')
