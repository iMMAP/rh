import calendar
import json
from collections import defaultdict
from datetime import datetime, timedelta

import pandas as pd
from django import forms
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import cache_control
from rh.models import (
    ActivityDetail,
    ActivityDomain,
    ActivityPlan,
    ActivityType,
    Disaggregation,
    FacilitySiteType,
    ImplementationModalityType,
    Indicator,
    Location,
    LocationType,
    Project,
    TargetLocation,
)

from .forms import (
    ActivityPlanReportForm,
    DisaggregationReportFormSet,
    IndicatorsForm,
    MonthlyReportFileUpload,
    ProjectMonthlyReportForm,
    TargetLocationReportFormSet,
)
from .models import ActivityPlanReport, DisaggregationLocationReport, ProjectMonthlyReport, TargetLocationReport

RECORDS_PER_PAGE = 10


def reports_dashboard_view(request):
    """Reports Dashboard"""
    project_reports = ProjectMonthlyReport.objects.all()
    # active_project_reports = project_reports.filter(active=True)
    # project_report_archive = project_reports.filter(active=False)
    # project_reports_todo = active_project_reports.filter(state__in=["todo", "pending", "submit", "reject"])
    # project_report_complete = active_project_reports.filter(state="complete")

    context = {
        # "project": project,
        "project_reports": project_reports,
        # "project_reports_todo": project_reports_todo,
        # "project_report_complete": project_report_complete,
        # "project_report_archive": project_report_archive,
        # # "report_filter":report_filter,
        # "project_view": False,
        # "financial_view": False,
        # "reports_view": True,
    }

    return render(request, "project_reports/dashboards/reports_dashboard.html", context)