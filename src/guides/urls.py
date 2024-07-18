from django.urls import path
from . import views

urlpatterns = [
    path("docs/<str:guide>", views.guide_detail, name="guides-detail"),
    path("docs/", views.index, name="docs"),
]
