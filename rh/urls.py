from django.urls import path

from . import views as user_views

urlpatterns = [
    path('', user_views.index, name='index'),
    path('home', user_views.home, name='home'),

    # Projects routes
    path('projects/draft/', user_views.draft_projects_view, name='draft_projects'),
    path('projects/active/', user_views.active_projects_view, name='active_projects'),
    path('projects/completed/', user_views.completed_projects_view, name='completed_projects'),
    path('project/create/', user_views.create_project_view, name='create_project'),
    path('project/project_plan/<str:pk>/', user_views.update_project_view, name='update_project'),
#     path('project/project_plan/view_complete/<str:pk>/', user_views.completed_project_view, name='completed_project'),
    path('project/view_project/<str:pk>/', user_views.open_project_view, name='view_project'),

    path('project/activity_plan/create/?project=<str:project>/', user_views.create_project_activity_plan,
         name='create_project_activity_plan'),

    path('project/target_location/create/?project=<str:project>/',
         user_views.create_project_target_location, name='create_project_target_location'),

    path('project/project_plan/review/?project=<str:project>/', user_views.project_planning_review, name='project_plan_review'),
    path('project/project_plan/submit/<str:pk>/', user_views.submit_project, name='project_submit'),

    path('project/project_plan/delete/<str:pk>/', user_views.delete_project, name='delete_project'),
    path('project/project_plan/copy/<str:pk>/', user_views.copy_project, name='copy_project'),

    path('ajax/load-districts-details/', user_views.load_locations_details, name='ajax-load-districts'),
    path('ajax/load-facility_sites/', user_views.load_facility_sites, name='ajax-load-facility_sites'),


]
