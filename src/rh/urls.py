from django.urls import path

from .views import exports as export_views

from .views.views import (
    landing_page,
    load_facility_sites,
    load_activity_domains,
    get_activity_domain_types,
    get_activity_type_indicators,
    get_locations_details,
)
from .views import (
    projects as projects,
    activity_plans as activity_plans,
    organizations as organizations,
    budget_progress as budget_progress,
    target_locations as target_locations,
)


urlpatterns = [
    path("", landing_page, name="landing"),
    # Organization CRUD
    path("organizations/create/", organizations.organization_register, name="organizations-create"),
    # Projects CRUD
    path("projects/", projects.org_projects_list, name="projects-list"),
    path(
        "projects/export-ap-import-template/<int:pk>",
        projects.export_activity_plans_import_template,
        name="projects-ap-import-template",
    ),
    path(
        "projects/import-activity-plans/<int:pk>", projects.import_activity_plans, name="projects-import-activity-plans"
    ),
    path("projects/clusters", projects.users_clusters_projects_list, name="user-clusters-projects-list"),
    path("projects/clusters/<str:cluster>", projects.cluster_projects_list, name="cluster-projects-list"),
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
    # load
    path(
        "activity-domains/activity-types",
        get_activity_domain_types,
        name="activity-domains-types",
    ),
    path(
        "activity-types/indicators",
        get_activity_type_indicators,
        name="activity-types-indicators",
    ),
    path(
        "indicator/types",
        activity_plans.update_indicator_type,
        name="update-indicator-type",
    ),
    # Projects Activity Plannings CRUD
    path(
        "activity-plans/<int:pk>/update",
        activity_plans.update_activity_plan,
        name="activity-plans-update",
    ),
    path(
        "activity-plans/<int:pk>/delete/",
        activity_plans.delete_activity_plan,
        name="activity-plans-delete",
    ),
    path(
        "activity-plans/project/<int:project>/create",
        activity_plans.create_activity_plan,
        name="activity-plans-create",
    ),
    path(
        "activity-plans/<int:pk>/copy",
        activity_plans.copy_activity_plan,
        name="activity-plans-copy",
    ),
    path(
        "projects/<int:project>/target-locations",
        target_locations.list_target_locations,
        name="target-locations-list",
    ),
    path(
        "projects/<int:project>/activity-plans",
        activity_plans.list_activity_plans,
        name="activity-plans-list",
    ),
    # Projects Target Locations CRUD
    path(
        "target-locations/<int:pk>/update",
        target_locations.update_target_location,
        name="target-locations-update",
    ),
    path(
        "target-locations/activity-plan/<int:activity_plan>/create",
        target_locations.create_target_location,
        name="target-locations-create",
    ),
    path(
        "projects/<int:project>/target_location/<str:location>/copy/",
        target_locations.copy_target_location,
        name="copy_location",
    ),
    path(
        "target-locations/<int:pk>/delete",
        target_locations.delete_target_location,
        name="target-locations-delete",
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
        get_locations_details,
        name="get-locations-details",
    ),
    path(
        "ajax/load-facility_sites/",
        load_facility_sites,
        name="ajax-load-facility_sites",
    ),
    # Exports
    path(
        "project/export-excel/<str:format>/",
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
        "projects/bulk_export/<str:format>/org",
        projects.export_org_projects,
        name="export-org-projects",
    ),
    path(
        "projects/bulk_export/<str:format>/clusters",
        projects.export_cluster_projects,
        name="export-clusters-projects",
    ),
]
