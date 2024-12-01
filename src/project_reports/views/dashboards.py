import datetime

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, render

from project_reports.models import ProjectMonthlyReport
from rh.models import Cluster, Organization
from rh.utils import is_cluster_lead


@login_required
def cluster_5w_dashboard(request, cluster):
    cluster = get_object_or_404(Cluster, code=cluster)

    if not is_cluster_lead(
        user=request.user,
        clusters=[
            cluster.code,
        ],
    ):
        raise PermissionDenied

    user_country = request.user.profile.country

    from_date = request.GET.get("from")
    if not from_date:
        from_date = datetime.date(datetime.datetime.now().year, 1, 1)

    to_date = request.GET.get("to")
    if not to_date:
        to_date = datetime.datetime.now().date()

    organization = request.GET.get("organization", None)

    filter_params = {
        "project__clusters__in": [cluster],
        "state__in": ["submited", "completed"],
        "from_date__lte": to_date,
        "to_date__gte": from_date,
        "project__user__profile__country": user_country,
        "activityplanreport__activity_plan__activity_domain__clusters__in": [cluster],
    }

    if organization:
        filter_params["project__organization__code"] = organization

    counts = ProjectMonthlyReport.objects.filter(**filter_params).aggregate(
        report_indicators_count=Count("activityplanreport__activity_plan__indicator", distinct=True),
        report_implementing_partners_count=Count(
            "activityplanreport__targetlocationreport__target_location__implementing_partner", distinct=True
        ),
        report_target_location_province_count=Count(
            "activityplanreport__targetlocationreport__target_location__province", distinct=True
        ),
    )

    people_reached_data = (
        ProjectMonthlyReport.objects.filter(**filter_params, activityplanreport__beneficiary_status="new_beneficiary")
        .order_by("from_date")
        .values("from_date")
        .annotate(
            total_people_reached=Sum("activityplanreport__targetlocationreport__disaggregationlocationreport__reached")
        )
    )

    counts["people_reached"] = sum(report["total_people_reached"] for report in people_reached_data)

    labels = [report["from_date"].strftime("%b") for report in people_reached_data]
    data = [
        report["total_people_reached"] if report["total_people_reached"] is not None else 0
        for report in people_reached_data
    ]

    # people reached by activities
    activity_domains = (
        ProjectMonthlyReport.objects.filter(**filter_params, activityplanreport__beneficiary_status="new_beneficiary")
        .values_list("activityplanreport__activity_plan__activity_domain__name", flat=True)
        .distinct()
    )

    reach_by_activity = (
        ProjectMonthlyReport.objects.filter(**filter_params, activityplanreport__beneficiary_status="new_beneficiary")
        .values(
            "activityplanreport__targetlocationreport__disaggregationlocationreport__disaggregation__name",
            "activityplanreport__activity_plan__activity_domain__name",
        )
        .annotate(
            total_people_reached=Sum("activityplanreport__targetlocationreport__disaggregationlocationreport__reached"),
        )
    )

    # Organize data into a dictionary
    data_dict = {}
    for entry in reach_by_activity:
        disaggregation_name = entry[
            "activityplanreport__targetlocationreport__disaggregationlocationreport__disaggregation__name"
        ]
        activity_domain = entry["activityplanreport__activity_plan__activity_domain__name"]
        total_reached = entry["total_people_reached"]

        if disaggregation_name not in data_dict:
            data_dict[disaggregation_name] = {}

        data_dict[disaggregation_name][activity_domain] = total_reached

    for category, total_reached in data_dict.items():
        if total_reached and all(value is not None for value in total_reached.values()):
            sum_disaggregation = sum(value for value in total_reached.values() if value is not None)
            data_dict[category]["total"] = sum_disaggregation

    context = {
        "cluster": cluster,
        "counts": counts,
        "people_reached_labels": labels,
        "people_reached_data": data,
        "activity_domains": activity_domains,
        "reach_by_activity": data_dict,
    }

    return render(request, "project_reports/cluster_5w_dashboard.html", context)


@login_required
def org_5w_dashboard(request, code):
    org = get_object_or_404(Organization, code=code)

    if not org.code == request.user.profile.organization.code and not is_cluster_lead(
        request.user, org.clusters.values_list("code", flat=True)
    ):
        raise PermissionDenied

    user_org = request.user.profile.organization

    from_date = request.GET.get("from")
    if not from_date:
        from_date = datetime.date(datetime.datetime.now().year, 1, 1)

    to_date = request.GET.get("to")
    if not to_date:
        to_date = datetime.datetime.now().date()

    cluster_code = request.GET.get("cluster")

    filter_params = {
        "project__organization": user_org,
        "state__in": ["submited", "completed"],
        "from_date__lte": to_date,
        "to_date__gte": from_date,
    }

    if cluster_code:
        filter_params["project__clusters__code__in"] = [cluster_code]

    counts = ProjectMonthlyReport.objects.filter(**filter_params).aggregate(
        report_indicators_count=Count("activityplanreport__activity_plan__indicator", distinct=True),
        report_implementing_partners_count=Count(
            "activityplanreport__targetlocationreport__target_location__implementing_partner", distinct=True
        ),
        report_target_location_province_count=Count(
            "activityplanreport__targetlocationreport__target_location__province", distinct=True
        ),
    )

    people_reached_data = (
        ProjectMonthlyReport.objects.filter(
            **filter_params,
            activityplanreport__beneficiary_status="new_beneficiary",
        )
        .order_by("from_date")
        .values("from_date")
        .annotate(
            total_people_reached=Sum("activityplanreport__targetlocationreport__disaggregationlocationreport__reached")
        )
    )

    counts["people_reached"] = sum(report["total_people_reached"] for report in people_reached_data)

    labels = [report["from_date"].strftime("%b") for report in people_reached_data]
    data = [
        report["total_people_reached"] if report["total_people_reached"] is not None else 0
        for report in people_reached_data
    ]

    # people reached by activities
    activity_domains = (
        ProjectMonthlyReport.objects.filter(
            **filter_params,
            activityplanreport__beneficiary_status="new_beneficiary",
        )
        .values_list("activityplanreport__activity_plan__activity_domain__name", flat=True)
        .distinct()
    )

    reach_by_activity = (
        ProjectMonthlyReport.objects.filter(
            **filter_params,
            activityplanreport__beneficiary_status="new_beneficiary",
        )
        .values(
            "activityplanreport__targetlocationreport__disaggregationlocationreport__disaggregation__name",
            "activityplanreport__activity_plan__activity_domain__name",
        )
        .annotate(
            total_people_reached=Sum("activityplanreport__targetlocationreport__disaggregationlocationreport__reached"),
        )
    )

    # Organize data into a dictionary
    data_dict = {}

    for entry in reach_by_activity:
        disaggregation_name = entry[
            "activityplanreport__targetlocationreport__disaggregationlocationreport__disaggregation__name"
        ]
        activity_domain = entry["activityplanreport__activity_plan__activity_domain__name"]
        total_reached = entry["total_people_reached"]

        if disaggregation_name not in data_dict:
            data_dict[disaggregation_name] = {}

        data_dict[disaggregation_name][activity_domain] = total_reached

    for category, total_reached in data_dict.items():
        if total_reached and all(value is not None for value in total_reached.values()):
            sum_disaggregation = sum(value for value in total_reached.values() if value is not None)
            data_dict[category]["total"] = sum_disaggregation

    clusters = cache.get("clusters")
    if clusters is None:
        clusters = Cluster.objects.all()
        cache.set("clusters", clusters, 60 * 60 * 24)  # cache for 1 day

    context = {
        "org": org,
        "counts": counts,
        "people_reached_labels": labels,
        "people_reached_data": data,
        "activity_domains": activity_domains,
        "reach_by_activity": data_dict,
        "clusters": clusters,
    }

    return render(request, "project_reports/org_5w_dashboard.html", context)
