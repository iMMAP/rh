RECORDS_PER_PAGE = 3

from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.forms import modelformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.views.decorators.cache import cache_control
from django.db.models import Q

from .filters import *
from .forms import *
from reports.models import ActivityReport


# TODO: Add is_safe_url to redirects
# from django.utils.http import is_safe_url


#############################################
############### Index Views #################
#############################################


@cache_control(no_store=True)
def index(request):
    template = loader.get_template('index.html')

    users_count = User.objects.all().count()
    locations_count = Location.objects.all().count()
    reports_count = ActivityReport.objects.all().count()
    context = {
        'users': users_count,
        'locations': locations_count,
        'reports': reports_count
    }
    return HttpResponse(template.render(context, request))


@cache_control(no_store=True)
@login_required
def home(request):
    template = loader.get_template('home.html')

    users_count = User.objects.all().count()
    locations_count = Location.objects.all().count()
    reports_count = ActivityReport.objects.all().count()
    context = {
        'users': users_count,
        'locations': locations_count,
        'reports': reports_count
    }
    return HttpResponse(template.render(context, request))

