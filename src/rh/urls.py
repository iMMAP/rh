from django.urls import path

from . import exports as export_views
from . import views as user_views

urlpatterns = [
    path("", user_views.landing_page, name="landing"),
    # Organization CRUD
    path("organizations/create/", user_views.organization_register, name="organizations-create"),
    # Projects CRUD
    path("projects/", user_views.projects_list, name="projects-list"),
    path("projects/create/", user_views.create_project_view, name="projects-create"),
    path(
        "projects/<str:pk>/",
        user_views.projects_detail,
        name="projects-detail",
    ),
    path(
        "projects/<str:pk>/update",
        user_views.update_project_view,
        name="projects-update",
    ),
    path(
        "projects/<str:pk>/delete",
        user_views.delete_project,
        name="projects-delete",
    ),
    path(
        "projects/project_plan/archive/<str:pk>/",
        user_views.archive_project,
        name="archive_project",
    ),
    path(
        "projects/project_plan/unarchive/<str:pk>/",
        user_views.unarchive_project,
        name="unarchive_project",
    ),
    path(
        "projects/project_plan/copy/<str:pk>/",
        user_views.copy_project,
        name="copy_project",
    ),
    # Projects Activity Plannings CRUD
    path(
        "projects/<int:project>/activity_plan/<str:plan>/copy/",
        user_views.copy_activity_plan,
        name="copy_plan",
    ),
    path(
        "project/activity_plan/<str:pk>/delete/",
        user_views.delete_activity_plan,
        name="delete_plan",
    ),
    path(
        "projects/<int:project>/activity_plan/create",
        user_views.create_project_activity_plan,
        name="create_project_activity_plan",
    ),
    # Projects Target Locations CRUD
    path(
        "projects/<int:project>/target_location/<str:location>/copy/",
        user_views.copy_target_location,
        name="copy_location",
    ),
    path(
        "projects/target_location/<str:pk>/delete",
        user_views.delete_target_location,
        name="delete_location",
    ),
    path(
        "projects/<int:project>/project_plan/review/",
        user_views.project_planning_review,
        name="project_plan_review",
    ),
    path(
        "projects/<str:pk>/project_plan/submit/",
        user_views.submit_project,
        name="project_submit",
    ),
    # Financial Reporting
    path(
        "projects/<int:project>/financials/budget_progress/",
        user_views.create_project_budget_progress_view,
        name="create_project_budget_progress",
    ),
    path(
        "projects/<int:project>/budget_progress/<str:budget>/copy/",
        user_views.copy_budget_progress,
        name="copy_budget",
    ),
    path(
        "projects/budget_progress/<str:pk>/delete/",
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
        "project/active/bulk_export/<flag>",
        user_views.ProjectListView,
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
        user_views.update_indicator_type,
        name="update_indicator_type",
    ),
    # User Guide Download Link
    path("rh/user_guide/download/", user_views.download_user_guide, name="download_user_guide"),
]
