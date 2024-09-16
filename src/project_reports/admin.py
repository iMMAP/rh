from django.contrib import admin

from .models import (
    ActivityPlanReport,
    DisaggregationLocationReport,
    ProjectMonthlyReport,
    ResponseType,
    TargetLocationReport,
)


##############################################
######### Reporting Model Admins ##########
##############################################
class ResponseTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "show_clusters",
    )
    search_fields = ("name",)

    def show_clusters(self, obj):
        return ",\n".join([a.title for a in obj.clusters.all()])

    show_clusters.short_description = "Clusters"


admin.site.register(ResponseType, ResponseTypeAdmin)


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
