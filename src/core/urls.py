from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

admin.site.site_header = "ReportHub Admin"
admin.site.site_title = settings.APP_NAME

urlpatterns = [
    path("", include("rh.urls")),
    path("", include("stock.urls")),
    path("", include("users.urls")),
    path("", include("project_reports.urls")),
    path("admin/", admin.site.urls),
    path("chaining/", include("smart_selects.urls")),
    path("maintenance/", TemplateView.as_view(template_name="maintenance.html"), name="maintenance"),
    path("", include("django_vite_plugin.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
