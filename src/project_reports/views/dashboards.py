import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, render
from rh.models import Cluster, Organization
from rh.utils import is_cluster_lead

from project_reports.models import ProjectMonthlyReport


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
    }

    if organization is not None:
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
    from_date = request.GET.get("from", datetime.date(datetime.datetime.now().year, 1, 1))
    to_date = request.GET.get("to", datetime.datetime.now().date())

    counts = ProjectMonthlyReport.objects.filter(
        project__organization=user_org,
        state__in=["submited", "completed"],
        from_date__lte=to_date,
        to_date__gte=from_date,
    ).aggregate(
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
            project__organization=user_org,
            state__in=["submited", "completed"],
            from_date__lte=to_date,
            to_date__gte=from_date,
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
            project__organization=user_org,
            state__in=["in-progress", "completed"],
            from_date__lte=to_date,
            to_date__gte=from_date,
            activityplanreport__beneficiary_status="new_beneficiary",
        )
        .values_list("activityplanreport__activity_plan__activity_domain__name", flat=True)
        .distinct()
    )

    reach_by_activity = (
        ProjectMonthlyReport.objects.filter(
            project__organization=user_org,
            state__in=["submited", "completed"],
            from_date__lte=to_date,
            to_date__gte=from_date,
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

    context = {
        "org": org,
        "counts": counts,
        "people_reached_labels": labels,
        "people_reached_data": data,
        "activity_domains": activity_domains,
        "reach_by_activity": data_dict,
    }

    return render(request, "project_reports/org_5w_dashboard.html", context)
