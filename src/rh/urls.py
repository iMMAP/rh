from django.urls import path

from . import exports as export_views
from . import views as user_views

urlpatterns = [
    path("", user_views.index, name="index"),
    path("home", user_views.home, name="home"),
    # Projects CRUD
    path("projects/draft/", user_views.draft_projects_view, name="draft_projects"),
    path("projects/active/", user_views.active_projects_view, name="active_projects"),
    path(
        "projects/completed/",
        user_views.completed_projects_view,
        name="completed_projects",
    ),
    path(
        "projects/archived/",
        user_views.archived_projects_view,
        name="archived_projects",
    ),
    path("project/create/", user_views.create_project_view, name="create_project"),
    path(
        "project/project_plan/<str:pk>/",
        user_views.update_project_view,
        name="update_project",
    ),
    path(
        "project/project_plan/archive/<str:pk>/",
        user_views.archive_project,
        name="archive_project",
    ),
    path(
        "project/project_plan/unarchive/<str:pk>/",
        user_views.unarchive_project,
        name="unarchive_project",
    ),
    path(
        "project/project_plan/delete/<str:pk>/",
        user_views.delete_project,
        name="delete_project",
    ),
    path(
        "project/project_plan/copy/<str:pk>/",
        user_views.copy_project,
        name="copy_project",
    ),
    path(
        "project/view_project/<str:pk>/",
        user_views.open_project_view,
        name="view_project",
    ),
    # Projects Activity Plannings CRUD
    path(
        "project/activity_plan/copy/<str:project>/<str:plan>/",
        user_views.copy_activity_plan,
        name="copy_plan",
    ),
    path(
        "project/activity_plan/delete/<str:pk>/",
        user_views.delete_activity_plan,
        name="delete_plan",
    ),
    path(
        "project/activity_plan/create/?project=<str:project>/",
        user_views.create_project_activity_plan,
        name="create_project_activity_plan",
    ),
    # Projects Target Locations CRUD
    path(
        "project/target_location/copy/<str:project>/<str:location>/",
        user_views.copy_target_location,
        name="copy_location",
    ),
    path(
        "project/target_location/delete/<str:pk>/",
        user_views.delete_target_location,
        name="delete_location",
    ),
    path(
        "project/project_plan/review/?project=<str:project>/",
        user_views.project_planning_review,
        name="project_plan_review",
    ),
    path(
        "project/project_plan/submit/<str:pk>/",
        user_views.submit_project,
        name="project_submit",
    ),
    # Financial Reporting
    path(
        "project/financials/budget_progress/?project=<str:project>/",
        user_views.create_project_budget_progress_view,
        name="create_project_budget_progress",
    ),
    path(
        "project/budget_progress/copy/<str:project>/<str:budget>/",
        user_views.copy_budget_progress,
        name="copy_budget",
    ),
    path(
        "project/budget_progress/delete/<str:pk>/",
        user_views.delete_budget_progress,
        name="delete_budget",
    ),
    # Ajax for data load
    path(
        "ajax/load-activity_domains/",
        user_views.load_activity_domains,
        name="ajax-load-activity_domains",
    ),
    path(
        "ajax/load-locations-details/",
        user_views.load_locations_details,
        name="ajax-load-locations",
    ),
    path(
        "ajax/load-facility_sites/",
        user_views.load_facility_sites,
        name="ajax-load-facility_sites",
    ),
    path(
        "ajax/get_target_location_empty_form/",
        user_views.get_target_location_empty_form,
        name="get_target_location_empty_form",
    ),
    path(
        "ajax/get_activity_empty_form/",
        user_views.get_activity_empty_form,
        name="get_activity_empty_form",
    ),
    path(
        "ajax/get_disaggregations_forms/",
        user_views.get_disaggregations_forms,
        name="get_disaggregations_forms",
    ),
    # Exports
    path(
        "export-excel/<int:project_id>/",
        export_views.ProjectExportExcelView.as_view(),
        name="export_project_excel",
    ),
    # Filter Export
    path(
        "export-filter/",
        export_views.ProjectFilterExportView.as_view(),
        name="export_project_filter",
    ),
    # path(
    #     "project/view_project/1/export-filter/",
    #     user_views.ProjectFilterExportView,
    #     name="export_project_filter",
    #     ),
]
