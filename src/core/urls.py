from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

admin.site.site_header = f"{settings.APP_NAME} Admin"
admin.site.site_title = settings.APP_NAME

urlpatterns = [
    path("", include("rh.urls")),
    path("", include("stock.urls")),
    path("", include("users.urls")),
    path("", include("project_reports.urls")),
    path("", include("guides.urls")),
    path("maintenance/", TemplateView.as_view(template_name="maintenance.html"), name="maintenance"),
    path("admin/", admin.site.urls),
    path("chaining/", include("smart_selects.urls")),
    path(r"mdeditor/", include("mdeditor.urls")),
    path("", include("django_vite_plugin.urls")),
]

if settings.DEBUG or not settings.TESTING:
    urlpatterns = [
        *urlpatterns,
        path("__debug__/", include("debug_toolbar.urls")),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
