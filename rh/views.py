RECORDS_PER_PAGE = 3

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.cache import cache_control

from .filters import *
from .forms import *
from .models import Project

# TODO: Add is_safe_url to redirects
# from django.utils.http import is_safe_url


#############################################
#                Index Views 
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
#               Project Views 
#############################################

@cache_control(no_store=True)
@login_required
def load_activity_domains(request):
    # FIXME: Fix the long url, by post request?
    cluster_ids = [int(i) for i in request.GET.getlist('clusters[]') if i]
    clusters = Cluster.objects.filter(pk__in=cluster_ids).prefetch_related('activitydomain_set')

    response = ''.join([
        f'<optgroup label="{cluster.title}">' +
        ''.join([f'<option value="{domain.pk}">{domain}</option>' for domain in
                 cluster.activitydomain_set.order_by('name')]) +
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
        ''.join(
            [f'<option value="{location.pk}">{location}</option>' for location in parent.children.order_by('name')]) +
        '</optgroup>'
        for parent in parents
    ])

    return JsonResponse(response, safe=False)


@cache_control(no_store=True)
@login_required
def load_facility_sites(request):
    # FIXME: Fix the long url, by post request?
    cluster_ids = [int(i) for i in request.GET.getlist('clusters[]') if i]
    clusters = Cluster.objects.filter(pk__in=cluster_ids)

    response = ''.join([
        f'<optgroup label="{cluster.title}">' +
        ''.join([f'<option value="{facility.pk}">{facility}</option>' for facility in
                 cluster.facilitysitetype_set.order_by('name')]) +
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
    """
    View function to handle creating or updating activity plans for a project.

    Args:
        request (HttpRequest): The HTTP request object.
        project (int): The primary key of the Project object.

    Returns:
        HttpResponse: The response containing the rendered template with the activity plan forms.
    """
    # Get the project object or return 404 if not found
    project = get_object_or_404(Project, pk=project)

    # Get all existing activity plans for the project
    activity_plans = project.activityplan_set.all()

    # Create the activity plan formset with initial data from the project
    activity_plan_formset = ActivityPlanFormSet(
        request.POST or None,
        instance=project,
        form_kwargs={'project': project}
    )
    target_location_formset = TargetLocationFormSet(
        request.POST or None,
    )

    target_location_formsets = []

    # Iterate over activity plan forms in the formset
    for activity_plan_form in activity_plan_formset.forms:
        # Create a target location formset for each activity plan form
        target_location_formset = TargetLocationFormSet(
            request.POST or None,
            instance=activity_plan_form.instance,
            prefix=f'target_locations_{activity_plan_form.prefix}'
        )
        for target_location_form in target_location_formset.forms:
            # Create a disaggregation formset for each target location form
            disaggregation_formset = DisaggregationFormSet(
                request.POST or None,
                instance=target_location_form.instance,
                prefix=f'disaggregation_{target_location_form.prefix}'
            )
            target_location_form.disaggregation_formset = disaggregation_formset

        target_location_formsets.append(target_location_formset)

    if request.method == 'POST':
        # Check if the form was submitted for "Next Step" or "Save & Continue"
        submit_type = request.POST.get('submit_type')

        if activity_plan_formset.is_valid():
            # Save valid activity plan forms
            for activity_plan_form in activity_plan_formset:
                if activity_plan_form.cleaned_data.get('activity_domain') and activity_plan_form.cleaned_data.get(
                        'activity_type'):
                    activity_plan_form.save()

            # Process target location forms and their disaggregation forms
            for target_location_formset in target_location_formsets:
                if target_location_formset.is_valid():
                    for target_location_form in target_location_formset:
                        if target_location_form.cleaned_data != {}:
                            if target_location_form.cleaned_data.get(
                                    'province') and target_location_form.cleaned_data.get('district'):

                                target_location_instance = target_location_form.save()

                        if hasattr(target_location_form, 'disaggregation_formset'):
                            disaggregation_formset = target_location_form.disaggregation_formset
                            if disaggregation_formset.is_valid():

                                # Delete the exisiting instances of the disaggregation location and create new
                                # based on the indicator disaggregations
                                target_location_form.instance.disaggregationlocation_set.all().delete()

                                for disaggregation_form in disaggregation_formset:
                                    if disaggregation_form.cleaned_data != {} and disaggregation_form.cleaned_data.get('target') > 0:
                                        disaggregation_instance = disaggregation_form.save(commit=False)
                                        disaggregation_instance.target_location = target_location_instance
                                        disaggregation_instance.save()

            activity_plan_formset.save()

            if submit_type == 'next_step':
                # Redirect to the project review page if "Next Step" is clicked
                return redirect('project_plan_review', project=project.pk)
            else:
                # Redirect back to this view if "Save & Continue" is clicked
                return redirect('create_project_activity_plan', project=project.pk)
        else:
            # TODO:
            # Handle invalid activity_plan_formset
            # Add error handling code here
            pass

    # Prepare data for rendering the template
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
        'activity_plan_formset': activity_plan_formset,
        'target_location_formset': target_location_formset,
        'combined_formset': combined_formset,
        'clusters': cluster_ids,
        'activity_planning': True,
        'plans': plans,
        'parent_page': parent_page
    }

    # Render the template with the context data
    return render(request, 'rh/projects/forms/project_activity_plan_form.html', context)


@login_required
def get_disaggregations_forms(request):
    """Get target location empty form"""
    # FIXME: Fix the long url, by post request?
    # Get selected indicators
    indicators = Indicator.objects.filter(pk__in=request.GET.getlist('indicators[]'))

    # Get selected locations prefixes
    locations_prefix = request.GET.getlist('locations_prefixes[]')

    # Use a set to store unique related Disaggregations
    unique_related_disaggregations = set()

    # Loop through each Indicator and retrieve its related Disaggregations
    for indicator in indicators:
        related_disaggregations = indicator.disaggregation_set.all()
        unique_related_disaggregations.update(related_disaggregations)

    # Convert the set to a list
    unique_related_disaggregations = list(unique_related_disaggregations)

    # Create a dictionary to hold disaggregation forms per location prefix
    location_disaggregation_dict = {}

    initial_data = []

    # Populate initial data with related disaggregations
    if unique_related_disaggregations:
        for disaggregation in unique_related_disaggregations:
            initial_data.append({'disaggregation': disaggregation})

        # Create DisaggregationFormSet for each location prefix
        for location_prefix in locations_prefix:
            DisaggregationFormSet.extra = len(unique_related_disaggregations)
            disaggregation_formset = DisaggregationFormSet(prefix=f'disaggregation_{location_prefix}',
                                                            initial=initial_data)

            # Generate HTML for each disaggregation form and store in dictionary
            for disaggregation_form in disaggregation_formset.forms:
                context = {
                    'disaggregation_form': disaggregation_form,
                }
                html = render_to_string('rh/projects/forms/disaggregation_empty_form.html', context)
            
                if location_prefix in location_disaggregation_dict:
                    location_disaggregation_dict[location_prefix].append(html)
                else:
                    location_disaggregation_dict.update({location_prefix: [html]})

    # Set back extra to 0 to avoid empty forms if refreshed.
    DisaggregationFormSet.extra = 0

    # Return JSON response containing generated HTML forms
    return JsonResponse(location_disaggregation_dict)


@login_required
def get_target_location_empty_form(request):
    """Get an empty target location form for a project"""
    # FIXME: Fix the long url, by post request?
    # Get the project object based on the provided project ID
    project = get_object_or_404(Project, pk=request.GET.get('project'))

    # Prepare form_kwargs to pass to ActivityPlanFormSet
    form_kwargs = {'project': project}

    # Create an instance of ActivityPlanFormSet using the project instance and form_kwargs
    activity_plan_formset = ActivityPlanFormSet(form_kwargs=form_kwargs, instance=project)

    # Get the prefix index from the request
    prefix_index = request.GET.get('prefix_index')

    # Create an instance of TargetLocationFormSet with a prefixed name
    target_location_formset = TargetLocationFormSet(
        prefix=f"target_locations_{activity_plan_formset.prefix}-{prefix_index}"
    )

    # for target_location_form in target_location_formset.forms:
        # Create a disaggregation formset for each target location form
    target_location_form = target_location_formset.empty_form
    disaggregation_formset = DisaggregationFormSet(
        request.POST or None,
        instance=target_location_form.instance,
        prefix=f'disaggregation_{target_location_form.prefix}'
    )
    target_location_form.disaggregation_formset = disaggregation_formset

    # Prepare context for rendering the target location form template
    context = {
        'target_location_form': target_location_form,
    }

    # Render the target location form template and generate HTML
    html = render_to_string('rh/projects/forms/target_location_empty_form.html', context)

    # Return JSON response containing the generated HTML
    return JsonResponse({'html': html})


@login_required
def get_activity_empty_form(request):
    """Get an empty activity form"""
    # FIXME: Fix the long url, by post request?
    # Get the project object based on the provided project ID
    project = get_object_or_404(Project, pk=request.GET.get('project'))

    # Get all activity plans associated with the project
    activity_plans = project.activityplan_set.all()

    # Extract a list of primary keys (pk) from activity plans
    plans = list(activity_plans.values_list('pk', flat=True))

    # Prepare form_kwargs to pass to ActivityPlanFormSet
    form_kwargs = {'project': project}

    # Create an instance of ActivityPlanFormSet using the project instance and form_kwargs
    activity_plan_formset = ActivityPlanFormSet(form_kwargs=form_kwargs, instance=project)

    # Get the prefix index from the request
    prefix_index = request.GET.get('prefix_index')

    # Create an instance of TargetLocationFormSet with a prefixed name
    target_location_formset = TargetLocationFormSet(
        prefix=f"target_locations_{activity_plan_formset.prefix}-{prefix_index}"
    )

    # Prepare context for rendering the activity empty form template
    context = {
        'form': activity_plan_formset.empty_form,
        'target_location_formset': target_location_formset,
        'project': project,
        'plans': plans
    }

    # Render the activity empty form template and generate HTML
    html = render_to_string('rh/projects/forms/activity_empty_form.html', context)

    # Return JSON response containing the generated HTML
    return JsonResponse({'html': html})


# TODO: Fix the functions related to the above activity planning changes

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

    return JsonResponse({'success': True})


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

    return JsonResponse({'success': True})


@cache_control(no_store=True)
@login_required
def delete_project(request, pk):
    """Delete Project View"""
    project = get_object_or_404(Project, pk=pk)
    if project:
        project.delete()
    return JsonResponse({'success': True})


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

    return JsonResponse({'success': True, 'returnURL': reverse('view_project', args=[new_project.pk])})


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
    return JsonResponse({'success': True})


@cache_control(no_store=True)
@login_required
def delete_activity_plan(request, pk):
    activity_plan = get_object_or_404(ActivityPlan, pk=pk)
    project = activity_plan.project
    if activity_plan:
        activity_plan.delete()
    return JsonResponse({'success': True})


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
    return JsonResponse({'success': True})


@cache_control(no_store=True)
@login_required
def delete_target_location(request, pk):
    target_location = get_object_or_404(TargetLocation, pk=pk)
    project = target_location.project
    if target_location:
        target_location.delete()
    return JsonResponse({'success': True})


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
    return JsonResponse({'success': True})


@cache_control(no_store=True)
@login_required
def delete_budget_progress(request, pk):
    budget_progress = get_object_or_404(BudgetProgress, pk=pk)
    project = budget_progress.project
    if budget_progress:
        budget_progress.delete()
    return JsonResponse({'success': True})


def form_create_view(request):
    YourModelFormSet = modelformset_factory(TargetLocation, fields="__all__")
    formset = YourModelFormSet(queryset=TargetLocation.objects.none())
    return render(request, 'rh/projects/forms/form_create.html', {'formset': formset})
