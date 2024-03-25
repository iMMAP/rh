from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.META.get('PATH_INFO', "")

        if not settings.MAINTENANCE_MODE_ENABLED: 
            if path == reverse("maintenance"): 
                # Do not load maintenance page if maintenance mode is not enabled
                return redirect("/")

           # Continue normally
            return  self.get_response(request)

        if path == reverse("maintenance"):
            return  self.get_response(request)

        if settings.MAINTENANCE_MODE_IGNORE_SUPERUSER and request.user.is_superuser:
            return self.get_response(request)

        if settings.MAINTENANCE_MODE_IGNORE_STAFF and request.user.is_staff:
           return  self.get_response(request)

        query = request.META.get('QUERY_STRING', "")
        if settings.MAINTENANCE_BYPASS_QUERY in query:
            request.session['bypass_maintenance']=True

        if request.session.get('bypass_maintenance', False):
            # Bypass the maintenance mode: continue normally bypass is correct
           return  self.get_response(request)

        redirect_to_url = settings.MAINTENANCE_MODE_REDIRECT_ROUTE
        return redirect(reverse(redirect_to_url))