from django.urls import path

from . import dashboards as dashboard_views
from . import exports as export_views
from .views.views import (
    import_monthly_reports,
)
from .views import (
    report_activity_plans as plan_views,
    report_target_locations as location_views,
    monthly_reports as report_views,
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
        "project/monthly-progress/submit_report/<str:report>",
        report_views.submit_monthly_report_view,
        name="submit_monthly_report",
    ),
    path(
        "project/monthly-progress/approve_report/<str:report>",
        report_views.approve_monthly_report_view,
        name="approve_monthly_report",
    ),
    path(
        "project/monthly-progress/reject_report/<str:report>",
        report_views.reject_monthly_report_view,
        name="reject_monthly_report",
    ),
    # Activity Plan Report URLS
    path(
        "project/report-activity-plan/<int:report_ap>/update",
        plan_views.update_report_activity_plan,
        name="update_report_activity_plan",
    ),
    path(
        "project/monthly-progress/<str:report>/report-activity-plan",
        plan_views.report_activity_plans,
        name="report_activity_plans",
    ),
    path(
        "project/monthly-progress/<str:report>/report-activity-plan/<int:report_ap>/update",
        plan_views.update_report_activity_plans,
        name="update_report_activity_plans",
    ),
    path(
        "project/<str:report>/report-activity-plan/create",
        plan_views.create_report_activity_plan,
        name="create_report_activity_plan",
    ),
    path(
        "project/monthly-progress/<int:ap_report>/report-activity-plan/delete",
        plan_views.delete_report_activity_plan,
        name="delete_report_activity_plan",
    ),
    # Location Report URLS
    path(
        "project/report-plan/<str:plan>/report-target-locations/create",
        location_views.create_report_target_locations,
        name="create_report_target_locations",
    ),
    # path(
    #     "project/<str:project>/monthly-progress/<str:report>/report-target-locations/view",
    #     location_views.list_report_target_locations,
    #     name="list_report_target_locations",
    # ),
    # path(
    #     "project/<str:project>/monthly-progress/<str:report>/report_plan/<str:plan>/report-target-locations/view",
    #     location_views.list_report_target_locations,
    #     name="list_report_target_locations_with_plan",
    # ),
    path(
        "project/<str:project>/monthly-progress/<str:report>/report_plan/<str:plan>/report-target-locations/<str:location>/update",
        location_views.update_report_target_locations,
        name="update_report_target_locations",
    ),
    path(
        "ajax/get_target_location_auto_fields/",
        location_views.get_target_location_auto_fields,
        name="ajax-get-target-location-auto-fields",
    ),
    path(
        "project/monthly-progress/location_report/delete/<str:location_report>/",
        location_views.delete_location_report_view,
        name="delete_location_report",
    ),
    # Exports
    path(
        "project/monthly-progress/export/<str:report>/",
        export_views.ReportTemplateExportView.as_view(),
        name="export_monthly_report_template",
    ),
    path(
        "project/monthly-progress/import/<str:report>/",
        import_monthly_reports,
        name="import_monthly_reports",
    ),
    # Dashboard Paths
    path(
        "projects/monthly_reports/dashboard/",
        dashboard_views.reports_dashboard_view,
        name="view_my_dashboard",
    ),
    path(
        "export/all/monthly-progress_reports/",
        export_views.ReportsExportView.as_view(),
        name="export_all_reports",
    ),
]
