from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.models import Group, User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives, send_mail
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from ..decorators import unauthenticated_user
from ..forms import (
    ProfileCreateForm,
    UserRegisterForm,
)
from ..tokens import activation_token_generator

def activate_account(request, uidb64, token):
    """Activate User account"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if user is not None and activation_token_generator.check_token(user, token):  
            user.profile.email_verified_at = datetime.now()
            user.profile.save()

            messages.success(request, "Thank you for your email confirmation, you can login now into your account.")

            return redirect("login")
        else:
            messages.error(request,"Invalid link")
            return redirect("login")

    except Exception as e:
        messages.error(request, f"{e} - Something went wrong!")
        return redirect("login")

@unauthenticated_user
def register_view(request):
    if request.method == "POST":
        u_form = UserRegisterForm(request.POST)
        p_form = ProfileCreateForm(request.POST)

        if u_form.is_valid() and p_form.is_valid():
            user = u_form.save(commit=False)
            user.is_active = False
            user.save()

            user_profile = p_form.save(commit=False)
            user_profile.user = user

            user_profile.save()
            p_form.save_m2m()

            user.groups.add(Group.objects.get(name="ORG_USER"))

            # inform the org admins
            send_account_notification_email(request, user)
            # send activation email
            send_account_activation_email(request, user)

            messages.success(request, "Activation link sent to your email address")

            return redirect(to="login")
    else:
        u_form = UserRegisterForm()
        p_form = ProfileCreateForm()

    context = {
        "u_form": u_form,
        "p_form": p_form,
    }
    return render(request, "users/auth/signup.html", context)


def send_account_activation_email(request, user):
    current_site = get_current_site(request)
    mail_subject = "Email Activation link"

    context = {
        "user": user,
        "domain": current_site.domain,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": activation_token_generator.make_token(user),
    }

    message = loader.render_to_string(template_name="users/emails/activation_email_template.html", context=context)

    send_mail(
        subject=mail_subject,
        message=message,
        from_email=None,
        recipient_list=[user.email],
        html_message=message,
    )


@unauthenticated_user
def login_view(request):
    template = loader.get_template("users/auth/login.html")
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST.get("password")
        user = authenticate(request, username=email, email=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if user.last_login:
                    messages.success(request, f"Welcome back {user}")
                else:
                    messages.success(request, f"Welcome {user} ! You've successfully logged in.")
                if "next" in request.POST:
                    return redirect(request.POST.get("next"))
                return redirect("landing")
            else:
                if not user.profile.email_verified_at:
                    # User is not verified, send them another verification email
                    send_account_activation_email(request=request, user=user)
                    messages.info(
                        request,
                        "Your account is not verified. We have sent you an email with instructions to verify your account.",
                    )
                else:
                    messages.error(request, "This account is deactivated. Please contact support.")
        else:
            messages.error(request, "Enter correct email or password.")
    context = {}
    return HttpResponse(template.render(context, request))


def logout_view(request):
    """User Logout View"""
    messages.info(request, f"{request.user} logged out.")
    logout(request)
    return redirect("/login")


def send_account_notification_email(request, user):
    """Email notification for new user registration"""
    # get organization admins
    user_org = user.profile.organization
    User = get_user_model()
    org_admin_group = Group.objects.get(name="ORG_LEAD")
    org_admins = User.objects.filter(groups=org_admin_group, profile__organization=user_org)

    current_site = get_current_site(request)
    mail_subject = "New User Registeration "
    for admin in org_admins:
        message = loader.render_to_string(
            "users/emails/notification_email_template.html",
            {
                "user": user,
                "domain": current_site.domain,
                "username": user.username,
                "protocol": "https" if request.is_secure() else "http",
                "admin": admin,
            },
        )
        email = EmailMultiAlternatives(mail_subject, "Testing", to=[admin.email])
        email.attach_alternative(message, "text/html")
        email.send()
    return
