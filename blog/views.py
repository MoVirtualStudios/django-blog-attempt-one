import time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.urls import reverse

from .forms import CommentForm, ContactForm, PostForm
from .models import Category, Comment, Post, Tag


def post_list(request):
    posts = (
        Post.objects
        .published()
        .with_counts()
        .select_related("author", "category")
        .prefetch_related("tags")
        .order_by("-published_at")
    )

    paginator = Paginator(posts, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/post_list.html",
        {
            "page_obj": page_obj,
        },
    )


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects
        .published()
        .with_counts()
        .select_related("author", "category")
        .prefetch_related("tags"),
        slug=slug,
    )

    user_bookmarked = False
    user_liked = False

    if request.user.is_authenticated:
        user_bookmarked = post.bookmarks.filter(
            pk=request.user.pk,
        ).exists()

        user_liked = post.likes.filter(
            pk=request.user.pk,
        ).exists()

    bookmark_count = getattr(
        post,
        "bookmark_total",
        None,
    )

    if bookmark_count is None:
        bookmark_count = post.bookmarks.count()

    like_count = getattr(
        post,
        "like_total",
        None,
    )

    if like_count is None:
        like_count = post.likes.count()

    post.view_count += 1

    post.save(
        update_fields=[
            "view_count",
        ],
    )

    comments = post.comments.filter(
        approved=True,
    )


    tag_ids = list(
    post.tags.values_list(
        "id",
        flat=True,
        )
    )

    related_filter = Q()

    if post.category_id:
        related_filter |= Q(
            category_id=post.category_id,
        )

    if tag_ids:
        related_filter |= Q(
            tags__id__in=tag_ids,
        )

    if related_filter:
        related_posts = (
            Post.objects
            .published()
            .with_counts()
            .filter(related_filter)
            .exclude(pk=post.pk)
            .select_related("author", "category")
            .prefetch_related("tags")
            .distinct()
            .order_by("-published_at")[:3]
        )

    else:
        related_posts = (
            Post.objects
            .published()
            .with_counts()
            .exclude(pk=post.pk)
            .select_related("author", "category")
            .prefetch_related("tags")
            .order_by("-published_at")[:3]
        )


    if request.method == "POST":
        comment_form = CommentForm(
            request.POST,
        )

        if comment_form.is_valid():
            comment = comment_form.save(
                commit=False,
            )

            comment.post = post

            comment.save()

            messages.success(
                request,
                "Your comment has been submitted and is awaiting moderation.",
            )

            return redirect(
                post.get_absolute_url(),
            )

    else:
        comment_form = CommentForm(
            initial={
                "timestamp": time.time(),
            },
        )

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_form": comment_form,
            "user_bookmarked": user_bookmarked,
            "bookmark_count": bookmark_count,
            "user_liked": user_liked,
            "like_count": like_count,
            "related_posts": related_posts,
        },
    )


def category_posts(request, slug):
    category = get_object_or_404(
        Category,
        slug=slug,
    )

    posts = (
        Post.objects
        .published()
        .with_counts()
        .filter(
            category=category,
        )
        .select_related("author", "category")
        .prefetch_related("tags")
        .order_by("-published_at")
    )

    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/category_posts.html",
        {
            "category": category,
            "page_obj": page_obj,
        },
    )


def tag_posts(request, slug):
    tag = get_object_or_404(
        Tag,
        slug=slug,
    )

    posts = (
        Post.objects
        .published()
        .with_counts()
        .filter(
            tags=tag,
        )
        .select_related("author", "category")
        .prefetch_related("tags")
        .order_by("-published_at")
    )

    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/category_posts.html",
        {
            "tag": tag,
            "page_obj": page_obj,
        },
    )


def search_posts(request):
    query = request.GET.get(
        "q",
        "",
    ).strip()

    posts = Post.objects.none()

    if query:
        posts = (
            Post.objects
            .published()
            .with_counts()
            .filter(
                Q(title__icontains=query)
                | Q(body__icontains=query)
                | Q(category__name__icontains=query)
                | Q(tags__name__icontains=query)
            )
            .select_related("author", "category")
            .prefetch_related("tags")
            .distinct()
            .order_by("-published_at")
        )

    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/search_results.html",
        {
            "query": query,
            "page_obj": page_obj,
        },
    )

def about(request):

    return render(
        request,
        "blog/about.html",
    )

def contact(request):

    if request.method == "POST":

        form = ContactForm(
            request.POST,
        )

        if form.is_valid():

            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            full_message = (
                f"Name: {name}\n"
                f"Email: {email}\n\n"
                f"Message:\n{message}"
            )

            send_mail(
                subject=f"Contact Form: {subject}",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[
                    getattr(
                        settings,
                        "CONTACT_EMAIL",
                        settings.DEFAULT_FROM_EMAIL,
                    ),
                ],
                fail_silently=False,
            )

            messages.success(
                request,
                "Your message has been sent successfully.",
            )

            return redirect(
                "blog:contact",
            )

    else:

        form = ContactForm()

    return render(
        request,
        "blog/contact.html",
        {
            "form": form,
        },
    )

@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            post = form.save(
                commit=False,
            )

            post.author = request.user

            if (
                post.status == Post.Status.PUBLISHED
                and post.published_at is None
            ):
                post.published_at = timezone.now()

            post.save()

            form.save_m2m()

            messages.success(
                request,
                "Post saved successfully.",
            )

            if post.status == Post.Status.PUBLISHED:
                return redirect(
                    "blog:post_detail",
                    slug=post.slug,
                )

            return redirect(
                "accounts:dashboard",
            )

    else:
        form = PostForm()

    return render(
        request,
        "blog/post_form.html",
        {
            "form": form,
        },
    )


@login_required
def post_edit(request, pk):
    post = get_object_or_404(
        Post,
        pk=pk,
        author=request.user,
    )

    if request.method == "POST":
        form = PostForm(
            request.POST,
            request.FILES,
            instance=post,
        )

        if form.is_valid():
            post = form.save(
                commit=False,
            )

            if (
                post.status == Post.Status.PUBLISHED
                and post.published_at is None
            ):
                post.published_at = timezone.now()

            post.save()

            form.save_m2m()

            messages.success(
                request,
                "Post updated successfully.",
            )

            if post.status == Post.Status.PUBLISHED:
                return redirect(
                    "blog:post_detail",
                    slug=post.slug,
                )

            return redirect(
                "accounts:dashboard",
            )

    else:
        form = PostForm(
            instance=post,
        )

    return render(
        request,
        "blog/post_form.html",
        {
            "form": form,
            "editing": True,
            "post": post,
        },
    )


@login_required
def post_delete(request, pk):
    post = get_object_or_404(
        Post,
        pk=pk,
        author=request.user,
    )

    if request.method == "POST":
        post.delete()

        messages.success(
            request,
            "Post deleted successfully.",
        )

        return redirect(
            "accounts:dashboard",
        )

    return render(
        request,
        "blog/post_confirm_delete.html",
        {
            "post": post,
        },
    )


@login_required
def my_posts(request):
    posts = (
        Post.objects
        .filter(
            author=request.user,
        )
        .with_counts()
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-updated_at")
    )

    paginator = Paginator(
        posts,
        10,
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number,
    )

    return render(
        request,
        "blog/my_posts.html",
        {
            "page_obj": page_obj,
        },
    )


@login_required
def comment_list(request):
    comments = (
        Comment.objects
        .filter(
            post__author=request.user,
        )
        .select_related("post")
        .order_by("-created_at")
    )

    return render(
        request,
        "blog/comment_list.html",
        {
            "comments": comments,
        },
    )


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(
        Comment,
        pk=pk,
        post__author=request.user,
    )

    comment.approved = True

    comment.save(
        update_fields=[
            "approved",
        ],
    )

    messages.success(
        request,
        "Comment approved successfully.",
    )

    return redirect(
        "blog:comment_list",
    )


@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(
        Comment,
        pk=pk,
        post__author=request.user,
    )

    if request.method == "POST":
        comment.delete()

        messages.success(
            request,
            "Comment deleted successfully.",
        )

        return redirect(
            "blog:comment_list",
        )

    return render(
        request,
        "blog/comment_confirm_delete.html",
        {
            "comment": comment,
        },
    )


@login_required
@require_POST
def post_bookmark_toggle(request, pk):
    post = get_object_or_404(
        Post.objects.published(),
        pk=pk,
    )

    bookmarked = post.bookmarks.filter(
        pk=request.user.pk,
    ).exists()

    if bookmarked:
        post.bookmarks.remove(
            request.user,
        )

        messages.info(
            request,
            "Post removed from your bookmarks.",
        )

    else:
        post.bookmarks.add(
            request.user,
        )

        messages.success(
            request,
            "Post added to your bookmarks.",
        )

    next_url = request.POST.get("next") or post.get_absolute_url()

    return redirect(
        next_url,
    )


@login_required
def bookmark_list(request):
    posts = (
        Post.objects
        .published()
        .with_counts()
        .filter(
            bookmarks=request.user,
        )
        .select_related("author", "category")
        .prefetch_related("tags")
        .order_by("-published_at")
    )

    paginator = Paginator(posts, 9)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/bookmark_list.html",
        {
            "page_obj": page_obj,
        },
    )


@login_required
@require_POST
def post_like_toggle(request, pk):
    post = get_object_or_404(
        Post.objects.published(),
        pk=pk,
    )

    liked = post.likes.filter(
        pk=request.user.pk,
    ).exists()

    if liked:
        post.likes.remove(
            request.user,
        )

        messages.info(
            request,
            "Post unliked.",
        )

    else:
        post.likes.add(
            request.user,
        )

        messages.success(
            request,
            "Post liked.",
        )

    next_url = request.POST.get("next") or post.get_absolute_url()

    return redirect(
        next_url,
    )


def custom_404(request, exception):

    return render(
        request,
        "404.html",
        status=404,
    )


def custom_500(request):

    return render(
        request,
        "500.html",
        status=500,
    )


def robots_txt(request):

    sitemap_url = (
        f"{request.scheme}://"
        f"{request.get_host()}"
        f"{reverse('django.contrib.sitemaps.views.sitemap')}"
    )

    content = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            f"Sitemap: {sitemap_url}",
        ]
    )

    return HttpResponse(
        content,
        content_type="text/plain",
    )