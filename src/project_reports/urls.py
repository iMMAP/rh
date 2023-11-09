from django.urls import path

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
        "project/monthly_progress/create_progress/<str:project>/<str:report>/",
        user_views.create_project_monthly_report_progress_view,
        name="create_project_monthly_report_progress",
    ),
    path(
        "project/monthly_progress/update_progress/<str:project>/<str:report>/",
        user_views.update_project_monthly_report_progress_view,
        name="update_project_monthly_report_progress",
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
    path(
        "ajax/get_location_report_empty_form/",
        user_views.get_location_report_empty_form,
        name="get_location_report_empty_form",
    ),
    path(
        "ajax/get_disaggregations_report_forms/",
        user_views.get_disaggregations_report_empty_forms,
        name="get_disaggregations_report_empty_forms",
    ),
]
