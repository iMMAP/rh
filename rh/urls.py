from django.urls import path
from . import views as user_views

urlpatterns = [
     path('', user_views.index, name='index'),
     path('home', user_views.home, name='home'),

     # Activities routes
     path('activity_plans/', user_views.activity_plans, name='activity_plan'),
     path('activity_plan/create/', user_views.create_activity_plan, name='create_activity_plan'),
     path('activity_plan/update/<str:pk>/', user_views.update_activity_plan, name='update_activity_plan'),
     path('ajax/activity_plan/activity_form/', user_views.load_activity_json_form, name='ajax-load-activityfields'),

     # Projects routes
     path('projects/', user_views.projects_view, name='projects'),
     path('project/view/<str:pk>/', user_views.completed_project_view, name='view_project'),
     path('project/create/', user_views.create_project_view, name='create_project'),
     path('project/update/<str:pk>/', user_views.update_project_view, name='update_project'),

     path('project/activity_plan/create/?project=<str:project>/', user_views.create_project_activity_plan, name='create_project_activity_plan'),
     path('project/activity_plan/update/?project=<str:project>/', user_views.update_project_activity_plan, name='update_project_activity_plan'),

     path('project/target_location/create/?project=<str:project>/?activity_plans=<str:plans>/', user_views.create_project_target_location, name='create_project_target_location'),
     path('project/target_location/update/?project=<str:project>/?activity_plans=<str:plans>/', user_views.update_project_target_location, name='update_project_target_location'),
     
     path('project/project_plan/review/?project=<str:project>/?activity_plans=<str:plans>/?target_locations=<str:locations>/', user_views.project_planning_review, name='project_plan_review'),
     
     path('project/project_plan/submit/<str:pk>/', user_views.submit_project, name='project_submit'),
     
     path('project/project_plan/delete/<str:pk>/', user_views.delete_project, name='delete_project'),
     path('project/project_plan/copy/<str:pk>/', user_views.copy_project, name='copy_project'),

     path('ajax/load-activities-details/', user_views.load_activities_details, name='ajax-load-activities'),
     path('ajax/load-locations-details/', user_views.load_locations_details, name='ajax-load-locations'),

]
