from django.contrib import admin

from .models import (
    ActivityPlanReport,
    DisaggregationLocationReport,
    ProjectMonthlyReport,
    TargetLocationReport,
    ResponseType,
    ClusterDashboardReport,
)

##############################################
######### Reporting Model Admins ##########
##############################################


admin.site.register(ResponseType)


class ProjectMonthlyReportAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "state",
        "is_active",
        "report_period",
        "report_date",
        "report_due_date",
    )
    raw_id_fields = ["project"]


admin.site.register(ProjectMonthlyReport, ProjectMonthlyReportAdmin)


class ActivityPlanReportAdmin(admin.ModelAdmin):
    list_display = ("monthly_report", "activity_plan", "indicator")
    raw_id_fields = ["monthly_report", "activity_plan", "indicator"]


admin.site.register(ActivityPlanReport, ActivityPlanReportAdmin)


class TargetLocationReportAdmin(admin.ModelAdmin):
    list_display = (
        "activity_plan_report",
        "country",
        "province",
        "district",
        "zone",
        "location_type",
    )


admin.site.register(TargetLocationReport, TargetLocationReportAdmin)


class DisaggregationLocationReportAdmin(admin.ModelAdmin):
    list_display = ("target_location_report", "is_active", "disaggregation", "target")


admin.site.register(DisaggregationLocationReport, DisaggregationLocationReportAdmin)

class ClusterDashboardReportAdmin(admin.ModelAdmin):
    list_display = (
        'cluster_name',
        'report_link',
    )

admin.site.register(ClusterDashboardReport, ClusterDashboardReportAdmin)