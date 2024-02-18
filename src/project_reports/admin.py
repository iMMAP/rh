from django.contrib import admin

from .models import (
    ActivityPlanReport,
    DisaggregationLocationReport,
    ProjectMonthlyReport,
    TargetLocationReport,
)

##############################################
######### Reporting Model Admins ##########
##############################################


class ProjectMonthlyReportAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "state",
        "is_active",
        "report_period",
        "report_date",
        "report_due_date",
    )


admin.site.register(ProjectMonthlyReport, ProjectMonthlyReportAdmin)


class ActivityPlanReportAdmin(admin.ModelAdmin):
    list_display = ("monthly_report", "activity_plan", "indicator")


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
