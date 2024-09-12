from django.urls import path

from . import views

urlpatterns = [
    path("docs/", views.index, name="docs"),
    path("docs/<slug:guide>", views.guide_detail, name="guides-detail"),
    path("docs/<slug:guide>/feeback", views.feedback, name="guides-feedback"),
]
