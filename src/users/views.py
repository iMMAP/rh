from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.cache import cache_control

from rh.models import Cluster, Location, Organization

from .decorators import unauthenticated_user
from .forms import (
    ProfileCreateForm,
    ProfileUpdateForm,
    UserRegisterForm,
    UserUpdateForm,
)
from .tokens import account_activation_token


#############################################
########### Authntication Views #############
#############################################
def activate_account(request, uidb64, token):
    """Activate User account"""
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception as e:
        messages.error(request, f"{e} - Something went wrong!")
        return redirect("login")

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for your email confirmation, you can login now into your account.")
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect("login")


def send_account_activation_email(request, user, to_email):
    """Email verification for resigtration"""
    current_site = get_current_site(request)
    mail_subject = "Email Activation link"
    message = loader.render_to_string(
        "users/registration/activation_email_template.html",
        {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
            "protocol": "https" if request.is_secure() else "http",
        },
    )

    email = EmailMultiAlternatives(mail_subject, "Testing", to=[to_email])
    email.attach_alternative(message, "text/html")
    if email.send():
        template = loader.get_template("users/registration/activation_email_done.html")
        context = {"user": user, "to_email": to_email}
        return HttpResponse(template.render(context, request))
    else:
        messages.error(
            request,
            f"""Problem sending email to <b>{to_email}</b>m check if you typed it correctly.""",
        )


@cache_control(no_store=True)
@unauthenticated_user
def register_view(request):
    """Registration view for creating new signing up"""
    template = loader.get_template("users/registration/signup.html")
    organizations = Organization.objects.all().order_by("code").values()
    clusters = Cluster.objects.all().order_by("title").values()
    locations = Location.objects.all().order_by("name").values()

    if request.method == "POST":
        u_form = UserRegisterForm(request.POST)
        p_form = ProfileCreateForm(request.POST)
        if u_form.is_valid() and p_form.is_valid():
            username = u_form.cleaned_data.get("username")
            email = u_form.clean_email()

            # Registration with email confirmation step.
            if settings.DEBUG:
                # If development mode then go ahead and create the user.
                user = u_form.save()
                user_profile = p_form.save(commit=False)
                user_profile.user = user

                user_profile.save()
                p_form.save_m2m()
                messages.success(request, f"Account created successfully for {username}.")
                return redirect("login")
            else:
                # If production mode send a verification email to the user for account activation
                user = u_form.save(commit=False)
                user.is_active = False
                user.save()
                user_profile = p_form.save(commit=False)
                user_profile.user = user

                user_profile.save()
                p_form.save_m2m()
                return send_account_activation_email(request, user, email)
        # else:
        #     for error in list(u_form.errors.values()):
        #         messages.error(request, error)
        #     for error in list(p_form.errors.values()):
        #         messages.error(request, error)
    else:
        u_form = UserRegisterForm()
        p_form = ProfileCreateForm()

    context = {
        "u_form": u_form,
        "p_form": p_form,
        "organizations": organizations,
        "clusters": clusters,
        "locations": locations,
    }
    return HttpResponse(template.render(context, request))


@cache_control(no_store=True)
@unauthenticated_user
def login_view(request):
    """User Login View"""
    template = loader.get_template("users/registration/login.html")
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST.get("password")
        user = authenticate(request, username=email, email=email, password=password)

        if user is not None:
            login(request, user)
            if "next" in request.POST:
                return redirect(request.POST.get("next"))
            return redirect("landing")
        else:
            messages.error(request, "Enter correct email and password.")
    context = {}
    return HttpResponse(template.render(context, request))


def logout_view(request):
    """User Logout View"""
    messages.info(request, f"{request.user} logged out.")
    logout(request)
    return redirect("/login")


#############################################
############### Profile Views #################
#############################################
@cache_control(no_store=True)
@login_required
def profile(request):
    template = loader.get_template("users/profile.html")
    user = request.user

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileUpdateForm(request.POST, instance=user.profile)

        if u_form.is_valid() and p_form.is_valid():
            user = u_form.save()
            user_profile = p_form.save(commit=False)

            user_profile.save()
            p_form.save_m2m()
            messages.success(request, "Profile Updated successfully")
            return redirect("profile")

        else:
            for error in list(u_form.errors.values()):
                messages.error(request, error)
            for error in list(p_form.errors.values()):
                messages.error(request, error)
    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=user.profile)

    context = {
        "user": user,
        "u_form": u_form,
        "p_form": p_form,
    }
    return HttpResponse(template.render(context, request))
