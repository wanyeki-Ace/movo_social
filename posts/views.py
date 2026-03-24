from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

from .models import Post, Like, Comment, Repost
from .forms import PostForm, CommentForm
from users.models import User, Follow
from dsa.heap import MaxHeap
from dsa.hash_table import HashTable


def _build_liked_ht(user):
    """Build a HashTable of post IDs liked by `user` for O(1) lookups."""
    ht = HashTable()
    for post_id in Like.objects.filter(user=user).values_list('post_id', flat=True):
        ht.set(str(post_id), True)
    return ht


def _build_reposted_ht(user):
    """Build a HashTable of post IDs reposted by `user` for O(1) lookups."""
    ht = HashTable()
    for post_id in Repost.objects.filter(user=user).values_list('post_id', flat=True):
        ht.set(str(post_id), True)
    return ht


@login_required
def feed(request):
    following_ids = request.user.following.values_list('following_id', flat=True)
    all_ids = list(following_ids) + [request.user.id]
    posts = (
        Post.objects
        .filter(author_id__in=all_ids)
        .select_related('author')
        .prefetch_related('likes', 'comments')
    )

    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created!')
            return redirect('feed')

    # DSA: HashTable for O(1) liked-post lookup
    liked_ht = _build_liked_ht(request.user)
    reposted_ht = _build_reposted_ht(request.user)
    posts_with_liked = [
        {'post': p, 'liked': str(p.id) in liked_ht, 'reposted': str(p.id) in reposted_ht}
        for p in posts
    ]

    # DSA: BFS graph recommendations
    from users.views import get_recommendations
    recommendations = get_recommendations(request)

    return render(request, 'posts/feed.html', {
        'posts': posts_with_liked,
        'form': form,
        'recommendations': recommendations,
    })


@login_required
def explore(request):
    """Trending posts ranked by DSA MaxHeap."""
    all_posts = (
        Post.objects
        .select_related('author')
        .prefetch_related('likes', 'comments')
        .all()
    )
    trending = MaxHeap.get_trending_posts(all_posts, n=20)

    liked_ht = _build_liked_ht(request.user)
    reposted_ht = _build_reposted_ht(request.user)
    posts_with_liked = [
        {'post': p, 'liked': str(p.id) in liked_ht, 'reposted': str(p.id) in reposted_ht}
        for p in trending
    ]

    following_ids = set(request.user.following.values_list('following_id', flat=True))
    suggested_users = (
        User.objects
        .exclude(id=request.user.id)
        .exclude(id__in=following_ids)
        .order_by('?')[:5]
    )

    return render(request, 'posts/explore.html', {
        'posts': posts_with_liked,
        'suggested_users': suggested_users,
    })


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.select_related('author').all()
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', post_id=post_id)

    liked = Like.objects.filter(user=request.user, post=post).exists()
    reposted = Repost.objects.filter(user=request.user, post=post).exists()
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'liked': liked,
        'reposted': reposted,
    })


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'count': post.likes_count()})

    return redirect(request.META.get('HTTP_REFERER', 'feed'))


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
    return redirect('feed')


@login_required
def repost_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    repost, created = Repost.objects.get_or_create(user=request.user, post=post)
    if not created:
        repost.delete()
        reposted = False
    else:
        reposted = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'reposted': reposted, 'count': post.reposts_count()})

    return redirect(request.META.get('HTTP_REFERER', 'feed'))
