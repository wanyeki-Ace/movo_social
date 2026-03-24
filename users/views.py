from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import User, Follow
from .forms import RegisterForm, LoginForm, ProfileEditForm
from dsa.graph import Graph
from dsa.hash_table import HashTable


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Movo, {user.username}!')
            return redirect('feed')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('feed')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.posts.all()
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    # Build graph for mutual follow suggestions using DSA Graph
    graph = Graph()
    all_follows = Follow.objects.select_related('follower', 'following').all()
    for follow in all_follows:
        graph.add_follow(follow.follower.id, follow.following.id)

    mutual_follows = []
    if profile_user != request.user:
        mutual_ids = graph.get_mutual_follows(request.user.id, profile_user.id)
        mutual_follows = list(User.objects.filter(id__in=mutual_ids)[:5])

    return render(request, 'users/profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,
        'mutual_follows': mutual_follows,
        'followers_count': profile_user.followers_count(),
        'following_count': profile_user.following_count(),
    })


@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow != request.user:
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow,
        )
        if not created:
            follow.delete()
            action = 'unfollowed'
        else:
            action = 'followed'

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'action': action,
                'followers_count': user_to_follow.followers_count(),
            })

    return redirect('profile', username=username)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def get_recommendations(request):
    """
    Uses DSA Graph + BFS to find users the current user may want to follow.
    Returns a list of dicts: [{'user': User, 'score': int}, ...]
    """
    graph = Graph()
    all_follows = Follow.objects.select_related('follower', 'following').all()
    for follow in all_follows:
        graph.add_follow(follow.follower.id, follow.following.id)

    recommendations = graph.bfs_recommendations(request.user.id, max_recommendations=5)
    recommended_users = []
    for user_id, score in recommendations:
        try:
            user = User.objects.get(id=user_id)
            recommended_users.append({'user': user, 'score': score})
        except User.DoesNotExist:
            pass

    return recommended_users
