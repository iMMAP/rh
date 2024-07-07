from django.urls import path

from . import dashboards as dashboard_views
from . import exports as export_views
from .views.views import (
    delete_location_report_view,
    import_monthly_reports,
    # get_location_report_empty_form,
    load_target_locations_details,
    get_disaggregations_report_empty_forms,
)
from .views import (
    report_activity_plans as plan_views,
    report_target_locations as location_views,
    monthly_reports as report_views,
)

urlpatterns = [
    # Projects CRUD
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
        "project/<str:project>/monthly_progress/<str:report>/report-activity-plans/view",
        plan_views.list_report_activity_plans,
        name="list_report_activity_plans",
    ),
    path(
        "project/<str:project>/monthly_progress/<str:report>/report-activity-plan/<str:plan>/update",
        plan_views.update_report_activity_plan,
        name="update_report_activity_plans",
    ),
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
        "project/monthly_progress/location_report/delete/<str:location_report>/",
        delete_location_report_view,
        name="delete_location_report",
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
    # Exports
    path(
        "project/monthly_progress/export/<str:report>/",
        export_views.ReportTemplateExportView.as_view(),
        name="export_monthly_report_template",
    ),
    path(
        "project/monthly_progress/import/<str:report>/",
        import_monthly_reports,
        name="import_monthly_reports",
    ),
    # path(
    #     "ajax/get_location_report_empty_form/",
    #     get_location_report_empty_form,
    #     name="get_location_report_empty_form",
    # ),
    path(
        "ajax/get_target_location_auto_fields/",
        location_views.get_target_location_auto_fields,
        name="ajax-get-target-location-auto-fields",
    ),
    path(
        "ajax/load-target-locations-details/",
        load_target_locations_details,
        name="ajax-load-target-locations",
    ),
    path(
        "ajax/get_disaggregations_report_forms/",
        get_disaggregations_report_empty_forms,
        name="get_disaggregations_report_empty_forms",
    ),
    # path(
    #     "ajax/get_indicator_reference/",
    #     get_indicator_reference,
    #     name="get_indicator_reference",
    # ),
    path(
        "project/<str:project>/monthly_progress/",
        report_views.index_project_report_view,
        name="project_reports_home",
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
]
