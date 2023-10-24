
from django.contrib.auth.decorators import login_required
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import cache_control

from .forms import *
from .models import *


@cache_control(no_store=True)
@login_required
def index_project_report_view(request, project):
    """Project Monthly Report View"""
    project = get_object_or_404(Project, pk=project)
    project_reports = ProjectMonthlyReport.objects.all()
    project_reports_todo = project_reports.filter(state__in=['todo', 'pending'])
    project_report_complete = project_reports.filter(state='complete')
    project_state = project.state
    parent_page = {
        'in-progress': 'active_projects',
        'draft': 'draft_projects',
        'done': 'completed_projects',
        'archive': 'archived_projects'
    }.get(project_state, None)
    context = {
        'project': project,
        'parent_page': parent_page,
        'project_reports': project_reports,
        'project_reports_todo': project_reports_todo,
        'project_report_complete': project_report_complete,
        'project_view': False,
        'financial_view': False,
        'reports_view': True,
    }

    return render(request, 'project_reports/views/monthly_reports_view_base.html', context)


@cache_control(no_store=True)
@login_required
def create_project_monthly_report_view(request, project):
    """Project Monthly Report Creation View"""
    project = get_object_or_404(Project, pk=project)
    project_state = project.state

    # Get all existing activity plans for the project
    activity_plans = project.activityplan_set.all()

    # Create the activity plan formset with initial data from the project
    ActivityReportFormset = inlineformset_factory(
        ProjectMonthlyReport,
        ActivityPlanReport,
        form=ActivityPlanReportForm,
        extra=len(activity_plans),
        can_delete=True,
    )

    activity_report_formset = ActivityReportFormset(
        request.POST or None,
    )
    # Loop through the forms in the formset and set initial values for specific fields
    for i, form in enumerate(activity_report_formset.forms):
        if i < len(activity_plans):
            activity_plan = activity_plans[i]
            form.initial = {'activity_plan': activity_plan}
            form.fields['indicator'].queryset = activity_plan.indicators.all()


    parent_page = {
        'in-progress': 'active_projects',
        'draft': 'draft_projects',
        'done': 'completed_projects',
        'archive': 'archived_projects'
    }.get(project_state, None)

    context = {
        'project': project,
        'activity_plans': activity_plans,
        'activity_report_formset': activity_report_formset,
        'parent_page': parent_page,
        'project_view': False,
        'financial_view': False,
        'reports_view': True,
    }

    return render(request, 'project_reports/forms/monthly_report_form.html', context)


@cache_control(no_store=True)
@login_required
def details_monthly_progress_view(request, pk):
    """Project Monthly Report Read View"""
    project = get_object_or_404(Project, pk=pk)
    project_state = project.state
    parent_page = {
        'in-progress': 'active_projects',
        'draft': 'draft_projects',
        'done': 'completed_projects',
        'archive': 'archived_projects'
    }.get(project_state, None)
    context = {
        'project': project,
        'parent_page': parent_page,
        'project_view': False,
        'financial_view': False,
        'reports_view': True,
    }

    return render(request, 'project_reports/views/monthly_report_view.html', context)