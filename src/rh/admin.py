from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Count
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
    ReportType,
    TargetLocation,
    TransferCategory,
    TransferMechanismType,
    UnitType,
)

from import_export.admin import ImportExportActionModelAdmin

admin.site.register(Currency)
admin.site.register(LocationType)
admin.site.register(FacilitySiteType)
admin.site.register(ImplementationModalityType)
admin.site.register(TransferMechanismType)
admin.site.register(PackageType)
admin.site.register(TransferCategory)
admin.site.register(GrantType)
admin.site.register(UnitType)
admin.site.register(ReportType)


class ActivityPlanModelAdminForm(forms.ModelForm):
    class Meta:
        model = ActivityPlan
        fields = "__all__"
        widgets = {
            "indicators": FilteredSelectMultiple("Indicators", False),
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
    list_filter = ("code",)

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
    # list_filter = ('cluster', 'country')

    def countries_count(self, obj):
        return obj.countries.count()

    def clusters_count(self, obj):
        return obj.clusters.count()


admin.site.register(Donor, DonorAdmin)


class BeneficiaryTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "country")
    search_fields = ("code", "name", "country__name")
    list_filter = ("country",)


admin.site.register(BeneficiaryType, BeneficiaryTypeAdmin)


class DisaggregationAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ("name", "indicators_count", "clusters_count")
    search_fields = (
        "code",
        "name",
    )
    form = DisseggregationModelAdminForm
    # list_filter = ('cluster', 'country')

    def indicators_count(self, obj):
        return obj.indicators.count()

    def clusters_count(self, obj):
        return obj.clusters.count()


admin.site.register(Disaggregation, DisaggregationAdmin)

admin.site.register(DisaggregationLocation)


class DisaggregationInline(admin.TabularInline):
    model = Disaggregation.indicators.through
    extra = 1


class IndicatorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
    )
    search_fields = ("activity_types__name", "name", "code")
    # list_filter = ('activity_type',)
    inlines = [
        DisaggregationInline,
    ]


admin.site.register(Indicator, IndicatorAdmin)


class ActivityDomainAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "active")
    search_fields = ("name", "clusters__title", "code", "countries__name")
    list_filter = ("clusters", "countries")


admin.site.register(ActivityDomain, ActivityDomainAdmin)


class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "activity_domain", "active")
    search_fields = (
        "name",
        "activity_domain__name",
        "clusters__title",
        "code",
        "countries__name",
    )
    list_filter = ("activity_domain", "clusters", "countries")


admin.site.register(ActivityType, ActivityTypeAdmin)


class ActivityDetailAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "activity_type",
        "code",
    )
    search_fields = ("activity_type__name", "name", "code")
    list_filter = ("activity_type",)


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
        "active",
    )
    search_fields = (
        "title",
        "code",
        "clusters__title",
        "implementing_partners__code",
        "programme_partners__code",
        "state",
    )
    list_filter = ("state", "active", "clusters")

    def show_clusters(self, obj):
        return ",\n".join([a.title for a in obj.clusters.all()])

    show_clusters.short_description = "Clusters"


admin.site.register(Project, ProjectAdmin)


class ActivityPlanAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project",
        "beneficiary",
        "beneficiary_category",
        "state",
        "active",
    )
    search_fields = ("title", "state", "active", "project__title")
    list_filter = ("state", "active", "project__code")
    form = ActivityPlanModelAdminForm


admin.site.register(ActivityPlan, ActivityPlanAdmin)


class TargetLocationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "site_name",
        "project",
        "activity_plan",
        "country",
        "province",
        "district",
        "zone",
        "state",
        "active",
    )
    search_fields = ("title", "project__title", "state", "active")
    list_filter = ("state", "active", "project__code")


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
    list_filter = ("project", "donor", "country")


admin.site.register(BudgetProgress, BudgetProgressAdmin)
