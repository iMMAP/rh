from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('add_project/', views.add_project, name='add_project'),
]