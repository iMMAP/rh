from django.urls import path

from . import views as user_views

urlpatterns = [
    path('', user_views.index, name='index'),
    path('home', user_views.home, name='home'),


]
