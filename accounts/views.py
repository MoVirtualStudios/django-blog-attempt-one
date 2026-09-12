from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

from blog.models import Post

from .models import Profile
from .forms import RegisterForm
from .forms import ProfileForm

User = get_user_model()


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(
                request, user,
            )
            messages.success(request, "Welcome! Your acccount has been created successfully!")
            return redirect("blog:post_list")
    else:
        form = RegisterForm()
    return render(
        request, "registration/register.html", {"form": form,},
    )



def author_detail(request, username):
    author = get_object_or_404(
        User,
        username=username,
    )

    profile = Profile.objects.filter(
        user=author,
    ).first()

    posts = Post.objects.published().filter(
        author=author,
    )

    paginator = Paginator(posts, 5)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "accounts/author_detail.html",
        {
            "author": author,
            "profile": profile,
            "page_obj": page_obj,
        },
    )


@login_required
def profile_edit(request):

    profile = request.user.profile

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
        )

        if form.is_valid():
            form.save()
            return redirect(
                "accounts:profile_edit"
            )
    else:
        form = ProfileForm(
            instance=profile,
        )
    return render(request, "accounts/profile_edit.html", {"form": form, "profile": profile,},)


@login_required
def dashboard(request):
    posts = Post.objects.filter(author=request.user,)
    published_posts=posts.filter(status=Post.Status.PUBLISHED,)
    draft_posts=posts.filter(status=Post.Status.DRAFT,)
    context={
        "published_count":published_posts.count(),
        "draft_count":draft_posts.count(),
        "recent_posts":posts.order_by("-created_at")[:5],
    }
    return render(request, "accounts/dashboard.html", context,)