from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Case, Count, IntegerField, Q, Sum, Value, When
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, render

from project_reports.filters import Organization5WFilter
from project_reports.models import ProjectMonthlyReport
from rh.models import Cluster, Organization
from users.utils import is_cluster_lead


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
    filter_params = {
        "project__clusters__in": [cluster],
        "state__in": ["submited", "completed"],
        "project__user__profile__country": user_country,
        "activityplanreport__activity_plan__activity_domain__clusters__in": [cluster],
        "activityplanreport__targetlocationreport__beneficiary_status": "new_beneficiary",
    }

    monthly_report_filter = Organization5WFilter(
        request.GET,
        queryset=ProjectMonthlyReport.objects.filter(**filter_params),
        user=request.user,
    )

    counts = monthly_report_filter.qs.filter(**filter_params).aggregate(
        report_indicators_count=Count("activityplanreport__activity_plan__indicator", distinct=True),
        report_implementing_partners_count=Count(
            "activityplanreport__targetlocationreport__target_location__implementing_partner", distinct=True
        ),
        report_target_location_province_count=Count(
            "activityplanreport__targetlocationreport__target_location__province", distinct=True
        ),
    )

    people_reached_data = (
        monthly_report_filter.qs.order_by("from_date")
        .values("from_date")
        .annotate(
            total_people_reached=Coalesce(
                Sum(
                    Case(
                        When(
                            ~Q(
                                activityplanreport__targetlocationreport__disaggregationlocationreport__disaggregation__name__icontains="households",
                            ),
                            then="activityplanreport__targetlocationreport__disaggregationlocationreport__reached",
                        ),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ),
                Value(0),
            )
        )
    )

    counts["people_reached"] = 0
    for report in people_reached_data:
        counts["people_reached"] += report["total_people_reached"]

    labels = [report["from_date"].strftime("%b") for report in people_reached_data]
    data = [
        report["total_people_reached"] if report["total_people_reached"] is not None else 0
        for report in people_reached_data
    ]

    # people reached by activities
    activity_domains = (
        monthly_report_filter.qs.filter(**filter_params)
        .values_list("activityplanreport__activity_plan__activity_domain__name", flat=True)
        .distinct()
    )

    reach_by_activity = (
        monthly_report_filter.qs.filter(**filter_params)
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
        "dashboard_filter": monthly_report_filter,
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
    filter_params = {
        "project__organization": user_org,
        "state__in": ["submited", "completed"],
        "activityplanreport__targetlocationreport__beneficiary_status": "new_beneficiary",
    }

    monthly_report_filter = Organization5WFilter(
        request.GET,
        queryset=ProjectMonthlyReport.objects.filter(**filter_params),
        user=request.user,
    )
    monthly_reports = monthly_report_filter.qs

    counts = monthly_reports.aggregate(
        report_indicators_count=Count("activityplanreport__activity_plan__indicator", distinct=True),
        report_implementing_partners_count=Count(
            "activityplanreport__targetlocationreport__target_location__implementing_partner", distinct=True
        ),
        report_target_location_province_count=Count(
            "activityplanreport__targetlocationreport__target_location__province", distinct=True
        ),
    )

    people_reached_data = (
        monthly_reports.order_by("from_date")
        .values("from_date")
        .annotate(
            total_people_reached=Coalesce(
                Sum(
                    Case(
                        When(
                            ~Q(
                                activityplanreport__targetlocationreport__disaggregationlocationreport__disaggregation__name__icontains="households",
                            ),
                            then="activityplanreport__targetlocationreport__disaggregationlocationreport__reached",
                        ),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ),
                Value(0),
                output_field=IntegerField(),
            )
        )
    )

    counts["people_reached"] = 0
    for report in people_reached_data:
        counts["people_reached"] += report["total_people_reached"]

    labels = [report["from_date"].strftime("%b") for report in people_reached_data]
    data = [
        report["total_people_reached"] if report["total_people_reached"] is not None else 0
        for report in people_reached_data
    ]

    activity_domains = monthly_reports.values_list(
        "activityplanreport__activity_plan__activity_domain__name", flat=True
    ).distinct()

    reach_by_activity = monthly_reports.values(
        "activityplanreport__targetlocationreport__disaggregationlocationreport__disaggregation__name",
        "activityplanreport__activity_plan__activity_domain__name",
    ).annotate(
        total_people_reached=Sum("activityplanreport__targetlocationreport__disaggregationlocationreport__reached"),
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
        "org": org,
        "counts": counts,
        "people_reached_labels": labels,
        "people_reached_data": data,
        "activity_domains": activity_domains,
        "reach_by_activity": data_dict,
        "dashboard_filter": monthly_report_filter,
    }

    return render(request, "project_reports/org_5w_dashboard.html", context)
