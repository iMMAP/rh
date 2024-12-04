import json

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Count, Prefetch
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from project_reports.models import ProjectMonthlyReport
from users.decorators import unauthenticated_user

from ..models import ActivityDomain, ActivityType, Cluster, Indicator, Location, Project


@login_required
def home(request):
    user_org = request.user.profile.organization

    active_p_cache_key = f"home_active_p_{user_org.code}"
    active_projects = cache.get(active_p_cache_key)
    if active_projects is None:
        active_projects = (
            Project.objects.filter(state="in-progress")
            .filter(organization=user_org)
            .values("id", "title", "code", "end_date")
            .order_by("-updated_at")[:8]
        )
        cache.set(active_p_cache_key, active_projects, timeout=60 * 60)  # Cache for 1 hour

    pending_reports = (
        ProjectMonthlyReport.objects.filter(
            state="pending", project__organization=user_org, project__state="in-progress"
        )
        .select_related("project", "project__user")
        .values(
            "id", "state", "from_date", "project_id", "project__code", "project__user__id", "project__user__username"
        )
        .distinct()
    )

    counts_cache_key = f"home_projects_counts_{user_org.code}"
    projects_counts = cache.get(counts_cache_key)
    if projects_counts is None:
        projects_counts = (
            Project.objects.filter(state="in-progress")
            .filter(organization=user_org)
            .aggregate(
                implementing_partners_count=Count("implementing_partners", distinct=True),
                activity_plans_count=Count("activityplan", distinct=True),
                target_locations_count=Count("targetlocation__province", distinct=True),
            )
        )
        cache.set(counts_cache_key, projects_counts, timeout=60 * 60)  # Cache for 1 hour

    projects_counts["pending_reports_count"] = pending_reports.count()

    context = {"active_projects": active_projects, "counts": projects_counts, "pending_reports": pending_reports}

    return render(request, "home.html", context)


@unauthenticated_user
@cache_page(60 * 60 * 4)  # 4 hour
def landing_page(request):
    context = {"users": 0, "locations": 0, "reports": 0}

    return render(request, "landing.html", context)


@login_required
def get_locations_details(request):
    parents = Location.objects.filter(pk=list(request.GET.values())[0]).select_related("parent")
    return render(request, "rh/target_locations/_location_select_options.html", {"parents": parents})


@login_required
def get_activity_domain_types(request):
    """
    View to return activity types for a given activity domain for HTMX response.
    Route: /activity-domains/activity-types
    """
    activity_domain_pk = request.GET.get("activity_domain")

    if activity_domain_pk:
        activity_types = ActivityType.objects.filter(activity_domain=activity_domain_pk).order_by("name")
    else:
        activity_types = ActivityType.objects.none()

    return render(request, "rh/activity_plans/_select_options.html", {"options": activity_types})


@login_required
def get_activity_type_indicators(request):
    """
    View to return activity details for a given activity types for HTMX response.
    Route: /activity-types/indicators
    """
    activity_type_pk = request.GET.get("activity_type")

    if activity_type_pk:
        indicators = Indicator.objects.filter(activity_types=activity_type_pk).order_by("name")
    else:
        indicators = Indicator.objects.none()

    return render(request, "rh/activity_plans/_select_options.html", {"options": indicators})


@login_required
def load_activity_domains(request):
    """
    Used in project form
    """
    data = json.loads(request.body)
    cluster_ids = data.get("clusters", [])
    # listed_domains = data.get("listed_domains", [])

    user_location = request.user.profile.country
    # Define a Prefetch object to optimize the related activitydomain_set
    prefetch_activitydomain = Prefetch(
        "activitydomain_set",
        queryset=ActivityDomain.objects.filter(countries=user_location).order_by("name"),
    )

    clusters = Cluster.objects.filter(pk__in=cluster_ids).prefetch_related(prefetch_activitydomain)

    clusters = [
        {
            "label": cluster.title,
            "id": cluster.code,
            "choices": [
                {
                    "value": domain.pk,
                    "label": domain.name,
                    "customProperties": {
                        "clusterId": cluster.id,
                    },
                }
                for domain in cluster.activitydomain_set.all()
            ],
        }
        for cluster in clusters
    ]

    return JsonResponse(clusters, safe=False)


@login_required
def load_facility_sites(request):
    # FIXME: Fix the long url, by post request?
    cluster_ids = [int(i) for i in request.GET.getlist("clusters[]") if i]
    clusters = Cluster.objects.filter(pk__in=cluster_ids)

    response = "".join(
        [
            f'<optgroup label="{cluster.title}">'
            + "".join(
                [
                    f'<option value="{facility.pk}">{facility}</option>'
                    for facility in cluster.facilitysitetype_set.order_by("name")
                ]
            )
            + "</optgroup>"
            for cluster in clusters
        ]
    )

    return JsonResponse(response, safe=False)
