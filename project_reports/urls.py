from django.urls import path

from . import views as user_views

urlpatterns = [
    # Projects CRUD
    path('project/monthly_progress/?project=<str:project>/',
        user_views.index_project_report_view, name='project_reports_home'),
    path('project/monthly_progress/create/', user_views.create_project_report_view, name='create_project_report'),

    # path('project/view_project/<str:pk>/', user_views.open_project_view, name='view_project'),

    # # Projects Activity Plannings CRUD
    # path('project/activity_plan/create/?project=<str:project>/', user_views.create_project_activity_plan,
    #     name='create_project_activity_plan'),

    # path('project/target_location/copy/<str:project>/<str:location>/', user_views.copy_target_location, name='copy_location'),
    # path('project/target_location/delete/<str:pk>/', user_views.delete_target_location, name='delete_location'),

    # path('project/project_plan/submit/<str:pk>/', user_views.submit_project, name='project_submit'),

    # path('ajax/load-locations-details/', user_views.load_locations_details, name='ajax-load-locations'),
    # path('ajax/load-facility_sites/', user_views.load_facility_sites, name='ajax-load-facility_sites'),

    # path('ajax/get_target_location_empty_form/', user_views.get_target_location_empty_form, name='get_target_location_empty_form'),
    # path('ajax/get_activity_empty_form/', user_views.get_activity_empty_form, name='get_activity_empty_form'),
    # path('ajax/get_disaggregations_forms/', user_views.get_disaggregations_forms, name='get_disaggregations_forms'),

]
