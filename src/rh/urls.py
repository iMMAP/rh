from django.urls import path

from .views import exports as export_views

from .views.views import landing_page, download_user_guide, load_facility_sites, load_activity_domains
from .views import (
    projects as projects,
    activity_plans as activity_plans,
    organizations as organizations,
    budget_progress as budget_progress,
    disaggregations as disaggregations,
    target_locations as target_locations,
    locations as locations,
)


urlpatterns = [
    path("", landing_page, name="landing"),
    # Organization CRUD
    path("organizations/create/", organizations.organization_register, name="organizations-create"),
    # Projects CRUD
    path("projects/", projects.projects_list, name="projects-list"),
    path("projects/create/", projects.create_project, name="projects-create"),
    path(
        "projects/<str:pk>/",
        projects.projects_detail,
        name="projects-detail",
    ),
    path(
        "projects/<str:pk>/update",
        projects.update_project,
        name="projects-update",
    ),
    path(
        "projects/<str:pk>/delete",
        projects.delete_project,
        name="projects-delete",
    ),
    path(
        "projects/project_plan/archive/<str:pk>/",
        projects.archive_project,
        name="archive_project",
    ),
    path(
        "projects/project_plan/unarchive/<str:pk>/",
        projects.unarchive_project,
        name="unarchive_project",
    ),
    path(
        "projects/project_plan/copy/<str:pk>/",
        projects.copy_project,
        name="copy_project",
    ),
    # Projects Activity Plannings CRUD
    path(
        "projects/<int:project>/activity_plan/<str:plan>/copy/",
        activity_plans.copy_activity_plan,
        name="copy_plan",
    ),
    path(
        "project/activity_plan/<str:pk>/delete/",
        activity_plans.delete_activity_plan,
        name="delete_plan",
    ),
    path(
        "projects/<int:project>/activity_plan/create",
        activity_plans.create_project_activity_plan,
        name="create_project_activity_plan",
    ),
    # Projects Target Locations CRUD
    path(
        "projects/<int:project>/target_location/<str:location>/copy/",
        target_locations.copy_target_location,
        name="copy_location",
    ),
    path(
        "projects/target_location/<str:pk>/delete",
        target_locations.delete_target_location,
        name="delete_location",
    ),
    path(
        "projects/<int:project>/project_plan/review/",
        projects.project_planning_review,
        name="project_plan_review",
    ),
    path(
        "projects/<str:pk>/project_plan/submit/",
        projects.submit_project,
        name="project_submit",
    ),
    # Financial Reporting
    path(
        "projects/<int:project>/financials/budget_progress/",
        budget_progress.create_project_budget_progress_view,
        name="create_project_budget_progress",
    ),
    path(
        "projects/<int:project>/budget_progress/<str:budget>/copy/",
        budget_progress.copy_budget_progress,
        name="copy_budget",
    ),
    path(
        "projects/budget_progress/<str:pk>/delete/",
        budget_progress.delete_budget_progress,
        name="delete_budget",
    ),
    # Ajax for data load
    path(
        "ajax/load-activity_domains/",
        load_activity_domains,
        name="ajax-load-activity_domains",
    ),
    path(
        "ajax/load-locations-details/",
        locations.load_locations_details,
        name="ajax-load-locations",
    ),
    path(
        "ajax/load-facility_sites/",
        load_facility_sites,
        name="ajax-load-facility_sites",
    ),
    path(
        "ajax/get_target_location_empty_form/",
        target_locations.get_target_location_empty_form,
        name="get_target_location_empty_form",
    ),
    path(
        "ajax/get_activity_empty_form/",
        activity_plans.get_activity_empty_form,
        name="get_activity_empty_form",
    ),
    path(
        "ajax/get_disaggregations_forms/",
        disaggregations.get_disaggregations_forms,
        name="get_disaggregations_forms",
    ),
    # Exports
    path(
        "project/export-excel/<int:project_id>/",
        export_views.ProjectExportExcelView.as_view(),
        name="export_project_excel",
    ),
    # Filter Export
    path(
        "project/export/<int:projectId>",
        export_views.ProjectFilterExportView.as_view(),
        name="export_project_filter",
    ),
    # bulk export
    path(
        "project/active/bulk_export/<format>",
        projects.export,
        name="export_porjcet_list",
    ),
    # single project csv export
    path(
        "project/export/CSV/<int:project_id>",
        export_views.ProjectExportCSV.as_view(),
        name="export_porjcet_CSV",
    ),
    path(
        "project/activityplan/indicator-type",
        activity_plans.update_indicator_type,
        name="update_indicator_type",
    ),
    # User Guide Download Link
    path("rh/user_guide/download/", download_user_guide, name="download_user_guide"),
]
