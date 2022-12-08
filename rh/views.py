import pandas as pd
import datetime
import sqlite3
import json


from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.conf import settings
from django.forms import modelformset_factory

from .models import *
from .forms import *


#############################################
############### Index Views #################
#############################################
@cache_control(no_store=True)
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


#############################################
############# Activities Views ##############
#############################################
@cache_control(no_store=True)
@login_required
def load_activity_json_form(request):
    """Create form elements and return JsonResponse to template"""
    data = None
    json_fields = {}
    if request.GET.get('activity', '') or request.GET.get('activity_plan_id'):
        if request.GET.get('activity'):
            activity_id = int(request.GET.get('activity', ''))
            json_fields = Activity.objects.get(id=activity_id).fields
        else:
            activity_plan = int(request.GET.get('activity_plan_id', ''))
            json_fields = ActivityPlan.objects.get(id=activity_plan).activity.fields
        
    if request.GET.get('activity_plan_id') != '':
        activity_plan_id = int(request.GET.get('activity_plan_id', ''))
        data = ActivityPlan.objects.get(id=activity_plan_id).activity_fields
    form_class = get_dynamic_form(json_fields, data)
    if not form_class:
        return JsonResponse({"form": False})
        
    form = form_class()
    temp = loader.render_to_string("dynamic_form_fields.html", {'form': form})
    return JsonResponse({"form": temp})


@cache_control(no_store=True)
@login_required
def activity_plans(request):
    """Activity Plans"""
    activity_plans = ActivityPlan.objects.all()
    return render(request, 'activities/activity_plans.html', {'activity_plans': activity_plans})


@cache_control(no_store=True)
@login_required
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
            return redirect('/activity_plans')
    else:
        form = ActivityPlanForm()
    return render(request, 'activities/activity_plans_form.html', {'form': form})


@cache_control(no_store=True)
@login_required
def update_activity_plan(request, pk):
    """Update Activity"""
    activity_plan = ActivityPlan.objects.get(id=pk)
    form = ActivityPlanForm(instance=activity_plan)
    json_class = get_dynamic_form(activity_plan.activity.fields, initial_data=activity_plan.activity_fields)
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



#############################################
############## Project Views ################
#############################################
@cache_control(no_store=True)
@login_required
def load_activities_details(request):
    """Load activities related to a cluster"""
    cluster_ids = dict(request.GET.lists()).get('clusters[]', [])
    listed_activity_ids = dict(request.GET.lists()).get('listed_activities[]', [])
    cluster_ids = list(map(int, cluster_ids))
    listed_activity_ids = list(map(int, listed_activity_ids))
    activities = Activity.objects.filter(clusters__in=cluster_ids).order_by('title').distinct()
    activities_options = """"""
    for activity in activities:
        option = f"""
        <option value="{activity.pk}">{activity.title}</option>
        """
        activities_options+=option
    return HttpResponse(activities_options)


@cache_control(no_store=True)
@login_required
def load_locations_details(request):
    """Load Locations with group info"""
    countries = Location.objects.filter(type='Country')
    provinces = Location.objects.filter(type='Province').order_by('name')
    country_group = """"""
    province_group = """"""
    for country in countries:
        for province in provinces:
            district_options = """"""
            districts = Location.objects.filter(parent=province)
            for district in districts:
                district_options += f"""
                <option value="{district.pk}">
                    {district.name}
                </option>"""
            
            province_group += f"""
            <optgroup label="{province.name}">
                <option value="{province.pk}">{province.name} ({province.type})</option>
                {district_options}
            </optgroup>"""

        country_group += f"""
        <optgroup label="{country.name}">
            <option value="{country.pk}">{country.name}</option>
        </optgroup>
        {province_group}
        """
    return HttpResponse(country_group)


@cache_control(no_store=True)
@login_required
def projects_view(request):
    """Projects Plans"""
    projects = Project.objects.all()
    return render(request, 'projects/projects.html', {'projects': projects})


@cache_control(no_store=True)
@login_required
def create_project_view(request):
    """Create Project"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project_id = form.save()
            return redirect('create_project_activity_plan', project=project_id.pk)
    else:
        form = ProjectForm(initial={'user': request.user})
    context = {'form': form}
    return render(request, 'projects/project_form.html', context)


@cache_control(no_store=True)
@login_required
def update_project_view(request, pk):
    """Update Project view"""
    project = Project.objects.get(id=pk)
    form = ProjectForm(instance=project)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project_id = form.save()
            return redirect('update_project_activity_plan', project=project_id.pk)
    context = {'form': form}
    return render(request, 'projects/project_form.html', context)


@cache_control(no_store=True)
@login_required
def create_project_activity_plan(request, project):
    project = Project.objects.get(id=project)
    activities = project.activities.all()
    ActivityPlanFormSet = modelformset_factory(ActivityPlan, exclude=['project', 'activity'], form=ActivityPlanForm, extra=len(activities))
    if request.method == 'POST':
        formset = ActivityPlanFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                form_data = form.cleaned_data
                json_data = {}
                activity = Activity.objects.get(id=form_data['activity_id'])
                json_class = get_dynamic_form(activity.fields)
                if json_class:
                    json_form = json_class(request.POST)
                    if json_form.is_valid():
                        json_data = json_form.cleaned_data

                activity_plan = form.save(commit=False)
                activity_plan.activity = activity
                activity_plan.project = project
                activity_plan.activity_fields = json_data
                activity_plan.save()
            return redirect('projects')
    else:
        initials = []
        for activity in activities:
            initials.append({'project': project, 'activity': activity, 'activity_id': activity.id})
        formset = ActivityPlanFormSet(queryset=ActivityPlan.objects.none(), initial=initials)
    context = {'formset': formset}
    return render(request, "projects/project_activity_plan_form.html", context)


@cache_control(no_store=True)
@login_required
def update_project_activity_plan(request, project):
    project = Project.objects.get(id=project)
    activity_plans = ActivityPlan.objects.filter(project__id=project.pk, activity__in=[a.pk for a in project.activities.all()])
    if not activity_plans:
        return redirect('create_project_activity_plan', project=project.pk)
    activities = project.activities.all()
    extras = len(project.activities.all()) - len(activity_plans)
    ActivityPlanFormSet = modelformset_factory(ActivityPlan, exclude=['project', 'activity'], form=ActivityPlanForm, extra=extras)
    initials = []
    for activity in activities:
        if activity.pk not in [a.activity.pk for a in activity_plans]:
            initials.append({'project': project, 'activity': activity, 'activity_id': activity.id})

    formset = ActivityPlanFormSet(request.POST or None, initial=initials, queryset=activity_plans)
    if request.method == "POST":
        if formset.is_valid():
            for form in formset:
                form_data = form.cleaned_data
                json_data = {}
                if form_data.get('id', False):
                    activity = ActivityPlan.objects.get(id=form_data.get('id', False).id).activity
                if form_data.get('activity_id', False):
                    activity = Activity.objects.get(id=form_data.get('activity_id', False))

                json_class = get_dynamic_form(activity.fields)
                json_form = json_class(request.POST)
                if json_form.is_valid():
                    json_data = json_form.cleaned_data
                activity_plan = form.save(commit=False)
                activity_plan.activity = activity
                activity_plan.project = project
                activity_plan.activity_fields = json_data
                activity_plan.save()
            return redirect('projects')
        else:
            for form in formset:
                for error in form.errors:
                    error_message = f"Something went wrong {form.errors}"
                    if form.errors[error]:
                        error_message = f"{error}: {form.errors[error][0]}"
                    messages.error(request, error_message)

    context = {'formset': formset}

    return render(request, "projects/project_activity_plan_form.html", context)
