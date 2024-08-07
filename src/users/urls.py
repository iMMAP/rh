from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import path

from .views import users as users_views
from .views import auth as auth_views
from .forms import UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm

urlpatterns = [
    # Profile routes
    path("profile/", users_views.profile, name="profile"),
    path("users/organization", users_views.org_users_list, name="users-organization"),
    path("users/<int:user_id>/toggle_status", users_views.toggle_status, name="toggle-status"),
    path("login/", auth_views.login_view, name="login"),
    path("logout/", auth_views.logout_view, name="logout"),
    path("register/", auth_views.register_view, name="register"),
    # Password change routes
    path(
        "password_change/",
        PasswordChangeView.as_view(
            template_name="users/auth/password_change.html",
            form_class=UserPasswordChangeForm,
        ),
        name="password_change",
    ),
    path(
        "password_change/done/",
        PasswordChangeDoneView.as_view(template_name="users/auth/password_change_done.html"),
        name="password_change_done",
    ),
    # Password reset routes
    path(
        "password_reset/",
        PasswordResetView.as_view(
            template_name="users/auth/password_reset.html",
            form_class=UserPasswordResetForm,
            html_email_template_name="users/emails/password_reset_email.html",
            subject_template_name="users/emails/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        PasswordResetDoneView.as_view(template_name="users/auth/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/auth/password_reset_confirm.html",
            form_class=UserSetPasswordForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(template_name="users/auth/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    path(
        "activate/<uidb64>/<token>",
        auth_views.activate_account,
        name="activate_account",
    ),
]
