from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "ReportHub Admin"

urlpatterns = [
    path("", include("rh.urls")),
    path("", include("stock.urls")),
    path("", include("users.urls")),
    path("", include("project_reports.urls")),
    path("", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("chaining/", include("smart_selects.urls")),
    path("", include("django_vite_plugin.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
]
