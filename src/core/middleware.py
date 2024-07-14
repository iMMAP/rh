from django.shortcuts import redirect
from django.urls import reverse

from django.contrib.messages import get_messages
from django.template.loader import render_to_string
from django.utils.deprecation import MiddlewareMixin
from extra_settings.models import Setting


class HtmxMessageMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if (
            "HX-Request" in request.headers
            and not 300 <= response.status_code < 400
            and "HX-Redirect" not in response.headers
        ):
            response.write(
                render_to_string(
                    "components/messages.html",
                    {"messages": get_messages(request)},
                )
            )
        return response


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.META.get("PATH_INFO", "")

        if not Setting.get("MAINTENANCE_MODE_ENABLED", default=False):
            if path == reverse("maintenance"):
                # Do not load maintenance page if maintenance mode is not enabled
                return redirect("/")

            # Continue normally
            return self.get_response(request)

        if path == reverse("maintenance"):
            return self.get_response(request)

        if Setting.get("MAINTENANCE_MODE_IGNORE_SUPERUSER", default=True) and request.user.is_superuser:
            return self.get_response(request)

        if Setting.get("MAINTENANCE_MODE_IGNORE_STAFF", default=True) and request.user.is_staff:
            return self.get_response(request)

        query = request.META.get("QUERY_STRING", "")
        if Setting.get("MAINTENANCE_BYPASS_QUERY", default="godmode") in query:
            request.session["bypass_maintenance"] = True

        if request.session.get("bypass_maintenance", False):
            # Bypass the maintenance mode: continue normally bypass is correct
            return self.get_response(request)

        redirect_to_url = Setting.get("MAINTENANCE_MODE_REDIRECT_ROUTE", default="maintenance")
        return redirect(reverse(redirect_to_url))
