from django.urls import path

from . import dashboards as dashboard_views
from . import exports as export_views
from . import views as user_views

urlpatterns = [
    # Projects CRUD
    path(
        "project/monthly_progress/?project=<str:project>/",
        user_views.index_project_report_view,
        name="project_reports_home",
    ),
    path(
        "project/monthly_progress/view/<str:project>/<str:report>/",
        user_views.details_monthly_progress_view,
        name="view_monthly_report",
    ),
    path(
        "project/monthly_progress/create/<str:project>/",
        user_views.create_project_monthly_report_view,
        name="create_project_monthly_report",
    ),
    path(
        "project/monthly_progress/copy/<str:report>/",
        user_views.copy_project_monthly_report_view,
        name="copy_project_monthly_report",
    ),
    path(
        "project/monthly_progress/delete/<str:report>/",
        user_views.delete_project_monthly_report_view,
        name="delete_project_monthly_report",
    ),
    path(
        "project/monthly_progress/archive/<str:report>/",
        user_views.archive_project_monthly_report_view,
        name="archive_project_monthly_report",
    ),
    path(
        "project/monthly_progress/unarchive/<str:report>/",
        user_views.unarchive_project_monthly_report_view,
        name="unarchive_project_monthly_report",
    ),
    path(
        "project/monthly_progress/create_progress/<str:project>/<str:report>/",
        user_views.create_project_monthly_report_progress_view,
        name="create_project_monthly_report_progress",
    ),
    path(
        "project/monthly_progress/update_progress/<str:project>/<str:report>/",
        user_views.update_project_monthly_report_progress_view,
        name="update_project_monthly_report_progress",
    ),
    path(
        "project/monthly_progress/location_report/delete/<str:location_report>/",
        user_views.delete_location_report_view,
        name="delete_location_report",
    ),
    path(
        "project/monthly_progress/submit_report/<str:report>/",
        user_views.submit_monthly_report_view,
        name="submit_monthly_report",
    ),
    path(
        "project/monthly_progress/approve_report/<str:report>/",
        user_views.approve_monthly_report_view,
        name="approve_monthly_report",
    ),
    path(
        "project/monthly_progress/reject_report/<str:report>/",
        user_views.reject_monthly_report_view,
        name="reject_monthly_report",
    ),
    # # Projects Activity Plannings CRUD
    # path(
    #     "project/activity_plan/create/?project=<str:project>/",
    #     user_views.create_project_activity_plan,
    #     name="create_project_activity_plan",
    # ),
    # path(
    #     "project/target_location/copy/<str:project>/<str:location>/",
    #     user_views.copy_target_location,
    #     name="copy_location",
    # ),
    # path(
    #     "project/target_location/delete/<str:pk>/",
    #     user_views.delete_target_location,
    #     name="delete_location",
    # ),
    # path(
    #     "project/project_plan/submit/<str:pk>/",
    #     user_views.submit_project,
    #     name="project_submit",
    # ),
    # # Ajax for data load
    # path(
    #     "ajax/load-activity_domains/",
    #     user_views.load_activity_domains,
    #     name="ajax-load-activity_domains",
    # ),
    # path(
    #     "ajax/load-locations-details/",
    #     user_views.load_locations_details,
    #     name="ajax-load-locations",
    # ),
    # path(
    #     "ajax/load-facility_sites/",
    #     user_views.load_facility_sites,
    #     name="ajax-load-facility_sites",
    # ),
    # Exports
    path(
        "project/monthly_progress/export/<str:report>/",
        export_views.ReportTemplateExportView.as_view(),
        name="export_monthly_report_template",
    ),
    path(
        "project/monthly_progress/import/<str:report>/",
        user_views.import_monthly_reports,
        name="import_monthly_reports",
    ),
    path(
        "ajax/get_location_report_empty_form/",
        user_views.get_location_report_empty_form,
        name="get_location_report_empty_form",
    ),
    path(
        "ajax/get_target_location_auto_fields/",
        user_views.get_target_location_auto_fields,
        name="ajax-get-target-location-auto-fields",
    ),
    path(
        "ajax/load-target-locations-details/",
        user_views.load_target_locations_details,
        name="ajax-load-target-locations",
    ),
    path(
        "ajax/get_disaggregations_report_forms/",
        user_views.get_disaggregations_report_empty_forms,
        name="get_disaggregations_report_empty_forms",
    ),
    # path(
    #     "ajax/get_indicator_reference/",
    #     user_views.get_indicator_reference,
    #     name="get_indicator_reference",
    # ),
    path(
        "project/monthly_progress/?project=<str:project>/",
        user_views.index_project_report_view,
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
