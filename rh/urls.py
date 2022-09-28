from django.urls import path
from django.contrib.auth import views as auth_views

from .forms import UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm
from . import views as user_views

urlpatterns = [
     path('', user_views.index, name='index'),

     path('register/', user_views.register_view, name='register'),
     path('activate/<uidb64>/<token>', user_views.activate_account, name='activate_account'),
     path('login/', user_views.login_view, name='login'),
     path('logout/', user_views.logout_view, name='logout'),

     # Password change routes
     path('password_change/',
          auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html', form_class=UserPasswordChangeForm),
          name='password_change'),
     path('password_change/done/',
          auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'),
          name='password_change_done'),

     # Password reset routes
     path('password_reset/',
          auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html', form_class=UserPasswordResetForm),
          name='password_reset'),
     path('password_reset/done/',
          auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
          name='password_reset_done'),
     path('reset/<uidb64>/<token>/',
          auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html', form_class=UserSetPasswordForm),
          name='password_reset_confirm'),
     path('reset/done/',
          auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
          name='password_reset_complete'),

     # Profile routes
     path('profile/', user_views.profile, name='profile'),

     # Activities routes
     path('activity_plans/', user_views.activity_plans, name='activity_plan'),
     path('activity_plan/create/', user_views.create_activity_plan, name='create_activity_plan'),
     path('activity_plan/update/<str:pk>/', user_views.update_activity_plan, name='update_activity_plan'),
     path('ajax/activity_plan/activity_form/', user_views.load_activity_json_form, name='ajax-load-activityfields'),

     # Projects routes
     path('projects/', user_views.projects_view, name='projects'),
     path('project/create/', user_views.create_project_view, name='create_project'),
     path('project/update/<str:pk>/', user_views.update_project_view, name='update_project'),
     path('ajax/load-activities-details/', user_views.load_activities_details, name='ajax-load-activities'),
     path('ajax/load-locations-details/', user_views.load_locations_details, name='ajax-load-locations'),
]
