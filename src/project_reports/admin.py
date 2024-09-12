from django.contrib import admin

from .models import (
    ActivityPlanReport,
    ClusterDashboardReport,
    DisaggregationLocationReport,
    ProjectMonthlyReport,
    ResponseType,
    TargetLocationReport,
)

##############################################
######### Reporting Model Admins ##########
##############################################


admin.site.register(ResponseType)


class ProjectMonthlyReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "project",
        "state",
        "from_date",
        "to_date",
    )
    search_fields = ("id", "project__code")
    raw_id_fields = ["project"]


admin.site.register(ProjectMonthlyReport, ProjectMonthlyReportAdmin)


class ActivityPlanReportAdmin(admin.ModelAdmin):
    list_display = ("monthly_report", "activity_plan")
    raw_id_fields = ["monthly_report", "activity_plan"]


admin.site.register(ActivityPlanReport, ActivityPlanReportAdmin)


class TargetLocationReportAdmin(admin.ModelAdmin):
    list_display = (
        "activity_plan_report",
        "location_type",
    )


admin.site.register(TargetLocationReport, TargetLocationReportAdmin)


class DisaggregationLocationReportAdmin(admin.ModelAdmin):
    list_display = ("target_location_report", "disaggregation", "reached")


admin.site.register(DisaggregationLocationReport, DisaggregationLocationReportAdmin)


class ClusterDashboardReportAdmin(admin.ModelAdmin):
    list_display = (
        "cluster_name",
        "report_link",
        "is_active",
    )


admin.site.register(ClusterDashboardReport, ClusterDashboardReportAdmin)
