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
# from django.db.models import Q

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
def load_activity_domains(request):
    # FIXME: Fix the long url, by post request?
    cluster_ids = [int(i) for i in request.GET.getlist('clusters[]') if i]
    clusters = Cluster.objects.filter(pk__in=cluster_ids).prefetch_related('activitydomain_set')

    response = ''.join([
        f'<optgroup label="{cluster.title}">' +
        ''.join([f'<option value="{domain.pk}">{domain}</option>' for domain in cluster.activitydomain_set.order_by('name')]) +
        '</optgroup>'
        for cluster in clusters
    ])

    return JsonResponse(response, safe=False)


@cache_control(no_store=True)
@login_required
def load_locations_details(request):
    # FIXME: Fix the long url, by post request?

    parent_ids = [int(i) for i in request.GET.getlist('parents[]') if i]
    parents = Location.objects.filter(pk__in=parent_ids).select_related('parent')

    response = ''.join([
        f'<optgroup label="{parent.name}">' +
        ''.join([f'<option value="{location.pk}">{location}</option>' for location in parent.children.order_by('name')]) +
        '</optgroup>'
        for parent in parents
    ])

    return JsonResponse(response, safe=False)

# @cache_control(no_store=True)
# @login_required
# def load_locations_details(request):
#     # FIXME: Fix the long url, by post request?
#     parent_ids = [int(i) for i in request.GET.getlist('parents[]') if i]
#     parents = Location.objects.filter(pk__in=parent_ids).select_related('parent')

#     response = ''.join([
#         f'<optgroup label="{parent.name}">' +
#         ''.join([f'<option value="{location.pk}">{location}</option>' for location in parent.location_set.order_by('name')]) +
#         '</optgroup>'
#         for parent in parents
#     ])

    # return JsonResponse(response, safe=False)


@cache_control(no_store=True)
@login_required
def load_facility_sites(request):
    # FIXME: Fix the long url, by post request?
    cluster_ids = [int(i) for i in request.GET.getlist('clusters[]') if i]
    clusters = Cluster.objects.filter(pk__in=cluster_ids)

    response = ''.join([
        f'<optgroup label="{cluster.title}">' +
        ''.join([f'<option value="{facility.pk}">{facility}</option>' for facility in cluster.facilitysitetype_set.order_by('name')]) +
        '</optgroup>'
        for cluster in clusters
    ])

    return JsonResponse(response, safe=False)


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
    return render(request, 'rh/projects/views/draft_projects.html', context)


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
    return render(request, 'rh/projects/views/active_projects.html', context)


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
    return render(request, 'rh/projects/views/completed_projects.html', context)


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
    return render(request, 'rh/projects/views/archived_projects.html', context)


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
    return render(request, 'rh/projects/views/completed_project.html', context)


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
    return render(request, 'rh/projects/views/project_view.html', context)


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
            # clusters = request.user.profile.clusters.all()
            form = ProjectForm(initial={'user': request.user, 'country': country})
        else:
            form = ProjectForm()

    context = {
        'form': form, 
        'project_planning': True, 
    }
    return render(request, 'rh/projects/forms/project_form.html', context)


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
        'done': 'completed_projects',
        'archive': 'archived_projects'
    }.get(project_state, None)

    context = {
        'form': form,
        'project': project,
        'project_planning': True,
        'plans': plans,
        'locations': locations,
        'parent_page': parent_page
    }
    return render(request, 'rh/projects/forms/project_form.html', context)


@cache_control(no_store=True)
@login_required
def create_project_activity_plan(request, project):
    project = get_object_or_404(Project, pk=project)
    activity_plans = project.activityplan_set.all()

    activity_plan_formset = ActivityPlanFormSet(
        request.POST or None,
        instance=project,
        form_kwargs={'project': project}
    )

    target_location_formsets = []
    for activity_plan_form in activity_plan_formset.forms:
        target_location_formset = TargetLocationFormSet(
            request.POST or None,
            instance=activity_plan_form.instance,
            prefix=f'target_locations_{activity_plan_form.prefix}'
        )
        for target_location_form in target_location_formset.forms:
            disaggregation_formset = DisaggregationFormSet(
                request.POST or None,
                instance=target_location_form.instance,
                prefix=f'disaggregation_{target_location_form.prefix}'
            )        
            target_location_form.disaggregation_formset = disaggregation_formset

        target_location_formsets.append(target_location_formset)

    
    if request.method == 'POST':
        if activity_plan_formset.is_valid():
            activity_plan_instances = activity_plan_formset.save()
            for activity_plan_instance, target_location_formset in zip(activity_plan_instances, target_location_formsets):
                if target_location_formset.is_valid():
                    target_location_instances = target_location_formset.save(commit=False)

                    for target_location_instance, target_location_form in zip(target_location_instances, target_location_formset.forms):
                        target_location_instance.activity_plan = activity_plan_instance
                        target_location_instance.save()

                        if hasattr(target_location_form, 'disaggregation_formset'):
                            disaggregation_formset = target_location_form.disaggregation_formset
                            if disaggregation_formset.is_valid():
                                disaggregation_instances = disaggregation_formset.save(commit=False)
                                for disaggregation_instance in disaggregation_instances:
                                    disaggregation_instance.target_location = target_location_instance
                                    disaggregation_instance.save()

                    target_location_formset.save()
                    target_location_formset.save_m2m()

        else:
            # TODO:
            # Handle invalid activity_plan_formset
            # add error handling code here
            pass

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

    combined_formset = zip(activity_plan_formset.forms, target_location_formsets)

    context = {
        'project': project,
        'formset': activity_plan_formset,
        'combined_formset': combined_formset,
        'clusters': cluster_ids,
        'activity_planning': True,
        'plans': plans,
        'parent_page': parent_page
    }
    return render(request, 'rh/projects/forms/project_activity_plan_form.html', context)


@cache_control(no_store=True)
@login_required
def create_project_target_location(request, plan):
    activity_plan = get_object_or_404(ActivityPlan, pk=plan)
    project = activity_plan.project

    target_locations = activity_plan.targetlocation_set.all()

    TargetLocationsFormSet = modelformset_factory(TargetLocation, form=TargetLocationForm, extra=1)
    formset = TargetLocationsFormSet(request.POST or None, queryset=target_locations, form_kwargs={'activity_plan': plan, 'project': project})

    # if request.method == 'POST':
    #     submit_type = request.POST.get('submit_type')
    #     country = request.POST.get('country')

    #     if formset.is_valid():
    #         for form in formset:
    #             if form.cleaned_data.get('save') or submit_type == 'next_step':
    #                 if form.cleaned_data.get('province') and form.cleaned_data.get('district'):
    #                     target_location = form.save(commit=False)
    #                     target_location.project = project
    #                     target_location.country_id = country
    #                     target_location.title = f"{target_location.province.name}, {target_location.district.name}, {target_location.site_name if target_location.site_name else ''}"
    #                     target_location.active = True
    #                     target_location.save()
    #         if submit_type == 'next_step':
    #             return redirect('project_plan_review', project=project.pk)
    #         else:
    #             return redirect('create_project_target_location', project=project.pk)
    #     else:
    #         for form in formset:
    #             for error in form.errors:
    #                 error_message = f"Something went wrong {formset.errors}"
    #                 if form.errors[error]:
    #                     error_message = f"{error}: {form.errors[error][0]}"
    #                 messages.error(request, error_message)

    # plans = list(activity_plans.values_list('pk', flat=True))
    # locations = list(target_locations.values_list('pk', flat=True))
    # project_state = project.state
    # parent_page = {
    #     'in-progress': 'active_projects',
    #     'draft': 'draft_projects',
    #     'done': 'completed_projects',
    #     'archive': 'archived_projects'
    # }.get(project_state, None)

    context = {
        # 'project': project,
        'formset': formset, 
        # 'locations_planning': True, 
        # 'plans': plans,
        # 'locations': locations,
        # 'parent_page':parent_page
    }
    return render(request, "rh/projects/forms/form_create.html", context)


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
    return render(request, 'rh/projects/forms/project_review.html', context)


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
    return render(request, "rh/projects/financials/project_budget_progress.html", context)


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



def form_create_view(request):
    YourModelFormSet = modelformset_factory(TargetLocation, fields="__all__")
    formset = YourModelFormSet(queryset=TargetLocation.objects.none())
    return render(request, 'rh/projects/forms/form_create.html', {'formset': formset})