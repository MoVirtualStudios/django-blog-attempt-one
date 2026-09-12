from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views


from .import views
from .forms import LoginForm

app_name = "accounts"

urlpatterns = [

    path("login/", auth_views.LoginView.as_view(authentication_form=LoginForm), name="login",),

    path("logout/", auth_views.LogoutView.as_view(next_page="blog:post_list",), name="logout",),

    path(
        "register/",
        views.register,
        name="register",
        ),

    path(
        "profile/",
        views.profile_edit,
        name="profile_edit",
        ),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard",
        ),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),

    path(
        "<str:username>/",
        views.author_detail,
        name="author_detail",
    ),


]