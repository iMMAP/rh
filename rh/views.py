RECORDS_PER_PAGE = 3

from django.contrib import messages
from django.urls import reverse
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
def load_facility_sites(request):
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
    cluster_ids = request.GET.getlist('clusters[]')
    cluster_ids = [int(i) for i in cluster_ids if i]
    listed_facilities_ids = request.GET.getlist('listed_facilities[]')
    listed_facilities_ids = [int(i) for i in listed_facilities_ids if i]

    clusters = Cluster.objects.filter(pk__in=cluster_ids)
    cluster_group = []
    for cluster in clusters:
        facilities = FacilitySiteType.objects.filter(cluster__pk=cluster.pk).order_by('name')
        facility_options = [f'<option value="{facility.pk}">{facility}</option>' for facility in facilities]
        facility_group = ''.join(facility_options)
        cluster_group.append(f'<optgroup label="{cluster.name}">{facility_group}</optgroup>')
        response = ''.join(cluster_group)

    if len(cluster_ids) == 1:
        facilities = FacilitySiteType.objects.filter(cluster__pk=cluster_ids[0]).order_by('name')
        facilities_options = [f'<option value="{facility.pk}">{facility}</option>' for facility in facilities]
        response = ''.join(facilities_options)

    return HttpResponse(response)


# TODO: Project View Structure can be improved.
@cache_control(no_store=True)
@login_required
def draft_projects_view(request):
    """Projects"""

    all_projects = Project.objects.all()
    draft_projects = all_projects.filter(state='draft').order_by('-id')
    draft_projects_count = draft_projects.count()
    active_projects = all_projects.filter(state='in-progress')
    completed_projects = all_projects.filter(state='done')
    archived_projects = all_projects.filter(state='archive')

    # Setup Filter
    project_filter = ProjectsFilter(request.GET, queryset=draft_projects)
    draft_projects = project_filter.qs

    # Setup Pagination
    p = Paginator(draft_projects, RECORDS_PER_PAGE)
    page = request.GET.get('page')
    p_draft_projects = p.get_page(page)
    total_pages = 'a' * p_draft_projects.paginator.num_pages

    context = {
        'draft_view': True,
        'draft_projects_count': draft_projects_count,
        'projects': p_draft_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'archived_projects': archived_projects,
        'project_filter': project_filter,
        'total_pages': total_pages,
    }
    return render(request, 'projects/views/draft_projects.html', context)


@cache_control(no_store=True)
@login_required
def active_projects_view(request):
    """Projects"""

    all_projects = Project.objects.all()
    active_projects = all_projects.filter(state='in-progress').order_by('-id')
    active_projects_count = active_projects.count()
    draft_projects = all_projects.filter(state='draft')
    completed_projects = all_projects.filter(state='done')
    archived_projects = all_projects.filter(state='archive')
    
    # Setup Filter
    project_filter = ProjectsFilter(request.GET, queryset=active_projects)
    active_projects = project_filter.qs

    # Setup Pagination
    p = Paginator(active_projects, RECORDS_PER_PAGE)
    page = request.GET.get('page')
    p_active_projects = p.get_page(page)
    total_pages = 'a' * p_active_projects.paginator.num_pages

    context = {
        'active_view': True,
        'active_projects_count': active_projects_count,
        'projects': p_active_projects,
        'draft_projects': draft_projects,
        'completed_projects': completed_projects,
        'archived_projects': archived_projects,
        'project_filter': project_filter,
        'total_pages': total_pages,
    }
    return render(request, 'projects/views/active_projects.html', context)


@cache_control(no_store=True)
@login_required
def completed_projects_view(request):
    """Projects"""

    all_projects = Project.objects.all()
    completed_projects = all_projects.filter(state='done').order_by('-id')
    completed_projects_count = completed_projects.count()
    draft_projects = all_projects.filter(state='draft')
    active_projects = all_projects.filter(state='in-progress')
    archived_projects = all_projects.filter(state='archive')

    # Setup Filter
    project_filter = ProjectsFilter(request.GET, queryset=completed_projects)
    completed_projects = project_filter.qs

    # Setup Pagination
    p = Paginator(completed_projects, RECORDS_PER_PAGE)
    page = request.GET.get('page')
    p_completed_projects = p.get_page(page)
    total_pages = 'a' * p_completed_projects.paginator.num_pages

    context = {
        'completed_view': True,
        'completed_projects_count': completed_projects_count,
        'projects': p_completed_projects,
        'draft_projects': draft_projects,
        'active_projects': active_projects,
        'archived_projects': archived_projects,
        'project_filter': project_filter,
        'total_pages': total_pages,
    }
    return render(request, 'projects/views/completed_projects.html', context)


@cache_control(no_store=True)
@login_required
def archived_projects_view(request):
    """Projects"""

    all_projects = Project.objects.all()
    archived_projects = all_projects.filter(state='archive').order_by('-id')
    archived_projects_count = archived_projects.count()
    completed_projects = all_projects.filter(state='done')
    draft_projects = all_projects.filter(state='draft')
    active_projects = all_projects.filter(state='in-progress')

    # Setup Filter
    project_filter = ProjectsFilter(request.GET, queryset=archived_projects)
    archived_projects = project_filter.qs

    # Setup Pagination
    p = Paginator(archived_projects, RECORDS_PER_PAGE)
    page = request.GET.get('page')
    p_archived_projects = p.get_page(page)
    total_pages = 'a' * p_archived_projects.paginator.num_pages

    context = {
        'archived_view': True,
        'archived_projects_count': archived_projects_count,
        'projects': p_archived_projects,
        'draft_projects': draft_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'project_filter': project_filter,
        'total_pages': total_pages,
    }
    return render(request, 'projects/views/archived_projects.html', context)


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
    return render(request, 'projects/views/completed_project.html', context)


@cache_control(no_store=True)
@login_required
def open_project_view(request, pk):
    """View for creating a project."""

    project = get_object_or_404(Project, pk=pk)
    activity_plans = project.activityplan_set.all()
    target_locations = project.targetlocation_set.all()
    plans = list(activity_plans.values_list('pk', flat=True))
    locations = list(target_locations.values_list('pk', flat=True))
    project_state = project.state
    parent_page = {
        'in-progress': 'active_projects',
        'draft': 'draft_projects',
        'done': 'completed_projects',
        'archive': 'archived_projects'
    }.get(project_state, None)

    context = {
        'project': project,
        'activity_plans': activity_plans,
        'target_locations': target_locations,
        'plans': plans,
        'locations': locations,
        'parent_page': parent_page
    }
    return render(request, 'projects/views/project_view.html', context)


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

    context = {
        'form': form, 
        'project_planning': True, 
    }
    return render(request, 'projects/forms/project_form.html', context)


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

    activity_plans = project.activityplan_set.all()
    plans = list(activity_plans.values_list('pk', flat=True))
    target_locations = project.targetlocation_set.all()
    locations = list(target_locations.values_list('pk', flat=True))
    project_state = project.state
    parent_page = {
        'in-progress': 'active_projects',
        'draft': 'draft_projects',
        'done': 'completed_projects'
    }.get(project_state, None)

    context = {
        'form': form,
        'project': project,
        'project_planning': True,
        'plans': plans,
        'locations': locations,
        'parent_page': parent_page
    }
    return render(request, 'projects/forms/project_form.html', context)


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
            for form in formset:
                if form.cleaned_data.get('save') or submit_type == 'next_step':
                    if form.cleaned_data.get('activity_domain') and form.cleaned_data.get('activity_type'):
                        activity = form.save(commit=False)
                        activity.project = project
                        activity.title = f"{activity.activity_domain.name}, {activity.activity_type.name},  {activity.activity_detail.name if activity.activity_detail else ''}"
                        activity.active = True
                        activity.total_0_5 = activity.female_0_5 + activity.male_0_5 + activity.other_0_5
                        activity.total_6_12 = activity.female_6_12 + activity.male_6_12 + activity.other_6_12
                        activity.total_12_17 = activity.female_12_17 + activity.male_12_17 + activity.other_12_17
                        activity.total_18 = activity.female_18 + activity.male_18 + activity.other_18
                        activity.total = activity.female_total + activity.male_total + activity.other_total
                        activity.save()
                        form.save_m2m()
            if submit_type == 'next_step':
                return redirect('create_project_target_location', project=project.pk)
            else:
                return redirect('create_project_activity_plan', project=project.pk)
        else:
            for form in formset:
                for error in form.errors:
                    error_message = f"Something went wrong {formset.errors}"
                    if form.errors[error]:
                        error_message = f"{error}: {form.errors[error][0]}"
                    messages.error(request, error_message)

    plans = list(activity_plans.values_list('pk', flat=True))
    clusters = project.clusters.all()
    cluster_ids = list(clusters.values_list('pk', flat=True))

    project_state = project.state
    parent_page = {
        'in-progress': 'active_projects',
        'draft': 'draft_projects',
        'done': 'completed_projects',
        'archive': 'archived_projects'
    }.get(project_state, None)

    context = {
        'project': project, 
        'formset': formset, 
        'clusters': cluster_ids, 
        'activity_planning': True,
        'plans': plans,
        'parent_page':parent_page
        }
    return render(request, 'projects/forms/project_activity_plan_form.html', context)


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
        country = request.POST.get('country')

        if formset.is_valid():
            for form in formset:
                if form.cleaned_data.get('save') or submit_type == 'next_step':
                    if form.cleaned_data.get('province') and form.cleaned_data.get('district'):
                        target_location = form.save(commit=False)
                        target_location.project = project
                        target_location.country_id = country
                        target_location.title = f"{target_location.province.name}, {target_location.district.name}, {target_location.site_name if target_location.site_name else ''}"
                        target_location.active = True
                        target_location.save()
            if submit_type == 'next_step':
                return redirect('project_plan_review', project=project.pk)
            else:
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
    project_state = project.state
    parent_page = {
        'in-progress': 'active_projects',
        'draft': 'draft_projects',
        'done': 'completed_projects',
        'archive': 'archived_projects'
    }.get(project_state, None)

    context = {
        'project': project,
        'formset': formset, 
        'locations_planning': True, 
        'plans': plans,
        'locations': locations,
        'parent_page':parent_page
    }
    return render(request, "projects/forms/project_target_locations.html", context)


@cache_control(no_store=True)
@login_required
def project_planning_review(request, **kwargs):
    """Projects Plans"""

    pk = int(kwargs['project'])
    project = get_object_or_404(Project, pk=pk)
    activity_plans = project.activityplan_set.all()
    target_locations = project.targetlocation_set.all()
    plans = list(activity_plans.values_list('pk', flat=True))
    locations = list(target_locations.values_list('pk', flat=True))
    project_state = project.state
    parent_page = {
        'in-progress': 'active_projects',
        'draft': 'draft_projects',
        'done': 'completed_projects',
        'archive': 'archived_projects'
    }.get(project_state, None)

    context = {
        'project': project,
        'activity_plans': activity_plans,
        'target_locations': target_locations,
        'project_review': True,
        'plans': plans,
        'locations': locations,
        'parent_page': parent_page
    }
    return render(request, 'projects/forms/project_review.html', context)


@cache_control(no_store=True)
@login_required
def submit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    activity_plans = project.activityplan_set.all()
    target_locations = project.targetlocation_set.all()
    if project:
        project.state = 'in-progress'
        project.save()

    for plan in activity_plans:
        plan.state = 'in-progress'
        plan.save()

    for target in target_locations:
        target.state = 'in-progress'
        target.save()

    return redirect('active_projects')


@cache_control(no_store=True)
@login_required
def archive_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project:
        activity_plans = project.activityplan_set.all()
        target_locations = project.targetlocation_set.all()

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

    return JsonResponse({ 'success': True})


@cache_control(no_store=True)
@login_required
def unarchive_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project:
        activity_plans = project.activityplan_set.all()
        target_locations = project.targetlocation_set.all()

        for plan in activity_plans:
            plan.state = 'draft'
            plan.active = True
            plan.save()

        for location in target_locations:
            location.state = 'draft'
            location.active = True
            location.save()

        project.state = 'draft'
        project.active = True
        project.save()

    return JsonResponse({ 'success': True})


@cache_control(no_store=True)
@login_required
def delete_project(request, pk):
    """Delete Project View"""
    project = get_object_or_404(Project, pk=pk)
    if project:
        project.delete()
    return JsonResponse({ 'success': True})


@cache_control(no_store=True)
@login_required
def copy_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project:
        new_project = get_object_or_404(Project, pk=pk)
        new_project.pk = None
        new_project.save()
        new_project.clusters.set(project.clusters.all())
        new_project.activity_domains.set(project.activity_domains.all())
        new_project.donors.set(project.donors.all())
        new_project.programme_partners.set(project.programme_partners.all())
        new_project.implementing_partners.set(project.implementing_partners.all())
        new_project.title = f"[COPY] - {project.title}"
        new_project.code = f"[COPY] - {project.code}"
        new_project.state = 'draft'

        if new_project:
            activity_plans = project.activityplan_set.all()
            target_locations = project.targetlocation_set.all()

            for plan in activity_plans:
                copy_project_activity_plan(new_project, plan)

            for location in target_locations:
                copy_project_target_location(new_project, location)

        new_project.save()

    return JsonResponse({ 'success': True, 'returnURL': reverse('view_project', args=[new_project.pk])})


def copy_project_activity_plan(project, plan):
    try:
        new_plan = get_object_or_404(ActivityPlan, pk=plan.pk)
        new_plan.pk = None
        new_plan.save()
        new_plan.project = project
        new_plan.active = True
        new_plan.state = 'draft'
        new_plan.title = f'[COPY] - {plan.title}'
        new_plan.indicators.set(plan.indicators.all())
        new_plan.save()
        return True
    except Exception as e:
        return False


def copy_project_target_location(project, location):
    try:
        new_location = get_object_or_404(TargetLocation, pk=location.pk)
        new_location.pk = None
        new_location.save()
        new_location.project = project
        new_location.active = True
        new_location.state = 'draft'
        new_location.title = f'[COPY] - {location.title}'
        new_location.save()
        return True
    except Exception as e:
        return False
    

@cache_control(no_store=True)
@login_required
def copy_activity_plan(request, project, plan):
    project = get_object_or_404(Project, pk=project)
    activity_plan = get_object_or_404(ActivityPlan, pk=plan)
    new_plan = get_object_or_404(ActivityPlan, pk=activity_plan.pk)
    if new_plan:
        new_plan.pk = None
        new_plan.save()
        new_plan.project = project
        new_plan.active = True
        new_plan.state = 'draft'
        new_plan.title = f'[COPY] - {activity_plan.title}'
        new_plan.indicators.set(activity_plan.indicators.all())
        new_plan.save()
    return JsonResponse({ 'success': True})


@cache_control(no_store=True)
@login_required
def delete_activity_plan(request, pk):
    activity_plan = get_object_or_404(ActivityPlan, pk=pk)
    project = activity_plan.project
    if activity_plan:
        activity_plan.delete()
    return JsonResponse({ 'success': True})


@cache_control(no_store=True)
@login_required
def copy_target_location(request, project, location):
    project = get_object_or_404(Project, pk=project)
    target_location = get_object_or_404(TargetLocation, pk=location)
    new_location = get_object_or_404(TargetLocation, pk=target_location.pk)
    if new_location:
        new_location.pk = None
        new_location.save()
        new_location.project = project
        new_location.active = True
        new_location.state = 'draft'
        new_location.title = f'[COPY] - {target_location.title}'
        new_location.save()
    return JsonResponse({ 'success': True})


@cache_control(no_store=True)
@login_required
def delete_target_location(request, pk):
    target_location = get_object_or_404(TargetLocation, pk=pk)
    project = target_location.project
    if target_location:
        target_location.delete()
    return JsonResponse({ 'success': True})


#############################################
########## Budget Progress Views ############
#############################################

@cache_control(no_store=True)
@login_required
def create_project_budget_progress_view(request, project):
    project = get_object_or_404(Project, pk=project)

    budget_progress = project.budgetprogress_set.all()

    BudgetProgressFormSet = modelformset_factory(BudgetProgress, form=BudgetProgressForm, extra=1)
    formset = BudgetProgressFormSet(request.POST or None, queryset=budget_progress, form_kwargs={'project': project})

    if request.method == 'POST':
        country = request.POST.get('country')

        if formset.is_valid():
            for form in formset:
                if form.cleaned_data.get('save'):
                    if form.cleaned_data.get('activity_domain') and form.cleaned_data.get('donor'):
                        budget_progress = form.save(commit=False)
                        budget_progress.project = project
                        budget_progress.country_id = country
                        budget_progress.title = f"{budget_progress.donor}: {budget_progress.activity_domain}"
                        budget_progress.save()
            return redirect('create_project_budget_progress', project=project.pk)
        else:
            for form in formset:
                for error in form.errors:
                    error_message = f"Something went wrong {formset.errors}"
                    if form.errors[error]:
                        error_message = f"{error}: {form.errors[error][0]}"
                    messages.error(request, error_message)

    progress = list(budget_progress.values_list('pk', flat=True))
    project_state = project.state
    parent_page = {
        'in-progress': 'active_projects',
        'draft': 'draft_projects',
        'done': 'completed_projects',
        'archive': 'archived_projects'
    }.get(project_state, None)

    context = {
        'project': project,
        'formset': formset,
        'parent_page': parent_page,
    }
    return render(request, "projects/financials/project_budget_progress.html", context)


@cache_control(no_store=True)
@login_required
def copy_budget_progress(request, project, budget):
    project = get_object_or_404(Project, pk=project)
    budget_progress = get_object_or_404(BudgetProgress, pk=budget)
    new_budget_progress = get_object_or_404(BudgetProgress, pk=budget_progress.pk)
    if new_budget_progress:
        new_budget_progress.pk = None
        new_budget_progress.save()
        new_budget_progress.project = project
        new_budget_progress.active = True
        new_budget_progress.state = 'draft'
        new_budget_progress.title = f'[COPY] - {budget_progress.title}'
        new_budget_progress.save()
    return JsonResponse({ 'success': True})


@cache_control(no_store=True)
@login_required
def delete_budget_progress(request, pk):
    budget_progress = get_object_or_404(BudgetProgress, pk=pk)
    project = budget_progress.project
    if budget_progress:
        budget_progress.delete()
    return JsonResponse({ 'success': True})