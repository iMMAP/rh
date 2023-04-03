import re
import pandas as pd
import datetime
import sqlite3
import json


from django.shortcuts import render, redirect, get_object_or_404

# TODO: Add is_safe_url to redirects
# from django.utils.http import is_safe_url


from django.http import HttpResponse, JsonResponse
from django.template import loader


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.conf import settings
from django.forms import modelformset_factory
from django.core.paginator import Paginator

from .models import *
from .forms import *
from .filters import *


#############################################
############### Index Views #################
#############################################
@cache_control(no_store=True)
def index(request):
    template = loader.get_template('index.html')

    users_count = User.objects.all().count()
    locations_count = Location.objects.all().count()
    reports_count = Report.objects.all().count()
    context = {
        'users': users_count, 
        'locations': locations_count, 
        'reports': reports_count
    }
    return HttpResponse(template.render(context, request))


@cache_control(no_store=True)
@login_required
def home(request):
    template = loader.get_template('home.html')

    users_count = User.objects.all().count()
    locations_count = Location.objects.all().count()
    reports_count = Report.objects.all().count()
    context = {
        'users': users_count, 
        'locations': locations_count, 
        'reports': reports_count
    }
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
            json_fields = Activity.objects.get(pk=activity_id).fields
        else:
            activity_plan = int(request.GET.get('activity_plan_id', ''))
            json_fields = ActivityPlan.objects.get(pk=activity_plan).activity.fields
        
    if request.GET.get('activity_plan_id') != '':
        activity_plan_id = int(request.GET.get('activity_plan_id', ''))
        data = ActivityPlan.objects.get(pk=activity_plan_id).activity_fields
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
            activity = Activity.objects.get(pk=request.POST.get('activity'))
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
    activity_plan = ActivityPlan.objects.get(pk=pk)
    form = ActivityPlanForm(instance=activity_plan)
    json_class = get_dynamic_form(activity_plan.activity.fields, initial_data=activity_plan.activity_fields)
    json_form = json_class()
    if request.method == 'POST':
        form = ActivityPlanForm(request.POST, instance=activity_plan)
        if form.is_valid():
            json_data = {}
            activity = Activity.objects.get(pk=request.POST.get('activity'))
            json_class = get_dynamic_form(activity.fields)
            json_form = json_class(request.POST)
            if json_form.is_valid():
                json_data = json_form.cleaned_data
            activity_plan = form.save(commit=False)
            activity_plan.activity_fields = json_data
            form.save()
            return redirect('/activity_plans')
    context = {'form': form, 'activity_plan': activity_plan.pk}
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
    draft_projects = Project.objects.filter(state='draft')
    active_projects = Project.objects.filter(state='in-progress')
    completed_projects = Project.objects.filter(state='done')

    # Setup Pagination
    p = Paginator(active_projects, 8)
    page = request.GET.get('page')
    p_active_projects = p.get_page(page)
    total_pages = 'a'*p_active_projects.paginator.num_pages


    # Setup Filter
    project_filter = ProjectsFilter(request.GET, queryset=active_projects)
    active_projects = project_filter.qs

    context = {
        'draft_projects': draft_projects,
        'active_projects': p_active_projects,
        'completed_projects': completed_projects,
        'project_filter':project_filter,
        'total_pages':total_pages,
    }
    return render(request, 'projects/projects.html', context)


@cache_control(no_store=True)
@login_required
def completed_project_view(request, pk):
    """Projects Plans"""
    project = Project.objects.get(pk=pk)

    activity_plans  = ActivityPlan.objects.filter(project__id=project.pk)
    target_locations = TargetLocation.objects.filter(project__id=project.pk)

    context = {
        'project': project,
        'activity_plans': activity_plans,
        'target_locations': target_locations,
        'project_review': True,
        'activity_plans': activity_plans,
        'locations': target_locations
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
    context = {'form': form, 'project_planning': True}
    return render(request, 'projects/project_form.html', context)


@cache_control(no_store=True)
@login_required
def update_project_view(request, pk):
    """Update Project view"""
    project = Project.objects.get(pk=pk)
    form = ProjectForm(instance=project)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project_id = form.save()
            return redirect('update_project_activity_plan', project=project_id.pk)
        
    activity_plans = ActivityPlan.objects.filter(project__id=project.pk)
    plans = list(activity_plans.values_list('pk', flat=True))
    target_locations = TargetLocation.objects.filter(project__id=project.pk)
    locations = list(target_locations.values_list('pk', flat=True))


    context = {'form': form, 'project': project, 'project_planning': True, 'plans':plans, 'locations': locations}
    return render(request, 'projects/project_form.html', context)


@cache_control(no_store=True)
@login_required
def create_project_activity_plan(request, project):
    project = Project.objects.get(pk=project)
    activities = project.activities.all()
    activity_plans = ActivityPlan.objects.filter(project__id=project.pk, activity__in=[a.pk for a in project.activities.all()])
    if activity_plans:
        return redirect('update_project_activity_plan', project=project.pk)
    ActivityPlanFormSet = modelformset_factory(ActivityPlan, exclude=['project'], form=ActivityPlanForm, extra=len(activities))
    if request.method == 'POST':
        formset = ActivityPlanFormSet(request.POST)
        if formset.is_valid():
            activity_plans = {'plans': []}
            for form in formset:
                form_data = form.cleaned_data

                activity = Activity.objects.get(pk=form_data['activity_id'])
                activity_plan = form.save(commit=False)
                activity_plan.activity = activity
                activity_plan.project = project
                activity_plan.save()

                activity_plans['plans'].append(activity_plan.pk)
            return redirect('create_project_target_location', project=project.pk, **activity_plans)
    else:
        initials = []
        for activity in activities:
            initials.append({'project': project, 'activity': activity, 'activity_id': activity.pk})
        formset = ActivityPlanFormSet(queryset=ActivityPlan.objects.none(), initial=initials)
    context = {'project': project, 'formset': formset, 'activity_planning': True, 'plans': False}
    return render(request, "projects/project_activity_plan_form.html", context)


@cache_control(no_store=True)
@login_required
def update_project_activity_plan(request, project):
    project = Project.objects.get(pk=project)
    activity_plans = ActivityPlan.objects.filter(project__id=project.pk, activity__in=[a.pk for a in project.activities.all()])
    if not activity_plans:
        return redirect('create_project_activity_plan', project=project.pk)
    activities = project.activities.all()
    extras = len(project.activities.all()) - len(activity_plans)
    ActivityPlanFormSet = modelformset_factory(ActivityPlan, exclude=['project'], form=ActivityPlanForm, extra=extras)
    initials = []
    for activity in activities:
        # if activity.pk not in [a.activity.pk for a in activity_plans]:
        initials.append({'project': project, 'activity': activity, 'activity_id': activity.pk})

    kwarg_vals = {'plans': list(activity_plans.values_list('pk', flat=True))}
    formset = ActivityPlanFormSet(request.POST or None, initial=initials, queryset=activity_plans)
    if request.method == "POST":
        if formset.is_valid():
            for form in formset:
                form_data = form.cleaned_data

                if form_data.get('id', False):
                    activity = ActivityPlan.objects.get(pk=form_data.get('id', False).pk).activity
                if form_data.get('activity_id', False):
                    activity = Activity.objects.get(pk=form_data.get('activity_id', False))

                # json_data = {}
                # json_class = get_dynamic_form(activity.fields)
                # json_form = json_class(request.POST)
                # if json_form.is_valid():
                    # json_data = json_form.cleaned_data
                # activity_plan.activity_fields = json_data

                activity_plan = form.save(commit=False)
                activity_plan.activity = activity
                activity_plan.project = project
                activity_plan.save()
                kwarg_vals['plans'].append(activity_plan.pk)

            return redirect('update_project_target_location', project=project.pk, **kwarg_vals)
        else:
            for form in formset:
                for error in form.errors:
                    error_message = f"Something went wrong {form.errors}"
                    if form.errors[error]:
                        error_message = f"{error}: {form.errors[error][0]}"
                    messages.error(request, error_message)


    target_locations = TargetLocation.objects.filter(project__id=project.pk)
    locations = list(target_locations.values_list('pk', flat=True))
    context = {'project': project, 'formset': formset, 'activity_planning': True, 'plans': kwarg_vals['plans'], 'locations':locations}

    return render(request, "projects/project_activity_plan_form.html", context)


@cache_control(no_store=True)
@login_required
def create_project_target_location(request, project, **kwargs):

    activity_plan_ids = [int(s) for s in re.findall(r'\d+', kwargs['plans'])]
    project = Project.objects.get(pk=project)

    locations = project.locations.all()
    TargetLocationsFormSet = modelformset_factory(TargetLocation, exclude=['project'], form=TargetLocationForm, extra=len(locations))

    target_locations = TargetLocation.objects.filter(project__id=project.pk)
    if target_locations:
        kwargs['lcoation', list(activity_plans.values_list('pk', flat=True))]
        return redirect('update_project_target_location', project=project.pk, **kwargs)

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
                    country_id = Location.objects.get(pk=form_data['country_id'])
                if form_data['province_id'] != 'False':
                    province_id = Location.objects.get(pk=form_data['province_id'])
                if form_data['district_id'] != 'False': 
                    district_id = Location.objects.get(pk=form_data['district_id'])

                target_location = form.save(commit=False)

                target_location.country = country_id
                target_location.province = province_id
                target_location.district = district_id

                target_location.project = project
                target_location.save()

                kwarg_vals['locations'].append(target_location.pk)

            # kwarg_vals = {'target_locations':str(locations)}
            return redirect('project_plan_review', project=project.pk, **kwarg_vals)
            # return redirect('projects')
    else:
        initials = []
        for location in locations:
            country_id = False
            province_id = False
            district_id = False
            initials_dict = {'project': project}

            if location.type == 'Country':
                country_id = location.pk
                initials_dict.update({'country': location})
            elif location.type == 'Province':
                province_id = location.pk
                initials_dict.update({'project': project.pk, 'province': location, 'country': location.parent})
                if location.parent:
                    country_id = location.parent.pk
            else:
                district_id = location.pk
                initials_dict.update({'district': location, 'province': location.parent, 'country': location.parent.parent})
                if location.parent:
                    province_id = location.parent.pk
                if location.parent and location.parent.parent:
                    country_id = location.parent.parent.pk

            initials_dict.update({'country_id': country_id, 'province_id': province_id, 'district_id': district_id, 'location':location})

            initials.append(initials_dict)
        formset = TargetLocationsFormSet(queryset=TargetLocation.objects.none(), initial=initials)
    context = {'project': project, 'formset': formset, 'locations_planning': True, 'plans': False, 'locations': False}
    return render(request, "projects/project_target_locations.html", context)


@cache_control(no_store=True)
@login_required
def update_project_target_location(request, project, **kwargs):
    activity_plan_ids = [int(s) for s in re.findall(r'\d+', kwargs['plans'])]
    project = Project.objects.get(pk=project)
    
    target_locations = TargetLocation.objects.filter(project__id=project.pk)
    if not target_locations:
        return redirect('create_project_target_location', project=project.pk, **kwargs)
    
    locations = project.locations.all()
    extras = len(project.locations.all()) - len(target_locations)
    TargetLocationsFormSet = modelformset_factory(TargetLocation, exclude=['project'], form=TargetLocationForm, extra=extras)
    
    initials = []
    for location in locations:
        country_id = False
        province_id = False
        district_id = False
        initials_dict = {'project': project}

        if location.type == 'Country':
            country_id = location.pk
            initials_dict.update({'country': location})
        elif location.type == 'Province':
            province_id = location.pk
            initials_dict.update({'project': project.pk, 'province': location, 'country': location.parent})
            if location.parent:
                country_id = location.parent.pk
        else:
            district_id = location.pk
            initials_dict.update({'district': location, 'province': location.parent, 'country': location.parent.parent})
            if location.parent:
                province_id = location.parent.pk
            if location.parent and location.parent.parent:
                country_id = location.parent.parent.pk

        initials_dict.update({'country_id': country_id, 'province_id': province_id, 'district_id': district_id})

        initials.append(initials_dict)
    
    formset = TargetLocationsFormSet(request.POST or None, initial=initials, queryset=target_locations)
    
    kwarg_vals = {'plans': activity_plan_ids, 'locations': list(target_locations.values_list('pk', flat=True)),}
    if request.method == 'POST':
        formset = TargetLocationsFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                form_data = form.cleaned_data

                country_id = None
                province_id = None
                district_id = None

                if form_data.get('country_id', False) and form_data.get('country_id', False) != 'False':
                    country_id = Location.objects.get(pk=form_data['country_id'])
                if form_data.get('province_id', False) and form_data.get('province_id', False) != 'False':
                    province_id = Location.objects.get(pk=form_data['province_id'])
                if form_data.get('district_id', False) and form_data.get('district_id', False) != 'False': 
                    district_id = Location.objects.get(pk=form_data['district_id'])
                
                if form_data.get('id', False):
                    country_id = form_data['id'].country
                    province_id = form_data['id'].province
                    district_id = form_data['id'].district

                target_location = form.save(commit=False)

                target_location.country = country_id
                target_location.province = province_id
                target_location.district = district_id

                target_location.project = project
                target_location.save()
                kwarg_vals['locations'].append(target_location.pk)

                # kwarg_vals['locations'].append(target_location.pk)

            # kwarg_vals = {'target_locations':str(locations)}
            return redirect('project_plan_review', project=project.pk, **kwarg_vals)
            # return redirect('projects')

    context = {'project': project, 'formset': formset, 'locations_planning': True, 'plans': kwarg_vals['plans'], 'locations': kwarg_vals['locations']}
    return render(request, "projects/project_target_locations.html", context)


@cache_control(no_store=True)
@login_required
def project_planning_review(request, **kwargs):
    """Projects Plans"""

    project_id = int(kwargs['project'])
    project = Project.objects.get(pk=project_id)

    activity_plan_ids = [int(p) for p in re.findall(r'\d+', kwargs['plans'])]
    activity_plans  = ActivityPlan.objects.filter(pk__in=activity_plan_ids)

    target_locations_ids = [int(p) for p in re.findall(r'\d+', kwargs['locations'])]
    target_locations = TargetLocation.objects.filter(pk__in=target_locations_ids)

    plans = list(activity_plans.values_list('pk', flat=True))
    locations = list(target_locations.values_list('pk', flat=True))

    context = {
        'project': project,
        'activity_plans': activity_plans,
        'target_locations': target_locations,
        'project_review': True,
        'plans': plans,
        'locations': locations
    }
    return render(request, 'projects/project_review.html', context)


@cache_control(no_store=True)
@login_required
def submit_project(request, pk):
    project_id = Project.objects.get(pk=pk)
    if project_id:
        project_id.state = 'in-progress'
        project_id.save()
    return redirect('projects')


@cache_control(no_store=True)
@login_required
def delete_project(request, pk):
    project = Project.objects.get(pk=pk)
    if project:
        activity_plans = ActivityPlan.objects.filter(project__id=project.pk)
        target_locations = TargetLocation.objects.filter(project__id=project.pk)

        for plan in activity_plans:
            plan.state = 'archive'
            plan.active = False
            plan.save()
        
        for location in target_locations:
            location.state = 'archive'
            location.active = False
            location.save()

        project.state = 'archive'
        project.active = False
        project.save()

    return redirect('projects')

@cache_control(no_store=True)
@login_required
def copy_project(request, pk):
    pass
    project = Project.objects.get(pk=pk)
    if project:
        new_project = project
        new_project.pk = None
        new_project.save()
        new_project.clusters.set(project.clusters.all())
        new_project.locations.set(project.locations.all())
        new_project.activities.set(project.activities.all())
        new_project.donors.set(project.donors.all())
        new_project.title = 'COPY'
        if new_project:
            activity_plans = ActivityPlan.objects.filter(project__id=project.pk)
            target_locations = TargetLocation.objects.filter(project__id=project.pk)

            for plan in activity_plans:
                new_plan = plan
                new_plan.pk = None
                new_plan.save()
                new_plan.project = new_project
                new_plan.active = True
                new_plan.state = 'in-progress'
                new_plan.description = 'COPY'
                # new_plan.save()
            
            for location in target_locations:
                new_location = location
                new_plan.pk = None
                new_location.save()
                new_location.project = new_project
                new_location.active = True
                new_location.state = 'in-progress'
                new_location.site_name = 'COPY'
                # new_location.save()

        # new_project_id.save()

    return redirect('projects')
    