from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Count
from import_export.admin import ImportExportActionModelAdmin

from .models import (
    ActivityDetail,
    ActivityDomain,
    ActivityPlan,
    ActivityType,
    BeneficiaryType,
    BudgetProgress,
    Cluster,
    Currency,
    Disaggregation,
    DisaggregationLocation,
    Donor,
    FacilitySiteType,
    GrantType,
    ImplementationModalityType,
    Indicator,
    Location,
    LocationType,
    Organization,
    PackageType,
    Project,
    TargetLocation,
    TransferCategory,
    TransferMechanismType,
    UnitType,
)

from django.urls import reverse
from django.utils.html import format_html

admin.site.register(Currency)
admin.site.register(LocationType)
admin.site.register(ImplementationModalityType)
admin.site.register(TransferMechanismType)
admin.site.register(PackageType)
admin.site.register(TransferCategory)
admin.site.register(GrantType)
admin.site.register(UnitType)


class FacilitySiteTypeAdmin(admin.ModelAdmin):
    list_filter = ("cluster",)


admin.site.register(FacilitySiteType, FacilitySiteTypeAdmin)


class ActivityPlanModelAdminForm(forms.ModelForm):
    class Meta:
        model = ActivityPlan
        fields = "__all__"
        widgets = {
            "indicator": FilteredSelectMultiple("Indicator", False),
        }


class DisseggregationModelAdminForm(forms.ModelForm):
    class Meta:
        model = Disaggregation
        fields = "__all__"
        widgets = {
            "indicators": FilteredSelectMultiple("Indicators", False),
        }


class ClusterAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "title", "countries_count", "donors_count")
    search_fields = ("code", "name")
    filter_horizontal = ("countries",)

    # get the count of a many to many relationship with Donor model
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(donors_count=Count("donor"), countries_count=Count("countries"))
        return queryset

    def donors_count(self, obj):
        return obj.donors_count

    def countries_count(self, obj):
        return obj.countries_count


admin.site.register(Cluster, ClusterAdmin)


class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "code", "level", "original_name", "type")
    list_filter = ("level", "type")
    search_fields = ("name", "parent__name", "level", "type")


admin.site.register(Location, LocationAdmin)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "type", "countries_count", "clusters_count")
    search_fields = ("name", "type")
    list_filter = ("type",)

    filter_horizontal = (
        "countries",
        "clusters",
    )

    def countries_count(self, obj):
        return obj.countries.count()

    def clusters_count(self, obj):
        return obj.clusters.count()


admin.site.register(Organization, OrganizationAdmin)


class DonorAdmin(admin.ModelAdmin):
    list_display = ("name", "countries_count", "clusters_count")
    search_fields = (
        "code",
        "name",
    )
    filter_horizontal = (
        "countries",
        "clusters",
    )

    def countries_count(self, obj):
        return obj.countries.count()

    def clusters_count(self, obj):
        return obj.clusters.count()


admin.site.register(Donor, DonorAdmin)


class BeneficiaryTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "country", "Clusters")
    search_fields = ("code", "name")
    list_filter = (
        "type",
        "clusters",
    )
    filter_horizontal = ("clusters",)

    def Clusters(self, obj):
        clusters = obj.clusters.all()
        return ", ".join([c.title for c in clusters])


admin.site.register(BeneficiaryType, BeneficiaryTypeAdmin)


class DisaggregationAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ("name", "indicators_count", "clusters_count")
    search_fields = (
        "code",
        "name",
    )
    form = DisseggregationModelAdminForm
    # list_filter = ('cluster', 'country')
    filter_horizontal = ("clusters",)

    def indicators_count(self, obj):
        return obj.indicators.count()

    def clusters_count(self, obj):
        return obj.clusters.count()


admin.site.register(Disaggregation, DisaggregationAdmin)


class DisaggregationInline(admin.TabularInline):
    model = Disaggregation.indicators.through
    extra = 1


class IndicatorAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("activity_types__name", "name")
    # list_filter = ('activity_type',)
    inlines = [
        DisaggregationInline,
    ]

    filter_horizontal = ("activity_types",)


admin.site.register(Indicator, IndicatorAdmin)


class ActivityDomainAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    search_fields = ("name", "clusters__title", "code", "countries__name")
    list_filter = ("clusters",)
    prepopulated_fields = {"code": ["name"]}

    filter_horizontal = (
        "clusters",
        "countries",
    )


admin.site.register(ActivityDomain, ActivityDomainAdmin)


class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "activity_domain", "is_active")
    search_fields = (
        "name",
        "activity_domain__name",
        "code",
    )
    prepopulated_fields = {"code": ["name"]}


admin.site.register(ActivityType, ActivityTypeAdmin)


class ActivityDetailAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "activity_type",
        "code",
    )
    search_fields = ("activity_type__name", "name", "code")


admin.site.register(ActivityDetail, ActivityDetailAdmin)


#############################################
####### Project Planning Model Admins #######
#############################################


class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "code",
        "user",
        "show_clusters",
        "budget",
        "budget_currency",
        "state",
    )
    search_fields = (
        "title",
        "code",
        "clusters__title",
        "implementing_partners__code",
        "programme_partners__code",
        "state",
    )
    list_filter = ("state", "clusters")

    def show_clusters(self, obj):
        return ",\n".join([a.title for a in obj.clusters.all()])

    show_clusters.short_description = "Clusters"


admin.site.register(Project, ProjectAdmin)


class ActivityPlanAdmin(admin.ModelAdmin):
    list_display = ("activity_domain", "project_link", "state")
    search_fields = ("state", "project__title")
    list_filter = ("state",)
    form = ActivityPlanModelAdminForm

    def project_link(self, obj):
        url = reverse("admin:rh_project_change", args=[obj.project.id])
        return format_html("<em><a href='{}'>{}</a></em>", url, obj.project.code)


admin.site.register(ActivityPlan, ActivityPlanAdmin)


class DisaggregationLocationInline(admin.TabularInline):
    model = DisaggregationLocation
    extra = 1


class TargetLocationAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "activity_plan",
        "country",
        "province",
        "district",
        "zone",
        "state",
    )
    search_fields = ("title", "project__title", "state")
    list_filter = ("state",)
    inlines = [
        DisaggregationLocationInline,
    ]


admin.site.register(TargetLocation, TargetLocationAdmin)


##############################################
######### Project Financial Report ###########
##############################################


class BudgetProgressAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "donor",
        "title",
        "activity_domain",
        "grant",
        "amount_recieved",
        "budget_currency",
        "received_date",
        "country",
    )
    search_fields = ("project", "donor", "activity_domain", "country")
    list_filter = ("project",)


admin.site.register(BudgetProgress, BudgetProgressAdmin)
