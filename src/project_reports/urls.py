from django.urls import path

from . import dashboards as dashboard_views
from . import exports as export_views
from .views import (
    monthly_reports as report_views,
)
from .views import (
    report_activity_plans as plan_views,
)
from .views import (
    report_target_locations as location_views,
)
from .views.views import (
    export_report_activities_import_template,
    import_report_activities,
)

urlpatterns = [
    # Monthly Report URLS
    path(
        "project/<str:project>/reports",
        report_views.index_project_report_view,
        name="project_reports_home",
    ),
    path(
        "project/<str:project>/monthly-progress/<str:report>/view",
        report_views.details_monthly_progress_view,
        name="view_monthly_report",
    ),
    path(
        "project/<str:project>/monthly-progress/create",
        report_views.create_project_monthly_report_view,
        name="create_project_monthly_report",
    ),
    path(
        "project/<str:project>/monthly-progress/<str:report>/update",
        report_views.update_project_monthly_report_view,
        name="update_project_monthly_report",
    ),
    path(
        "project/monthly-progress/<str:report>/copy",
        report_views.copy_project_monthly_report_view,
        name="copy_project_monthly_report",
    ),
    # download last month activity report
    path(
        "project/monthly-progress/<str:report>/download",
        report_views.download_project_monthly_report_view,
        name="download_project_monthly_report",
    ),
    path(
        "project/monthly-progress/<str:report>/delete",
        report_views.delete_project_monthly_report_view,
        name="delete_project_monthly_report",
    ),
    path(
        "project/monthly-progress/<str:report>/archive",
        report_views.archive_project_monthly_report_view,
        name="archive_project_monthly_report",
    ),
    path(
        "project/monthly-progress/<str:report>/unarchive",
        report_views.unarchive_project_monthly_report_view,
        name="unarchive_project_monthly_report",
    ),
    path(
        "project/monthly-progress/submit-report/<str:report>",
        report_views.submit_monthly_report_view,
        name="submit_monthly_report",
    ),
    path(
        "project/monthly-progress/approve-report/<str:report>",
        report_views.approve_monthly_report_view,
        name="approve_monthly_report",
    ),
    path(
        "project/monthly-progress/reject-report/<str:report>",
        report_views.reject_monthly_report_view,
        name="reject_monthly_report",
    ),
    # Activity Plan Report URLS
    path(
        "project/<str:project>/monthly-progress/<str:report>/create",
        plan_views.create_report_activity_plan,
        name="create_report_activity_plan",
    ),
    path(
        "project/<str:project>/monthly-progress/<str:report>/report-activity-plan/<str:plan>/update",
        plan_views.update_report_activity_plan,
        name="update_report_activity_plans",
    ),
    path(
        "project/monthly-progress/report-activity-plan/delete/<str:plan_report>",
        plan_views.delete_report_activity_plan,
        name="delete_report_activity_plan",
    ),
    path(
        "hx/activity-plans/info",
        plan_views.hx_activity_plan_info,
        name="hx-acitivity-plans-info",
    ),
    # Location Report URLS
    path(
        "report-target-locations/activity-plan-report/<int:plan>/create",
        location_views.create_report_target_location,
        name="create_report_target_location",
    ),
    path(
        "project/<str:project>/monthly-progress/<str:report>/report-target-locations",
        location_views.list_report_target_locations,
        name="list_report_target_locations",
    ),
    path(
        "project/<str:project>/monthly-progress/<str:report>/report_plan/<str:plan>/report-target-locations/<str:location>/update",
        location_views.update_report_target_locations,
        name="update_report_target_locations",
    ),
    path(
        "hx/target-locations/info",
        location_views.hx_target_location_info,
        name="hx_target_location_info",
    ),
    path(
        "project/monthly-progress/location_report/delete/<str:location_report>",
        location_views.delete_location_report_view,
        name="delete_location_report",
    ),
    # Exports
    path(
        "project/monthly-progress/export/<str:report>",
        export_report_activities_import_template,
        name="export_monthly_report_template",
    ),
    path(
        "monthly_progress/import-report-activities/<str:pk>", import_report_activities, name="import-report-activities"
    ),
    # Dashboard Paths
    path(
        "projects/monthly-reports/dashboard",
        dashboard_views.reports_dashboard_view,
        name="view_my_dashboard",
    ),
    path(
        "export/all/monthly_progress_reports",
        export_views.export_all_monthly_reports_view,
        name="export_all_reports",
    ),
    path(
        "project/monthly-report/export/<int:pk>",
        export_views.export_monthly_report_view,
        name="export_monthly_report",
    ),
]
