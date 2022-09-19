import pandas as pd
import datetime
import sqlite3
import json

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
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


@cache_control(no_store=True)
def index(request):
    template = loader.get_template('index.html')

    play_db = settings.PLAY_DB
    con = sqlite3.connect(play_db)

    play = con.execute("""
SELECT 
DATE('2022-0' || (r.month +1) || '-01') as month,
SUM(boys) + SUM(girls) + SUM(men) + SUM(women) + SUM(elderly_women) + SUM(elderly_men) AS people_recieved
FROM benef b 
INNER JOIN report r on b.report_id=r.id
INNER JOIN activity a on a.id = b.activity_id
INNER JOIN project p on p.id=r.project_id
INNER JOIN org o on o.id=p.org_id
INNER JOIN locs on locs.id = b.loc_id
WHERE substr(locs.code, 0, 3) = 'AF' AND 
o.short <> 'iMMAP' AND 
r.year = 2022
GROUP BY r.month
ORDER BY month
""")

    types = []
    nb_benef = []
    for x in play:
        types.append(
            datetime.date.fromisoformat(x[0]).strftime('%B')
        )
        nb_benef.append(x[1])

    
    months = str(types[0:10])
    benefs = str(nb_benef[0:10])

    df = pd.read_sql("""
SELECT 
DATE('2022-0' || (r.month +1) || '-01') as month, p.cluster,
--a.activity_type || ' - ' || a.activity_desc as activity,
SUM(boys) + SUM(girls) + SUM(men) + SUM(women) + SUM(elderly_women) + SUM(elderly_men) AS people_recieved
FROM benef b 
INNER JOIN report r on b.report_id=r.id
INNER JOIN activity a on a.id = b.activity_id
INNER JOIN project p on p.id=r.project_id
INNER JOIN org o on o.id=p.org_id
INNER JOIN locs on locs.id = b.loc_id
WHERE substr(locs.code, 0, 3) = 'AF' AND 
o.short <> 'iMMAP' AND 
r.year = 2022 AND
p.cluster IN ('ESNFI', 'FSAC', 'Protection', 'WASH')
GROUP BY r.month, p.cluster
ORDER BY month, cluster;
    """, con=con)
    
    clusters = df.pivot(index='month', columns='cluster', values='people_recieved').convert_dtypes().fillna(0).to_dict('list')

    df = pd.read_sql("""
    SELECT 
a.activity_type || ' - ' || a.activity_desc as activity, o.short, l2.name,
printf("%,d", SUM(boys) + SUM(girls) + SUM(men) + SUM(women) + SUM(elderly_women) + SUM(elderly_men)) AS people_recieved
FROM benef b 
INNER JOIN report r on b.report_id=r.id
INNER JOIN activity a on a.id = b.activity_id
INNER JOIN project p on p.id=r.project_id
INNER JOIN org o on o.id=p.org_id
INNER JOIN locs on locs.id = b.loc_id
INNER JOIN locs l2 on locs.parent_id = l2.id
WHERE substr(locs.code, 0, 3) = 'AF' AND 
o.short <> 'iMMAP' AND 
r.year = 2022 AND
r.month = 6 AND r.status='complete'
GROUP BY l2.id, activity_type, activity_desc HAVING people_recieved IS NOT NULL
ORDER BY month, l2.name, people_recieved desc;
    """, con=con)

    activities = df.to_dict('records')
    # import pdb; pdb.set_trace()
    context = {
        'months': months, 
        'benefs': benefs,
        'ESNFI': clusters['ESNFI'],
        'FSAC': clusters['FSAC'],
        'Protection': clusters['Protection'],
        'WASH': clusters['WASH'],
        'activities': activities,
    }
    # context = {}
    return HttpResponse(template.render(context, request))


@cache_control(no_store=True)
@login_required
def profile(request):
    template = loader.get_template('profile.html')
    user = request.user
    context = {'user': user}
    return HttpResponse(template.render(context, request))


@cache_control(no_store=True)
@login_required
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        project = Project(
            user=request.user,
            title=request.POST['title'],
            description=request.POST['description'],
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
        )

        if form.is_valid():
            project.save()
            # return HttpResponseRedirect(reverse('index', args=(project.id,)))
            # messages.info(request, "Report saved successfully")
            return HttpResponseRedirect('/profile/')

    else:
        form = ProjectForm()
    return render(request, 'add_report.html', {'form': form})
    # template = loader.get_template('report/add.html')
    # user = request.user
    # context = {'user': user}
    # return HttpResponse(template.render(context, request))


def activity_json_form(request):
    """Create form elements and return JsonResponse to template"""
    data = None
    json_fields = {}
    if request.GET.get('activity', ''):
        activity_id = int(request.GET.get('activity', ''))
        json_fields = Activity.objects.get(id=activity_id).fields
    if request.GET.get('activity_plan_id', False):
        activity_plan_id = int(request.GET.get('activity_plan_id', ''))
        data = ActivityPlan.objects.get(id=activity_plan_id).activity_fields
    form_class = get_dynamic_form(json_fields, data)
    form = form_class()
    temp = loader.render_to_string("activities/dynamic_form_fields.html", {'form': form})
    return JsonResponse({"form": temp})


def activity_plans(request):
    """Activity Plans"""
    activity_plans = ActivityPlan.objects.all()
    return render(request, 'activities/activity_plans.html', {'activity_plans': activity_plans})


def create_activity_plan(request):
    """Create Activity Plans"""
    if request.method == 'POST':
        form = ActivityPlanForm(request.POST)
        if form.is_valid():
            json_data = {}
            activity = Activity.objects.get(id=request.POST.get('activity'))
            json_class = get_dynamic_form(activity.fields)
            json_form = json_class(request.POST)
            if json_form.is_valid():
                json_data = json_form.cleaned_data
            activity_plan = form.save(commit=False)
            activity_plan.activity_fields = json_data
            form.save()
    else:
        form = ActivityPlanForm()
    return render(request, 'activities/activity_plans_form.html', {'form': form})


def update_activity_plan(request, pk):
    """Update Activity"""
    activity_plan = ActivityPlan.objects.get(id=pk)
    form = ActivityPlanForm(instance=activity_plan)
    json_class = get_dynamic_form(activity_plan.activity.fields, data=activity_plan.activity_fields)
    json_form = json_class()
    if request.method == 'POST':
        form = ActivityPlanForm(request.POST, instance=activity_plan)
        if form.is_valid():
            json_data = {}
            activity = Activity.objects.get(id=request.POST.get('activity'))
            json_class = get_dynamic_form(activity.fields)
            json_form = json_class(request.POST)
            if json_form.is_valid():
                json_data = json_form.cleaned_data
            activity_plan = form.save(commit=False)
            activity_plan.activity_fields = json_data
            form.save()
            return redirect('/activity_plans')
    context = {'form': form, 'activity_plan': activity_plan.id}
    return render(request, 'activities/activity_plans_form.html', context)

