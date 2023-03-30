import re
import pandas as pd
import datetime
import sqlite3
import json


from django.shortcuts import render, redirect, get_object_or_404, reverse

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
    context = {}
    return HttpResponse(template.render(context, request))


@cache_control(no_store=True)
@login_required
def home(request):
    template = loader.get_template('home.html')
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
    activities = Activity.objects.filter(clusters__in=cluster_ids).order_by('name')
    activities_options = """"""
    for activity in activities:
        option = f"""
        <option value="{activity.pk}">{activity}</option>
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
    active_projects = Project.objects.filter(active=True)
    completed_projects = Project.objects.filter(active=False)
    context = {
        'active_projects': active_projects,
        'completed_projects': completed_projects
    }
    return render(request, 'projects/projects.html', context)

@cache_control(no_store=True)
@login_required
def completed_project_view(request, pk):
    """Projects Plans"""
    project = Project.objects.filter(id=pk)
    context = {
        'project': project,
    }
    return render(request, 'projects/completed_project.html', context)


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
    context = {'form': form, 'project': project}
    return render(request, 'projects/project_form.html', context)


@cache_control(no_store=True)
@login_required
def create_project_activity_plan(request, project):
    project = Project.objects.get(id=project)
    activities = project.activities.all()
    ActivityPlanFormSet = modelformset_factory(ActivityPlan, exclude=['project'], form=ActivityPlanForm, extra=len(activities))
    if request.method == 'POST':
        formset = ActivityPlanFormSet(request.POST)
        if formset.is_valid():
            activity_plans = {'plans': []}
            for form in formset:
                form_data = form.cleaned_data

                activity = Activity.objects.get(id=form_data['activity_id'])
                activity_plan = form.save(commit=False)
                activity_plan.activity = activity
                activity_plan.project = project
                activity_plan.save()

                activity_plans['plans'].append(activity_plan.id)
            return redirect('create_project_target_location', project=project.id, **activity_plans)
    else:
        initials = []
        for activity in activities:
            initials.append({'project': project, 'activity': activity, 'activity_id': activity.id})
        formset = ActivityPlanFormSet(queryset=ActivityPlan.objects.none(), initial=initials)
    context = {'project': project, 'formset': formset}
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
                # form_data = form.cleaned_data
                # json_data = {}
                # if form_data.get('id', False):
                    # activity = ActivityPlan.objects.get(id=form_data.get('id', False).id).activity
                # if form_data.get('activity_id', False):
                    # activity = Activity.objects.get(id=form_data.get('activity_id', False))

                # json_class = get_dynamic_form(activity.fields)
                # json_form = json_class(request.POST)
                # if json_form.is_valid():
                    # json_data = json_form.cleaned_data
                activity_plan = form.save(commit=False)
                # activity_plan.activity = activity
                activity_plan.project = project
                # activity_plan.activity_fields = json_data
                activity_plan.save()
            return redirect('create_project_target_location', project=project)
        else:
            for form in formset:
                for error in form.errors:
                    error_message = f"Something went wrong {form.errors}"
                    if form.errors[error]:
                        error_message = f"{error}: {form.errors[error][0]}"
                    messages.error(request, error_message)

    context = {'formset': formset}

    return render(request, "projects/project_activity_plan_form.html", context)


@cache_control(no_store=True)
@login_required
def create_project_target_location(request, project, **kwargs):

    activity_plan_ids = [int(s) for s in re.findall(r'\d+', kwargs['plans'])]
    project = Project.objects.get(id=project)

    locations = project.locations.all()
    TargetLocationsFormSet = modelformset_factory(TargetLocation, exclude=['project'], form=TargetLocationForm, extra=len(locations))

    if request.method == 'POST':
        formset = TargetLocationsFormSet(request.POST)
        if formset.is_valid():
            kwarg_vals = {'plans': activity_plan_ids, 'locations': [],}
            for form in formset:
                form_data = form.cleaned_data

                country_id = None
                province_id = None
                district_id = None

                if form_data['country_id'] != 'False':
                    country_id = Location.objects.get(id=form_data['country_id'])
                if form_data['province_id'] != 'False':
                    province_id = Location.objects.get(id=form_data['province_id'])
                if form_data['district_id'] != 'False': 
                    district_id = Location.objects.get(id=form_data['district_id'])

                target_location = form.save(commit=False)

                target_location.country = country_id
                target_location.province = province_id
                target_location.district = district_id

                target_location.project = project
                target_location.save()

                kwarg_vals['locations'].append(target_location.id)

            # kwarg_vals = {'target_locations':str(locations)}
            return redirect('project_plan_review', project=project.id, **kwarg_vals)
            # return redirect('projects')
    else:
        initials = []
        for location in locations:
            country_id = False
            province_id = False
            district_id = False
            initials_dict = {'project': project}

            if location.type == 'Country':
                country_id = location.id
                initials_dict.update({'country': location})
            elif location.type == 'Province':
                province_id = location.id
                initials_dict.update({'project': project.id, 'province': location, 'country': location.parent})
                if location.parent:
                    country_id = location.parent.id
            else:
                district_id = location.id
                initials_dict.update({'district': location, 'province': location.parent, 'country': location.parent.parent})
                if location.parent:
                    province_id = location.parent.id
                if location.parent and location.parent.parent:
                    country_id = location.parent.parent.id

            initials_dict.update({'country_id': country_id, 'province_id': province_id, 'district_id': district_id, 'location':location})

            initials.append(initials_dict)
        formset = TargetLocationsFormSet(queryset=TargetLocation.objects.none(), initial=initials)
    context = {'project': project, 'formset': formset}
    return render(request, "projects/project_target_locations.html", context)


def project_planning_review(request, **kwargs):

    """Projects Plans"""

    project_id = int(kwargs['project'])
    project = Project.objects.get(id=project_id)

    activity_plan_ids = [int(p) for p in re.findall(r'\d+', kwargs['plans'])]
    activity_plans  = ActivityPlan.objects.filter(id__in=activity_plan_ids)

    target_locations_ids = [int(p) for p in re.findall(r'\d+', kwargs['locations'])]
    target_locations = TargetLocation.objects.filter(id__in=target_locations_ids)

    context = {
        'project': project,
        'activity_plans': activity_plans,
        'target_locations': target_locations,
    }
    return render(request, 'projects/project_review.html', context)



# def update_project_target_location(request, project):
