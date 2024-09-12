from django.urls import path

from . import dashboards as dashboard_views
from . import exports as export_views
from .views.views import (
    import_report_activities,
    export_report_activities_import_template,
)
from .views import (
    cluster_powerbi_report as fetch_powerbi_report_view,
    report_activity_plans as plan_views,
    report_target_locations as location_views,
    monthly_reports as report_views,
)

urlpatterns = [
    # Monthly Report URLS
    path(
        "project/<str:project>/monthly_progress",
        report_views.index_project_report_view,
        name="project_reports_home",
    ),
    path(
        "project/<str:project>/monthly_progress/<str:report>/view/",
        report_views.details_monthly_progress_view,
        name="view_monthly_report",
    ),
    path(
        "project/<str:project>/monthly_progress/create/",
        report_views.create_project_monthly_report_view,
        name="create_project_monthly_report",
    ),
    path(
        "project/<str:project>/monthly_progress/<str:report>/update/",
        report_views.update_project_monthly_report_view,
        name="update_project_monthly_report",
    ),
    path(
        "project/monthly_progress/<str:report>/copy/",
        report_views.copy_project_monthly_report_view,
        name="copy_project_monthly_report",
    ),
    path(
        "project/monthly_progress/<str:report>/delete/",
        report_views.delete_project_monthly_report_view,
        name="delete_project_monthly_report",
    ),
    path(
        "project/monthly_progress/<str:report>/archive/",
        report_views.archive_project_monthly_report_view,
        name="archive_project_monthly_report",
    ),
    path(
        "project/monthly_progress/<str:report>/unarchive/",
        report_views.unarchive_project_monthly_report_view,
        name="unarchive_project_monthly_report",
    ),
    path(
        "project/monthly_progress/submit_report/<str:report>/",
        report_views.submit_monthly_report_view,
        name="submit_monthly_report",
    ),
    path(
        "project/monthly_progress/approve_report/<str:report>/",
        report_views.approve_monthly_report_view,
        name="approve_monthly_report",
    ),
    path(
        "project/monthly_progress/reject_report/<str:report>/",
        report_views.reject_monthly_report_view,
        name="reject_monthly_report",
    ),
    # Activity Plan Report URLS
    path(
        "project/<str:project>/monthly_progress/<str:report>/report-activity-plans/view",
        plan_views.list_report_activity_plans,
        name="list_report_activity_plans",
    ),
    path(
        "project/<str:project>/monthly_progress/<str:report>/create",
        plan_views.create_report_activity_plan,
        name="create_report_activity_plan",
    ),
    path(
        "project/<str:project>/monthly_progress/<str:report>/report-activity-plan/<str:plan>/update",
        plan_views.update_report_activity_plan,
        name="update_report_activity_plans",
    ),
    path(
        "project/monthly_progress/report-activity-plan/delete/<str:plan_report>/",
        plan_views.delete_report_activity_plan,
        name="update_report_activity_plans",
    ),
    path(
        "ajax/get_activity_details_fields_data/",
        plan_views.get_activity_details_fields_data,
        name="ajax-get-activity-details-auto-fields",
    ),
    # Location Report URLS
    path(
        "project/<str:project>/monthly_progress/<str:report>/report-plan/<str:plan>/report-target-locations/create",
        location_views.create_report_target_locations,
        name="create_report_target_locations",
    ),
    path(
        "project/<str:project>/monthly_progress/<str:report>/report-target-locations/view",
        location_views.list_report_target_locations,
        name="list_report_target_locations",
    ),
    path(
        "project/<str:project>/monthly_progress/<str:report>/report_plan/<str:plan>/report-target-locations/view",
        location_views.list_report_target_locations,
        name="list_report_target_locations_with_plan",
    ),
    path(
        "project/<str:project>/monthly_progress/<str:report>/report_plan/<str:plan>/report-target-locations/<str:location>/update",
        location_views.update_report_target_locations,
        name="update_report_target_locations",
    ),
    path(
        "ajax/get_target_location_auto_fields/",
        location_views.get_target_location_auto_fields,
        name="ajax-get-target-location-auto-fields",
    ),
    path(
        "project/monthly_progress/location_report/delete/<str:location_report>/",
        location_views.delete_location_report_view,
        name="delete_location_report",
    ),
    # Exports
    path(
        "project/monthly_progress/export/<str:report>/",
        export_report_activities_import_template,
        name="export_monthly_report_template",
    ),
    path(
        "monthly_progress/import-report-activities/<str:pk>", import_report_activities, name="import-report-activities"
    ),
    # Dashboard Paths
    path(
        "projects/monthly_reports/dashboard/",
        dashboard_views.reports_dashboard_view,
        name="view_my_dashboard",
    ),
    path(
        "export/all/monthly_progress_reports/",
        export_views.ReportsExportView.as_view(),
        name="export_all_reports",
    ),
    path(
        "cluster_powerbi_report/",
        fetch_powerbi_report_view.fetch_cluster_report,
        name="fetch_cluster_powerbi_report",
    ),
]
