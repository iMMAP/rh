import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.forms import modelformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.views.decorators.cache import cache_control
from django.db.models import Q

from .filters import *
from .forms import *


# TODO: Add is_safe_url to redirects
# from django.utils.http import is_safe_url


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
############## Project Views ################
#############################################


@cache_control(no_store=True)
@login_required
def load_locations_details(request):
    """
    View function to load Locations with group info.

    This function accepts GET requests with the following parameters:
    - provinces[]: a list of Location primary keys for provinces to filter by
    - listed_districts[]: a list of Location primary keys for districts to include in the response

    If only one province is specified, the function returns a list of district options for that province.
    Otherwise, it returns an HTML string containing optgroup labels for each specified province, with
    option tags for each district belonging to the province.

    The function is decorated with cache_control and login_required to ensure reliable and secure access.
    """
    province_ids = request.GET.getlist('provinces[]')
    province_ids = [int(i) for i in province_ids if i]
    listed_district_ids = request.GET.getlist('listed_districts[]')
    listed_district_ids = [int(i) for i in listed_district_ids if i]

    provinces = Location.objects.filter(pk__in=province_ids).select_related('parent')
    province_group = []
    for province in provinces:
        districts = Location.objects.filter(parent__pk=province.pk).order_by('name')
        districts_options = [f'<option value="{district.pk}">{district}</option>' for district in districts]
        district_group = ''.join(districts_options)
        province_group.append(f'<optgroup label="{province.name}">{district_group}</optgroup>')
    response = ''.join(province_group)

    if len(province_ids) == 1:
        districts = Location.objects.filter(parent__pk=province_ids[0]).order_by('name')
        districts_options = [f'<option value="{district.pk}">{district}</option>' for district in districts]
        response = ''.join(districts_options)

    return HttpResponse(response)


@cache_control(no_store=True)
@login_required
def projects_view(request):
    """Projects Plans"""

    draft_projects = Project.objects.filter(state='draft')
    active_projects = Project.objects.filter(state='in-progress').order_by('-id')
    completed_projects = Project.objects.filter(state='done')

    # Setup Pagination
    p = Paginator(active_projects, 3)
    page = request.GET.get('page')
    p_active_projects = p.get_page(page)
    total_pages = 'a' * p_active_projects.paginator.num_pages

    # Setup Filter
    project_filter = ProjectsFilter(request.GET, queryset=active_projects)
    active_projects = project_filter.qs

    context = {
        'draft_projects': draft_projects,
        'active_projects': p_active_projects,
        'completed_projects': completed_projects,
        'project_filter': project_filter,
        'total_pages': total_pages,
    }
    return render(request, 'projects/projects.html', context)


@cache_control(no_store=True)
@login_required
def completed_project_view(request, pk):
    """Projects Plans"""

    project = Project.objects.get(pk=pk)

    activity_plans = ActivityPlan.objects.filter(project__id=project.pk)
    target_locations = TargetLocation.objects.filter(project__id=project.pk)

    context = {
        'project': project,
        'activity_plans': activity_plans,
        'target_locations': target_locations,
        'project_review': True,
        'locations': target_locations
    }
    return render(request, 'projects/completed_project.html', context)


@cache_control(no_store=True)
@login_required
def create_project_view(request):
    """View for creating a project."""

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            return redirect('create_project_activity_plan', project=project.pk)

        # Form is not valid
        error_message = 'Something went wrong. Please fix the errors below.'
        messages.error(request, error_message)
    else:
        # Use user's country and clusters as default values if available
        if request.user.is_authenticated and request.user.profile and request.user.profile.country:
            country = request.user.profile.country
            clusters = request.user.profile.clusters.all()
            form = ProjectForm(initial={'user': request.user, 'country': country, 'clusters': clusters})
        else:
            form = ProjectForm()

    context = {'form': form, 'project_planning': True}
    return render(request, 'projects/project_form.html', context)


@cache_control(no_store=True)
@login_required
def update_project_view(request, pk):
    """View for updating a project."""

    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            return redirect('create_project_activity_plan', project=project.pk)
    else:
        form = ProjectForm(instance=project)

    activity_plans = ActivityPlan.objects.filter(project=project)
    plans = list(activity_plans.values_list('pk', flat=True))
    target_locations = TargetLocation.objects.filter(project=project)
    locations = list(target_locations.values_list('pk', flat=True))

    context = {
        'form': form,
        'project': project,
        'project_planning': True,
        'plans': plans,
        'locations': locations
    }
    return render(request, 'projects/project_form.html', context)


@cache_control(no_store=True)
@login_required
def create_project_activity_plan(request, project):
    """
    View for creating or updating activity plans for a project.
    """
    project = get_object_or_404(Project, pk=project)
    activity_plans = project.activityplan_set.all()
    ActivityPlanFormSet = modelformset_factory(ActivityPlan, form=ActivityPlanForm, can_delete=True, extra=1)
    formset = ActivityPlanFormSet(request.POST or None, queryset=activity_plans, form_kwargs={'project': project})

    if request.method == 'POST':
        submit_type = request.POST.get('submit_type')
        if formset.is_valid():
            if submit_type == 'next_step':
                for form in formset:
                    if form.cleaned_data.get('activity_domain') and form.cleaned_data.get('activity_type'):
                        activity = form.save(commit=False)
                        activity.project = project
                        activity.active = True
                        activity.save()
                        form.save_m2m()
                return redirect('create_project_target_location', project=project.pk)
            else:
                for form in formset:
                    if form.cleaned_data.get('save'):
                        if form.cleaned_data.get('activity_domain') and form.cleaned_data.get('activity_type'):
                            form.save(commit=False).project = project
                            form.save()
                            form.save_m2m()
                        return redirect('create_project_activity_plan', project=project.pk)
        else:
            for form in formset:
                for error in form.errors:
                    error_message = f"Something went wrong {formset.errors}"
                    if form.errors[error]:
                        error_message = f"{error}: {form.errors[error][0]}"
                    messages.error(request, error_message)

    plans = list(activity_plans.values_list('pk', flat=True))
    context = {'project': project, 'formset': formset, 'activity_planning': True, 'plans': plans}
    return render(request, 'projects/project_activity_plan_form.html', context)


@cache_control(no_store=True)
@login_required
def create_project_target_location(request, project):
    project = get_object_or_404(Project, pk=project)

    activity_plans = project.activityplan_set.all()
    target_locations = project.targetlocation_set.all()

    TargetLocationsFormSet = modelformset_factory(TargetLocation, form=TargetLocationForm, extra=1)
    formset = TargetLocationsFormSet(request.POST or None, queryset=target_locations, form_kwargs={'project': project})

    if request.method == 'POST':
        submit_type = request.POST.get('submit_type')

        if formset.is_valid():
            if submit_type == 'next_step':
                for form in formset:
                    form.save(commit=False).project = project
                    form.save()
                    form.save_m2m()
                return redirect('project_plan_review', project=project.pk)
            else:
                for form in formset:
                    if form.cleaned_data.get('save'):
                        form.save(commit=False).project = project
                        form.save()
                        form.save_m2m()
                        return redirect('create_project_target_location', project=project.pk)
        else:
            for form in formset:
                for error in form.errors:
                    error_message = f"Something went wrong {formset.errors}"
                    if form.errors[error]:
                        error_message = f"{error}: {form.errors[error][0]}"
                    messages.error(request, error_message)

    plans = list(activity_plans.values_list('pk', flat=True))
    locations = list(target_locations.values_list('pk', flat=True))
    context = {'project': project, 'formset': formset, 'locations_planning': True, 'plans': plans, 'locations': locations}
    return render(request, "projects/project_target_locations.html", context)


@cache_control(no_store=True)
@login_required
def project_planning_review(request, **kwargs):
    """Projects Plans"""

    project_id = int(kwargs['project'])
    project = Project.objects.get(pk=project_id)
    activity_plans = ActivityPlan.objects.filter(project__pk=project.pk)
    target_locations = TargetLocation.objects.filter(project__pk=project.pk)
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
        new_project = Project.objects.get(pk=pk)
        new_project.pk = None
        new_project.save()
        new_project.clusters.set(project.clusters.all())
        new_project.locations.set(project.locations.all())
        new_project.activities.set(project.activities.all())
        new_project.donors.set(project.donors.all())
        new_project.programme_partners.set(project.programme_partners.all())
        new_project.implementing_partners.set(project.implementing_partners.all())
        new_project.title = f"{project.title} - COPY"

        if new_project:
            activity_plans = ActivityPlan.objects.filter(project__pk=project.pk)
            target_locations = TargetLocation.objects.filter(project__pk=project.pk)

            for plan in activity_plans:
                new_plan = ActivityPlan.objects.get(pk=plan.pk)
                new_plan.pk = None
                new_plan.save()
                new_plan.project = new_project
                new_plan.active = True
                new_plan.state = 'in-progress'
                new_plan.description = 'COPY'
                new_plan.save()
                # new_plan.save()

            for location in target_locations:
                new_location = TargetLocation.objects.get(pk=location.pk)
                new_location.pk = None
                new_location.save()
                new_location.project = new_project
                new_location.active = True
                new_location.state = 'in-progress'
                new_location.site_name = 'COPY'
                # new_location.save()
                new_location.save()

        new_project.save()

    return redirect('projects')
