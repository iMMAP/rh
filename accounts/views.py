from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader


from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site  

from django.utils.encoding import force_bytes, force_str  
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  

from django.core.mail import EmailMessage  
from django.views.decorators.cache import cache_control
from django.conf import settings

from .models import *
from .forms import *
from .decorators import unauthenticated_user
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
    except:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for your email confirmation, you can login now into your account.")
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('login')


def send_account_activation_email(request, user, to_email):
    """Email verification for resigtration """
    current_site = get_current_site(request)  
    mail_subject = 'Activation link has been sent to your email id'  
    message = loader.render_to_string('registration/activation_email_template.html', {  
        'user': user,  
        'domain': current_site.domain,  
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),  
        'token': account_activation_token.make_token(user),  
        'protocol': 'https' if request.is_secure() else 'http', 
    })  
    email = EmailMessage(  
        mail_subject, message, to=[to_email]  
    )
    if email.send():
        template = loader.get_template('registration/activation_email_done.html')
        context = {'user': user, 'to_email': to_email}
        return HttpResponse(template.render(context, request))
    else:
        messages.error(request, 
            f"""Problem sending email to <b>{to_email}</b>m check if you typed it correctly."""
        )


@cache_control(no_store=True)
@unauthenticated_user
def register_view(request):
    """Registration view for creating new signing up"""
    template = loader.get_template('registration/signup.html')
    form = RegisterForm()
    organizations = Organization.objects.all()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            # Registration with email confirmation step.
            if settings.DEBUG==True:
                # If development mode then go ahead and create the user.
                user = form.save()
                messages.success(request, f'Account created successfully for {username}.')
            else:
                # If production mode send a verification email to the user for account activation
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                return send_account_activation_email(request, user, email)  
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
        
    context = {'form': form, 'organizations': organizations}
    return HttpResponse(template.render(context, request))


@cache_control(no_store=True)
@unauthenticated_user
def login_view(request):
    """User Login View """
    template = loader.get_template('registration/login.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            return redirect('index')
        else:
            messages.error(request, f'Enter correct username and password.')
    context = {}
    return HttpResponse(template.render(context, request))


def logout_view(request):
    """User Logout View"""
    messages.info(request, f'{request.user} logged out.')
    logout(request)
    return redirect("/login")


#############################################
############### Profile Views #################
#############################################
@cache_control(no_store=True)
@login_required
def profile(request):
    template = loader.get_template('profile.html')
    user = request.user
    context = {'user': user}
    return HttpResponse(template.render(context, request))
