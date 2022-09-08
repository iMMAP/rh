from functools import cache
import pandas as pd
import datetime
import sqlite3
from multiprocessing import context
from tkinter import E

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control


from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.conf import settings

from .models import Project
from .forms import ProjectForm, RegisterForm
from .decorators import unauthenticated_user

@cache_control(no_store=True)
@unauthenticated_user
def register_view(request):
    """Registration view for creating new signing up"""
    template = loader.get_template('registration/signup.html')
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            name = form.cleaned_data.get('name')
            user = form.save()
            #TODO: When user is created populate the name field with username for now.
            if not name:
                user.name = username
                user.save()
            messages.success(request, f'Account created successfully for {username}.')
            return redirect('login')
    context = {'form': form}
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
            return redirect('index')
        else:
            messages.info(request, f'Enter correct username and password.')
    context = {}
    return HttpResponse(template.render(context, request))


def logout_view(request):
    """User Logout View"""
    messages.info(request, f'{request.user} logged out.')
    logout(request)
    return redirect("/login")

@cache_control(no_store=True)
@login_required
def index(request):
    template = loader.get_template('index.html')

#     play_db = settings.PLAY_DB
#     con = sqlite3.connect(play_db)

#     play = con.execute("""
# SELECT 
# DATE('2022-0' || (r.month +1) || '-01') as month,
# SUM(boys) + SUM(girls) + SUM(men) + SUM(women) + SUM(elderly_women) + SUM(elderly_men) AS people_recieved
# FROM benef b 
# INNER JOIN report r on b.report_id=r.id
# INNER JOIN activity a on a.id = b.activity_id
# INNER JOIN project p on p.id=r.project_id
# INNER JOIN org o on o.id=p.org_id
# INNER JOIN locs on locs.id = b.loc_id
# WHERE substr(locs.code, 0, 3) = 'AF' AND 
# o.short <> 'iMMAP' AND 
# r.year = 2022
# GROUP BY r.month
# ORDER BY month
# """)

#     types = []
#     nb_benef = []
#     for x in play:
#         types.append(
#             datetime.date.fromisoformat(x[0]).strftime('%B')
#         )
#         nb_benef.append(x[1])

    
#     months = str(types[0:10])
#     benefs = str(nb_benef[0:10])

#     df = pd.read_sql("""
# SELECT 
# DATE('2022-0' || (r.month +1) || '-01') as month, p.cluster,
# --a.activity_type || ' - ' || a.activity_desc as activity,
# SUM(boys) + SUM(girls) + SUM(men) + SUM(women) + SUM(elderly_women) + SUM(elderly_men) AS people_recieved
# FROM benef b 
# INNER JOIN report r on b.report_id=r.id
# INNER JOIN activity a on a.id = b.activity_id
# INNER JOIN project p on p.id=r.project_id
# INNER JOIN org o on o.id=p.org_id
# INNER JOIN locs on locs.id = b.loc_id
# WHERE substr(locs.code, 0, 3) = 'AF' AND 
# o.short <> 'iMMAP' AND 
# r.year = 2022 AND
# p.cluster IN ('ESNFI', 'FSAC', 'Protection', 'WASH')
# GROUP BY r.month, p.cluster
# ORDER BY month, cluster;
#     """, con=con)
    
#     clusters = df.pivot(index='month', columns='cluster', values='people_recieved').convert_dtypes().fillna(0).to_dict('list')

#     df = pd.read_sql("""
#     SELECT 
# a.activity_type || ' - ' || a.activity_desc as activity, o.short, l2.name,
# printf("%,d", SUM(boys) + SUM(girls) + SUM(men) + SUM(women) + SUM(elderly_women) + SUM(elderly_men)) AS people_recieved
# FROM benef b 
# INNER JOIN report r on b.report_id=r.id
# INNER JOIN activity a on a.id = b.activity_id
# INNER JOIN project p on p.id=r.project_id
# INNER JOIN org o on o.id=p.org_id
# INNER JOIN locs on locs.id = b.loc_id
# INNER JOIN locs l2 on locs.parent_id = l2.id
# WHERE substr(locs.code, 0, 3) = 'AF' AND 
# o.short <> 'iMMAP' AND 
# r.year = 2022 AND
# r.month = 6 AND r.status='complete'
# GROUP BY l2.id, activity_type, activity_desc HAVING people_recieved IS NOT NULL
# ORDER BY month, l2.name, people_recieved desc;
#     """, con=con)

#     activities = df.to_dict('records')
#     # import pdb; pdb.set_trace()
#     context = {
#         'months': months, 
#         'benefs': benefs,
#         'ESNFI': clusters['ESNFI'],
#         'FSAC': clusters['FSAC'],
#         'Protection': clusters['Protection'],
#         'WASH': clusters['WASH'],
#         'activities': activities,
#     }
    context = {}
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
            #return HttpResponseRedirect(reverse('index', args=(project.id,)))
            # messages.info(request, "Report saved successfully")
            return HttpResponseRedirect('/profile/')
            
    else:
        form = ProjectForm()
    return render(request, 'add_report.html', {'form': form})
        # template = loader.get_template('report/add.html')
        # user = request.user
        # context = {'user': user}
        # return HttpResponse(template.render(context, request))
