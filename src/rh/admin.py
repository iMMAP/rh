import csv

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Count
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    ActivityDetail,
    ActivityDomain,
    ActivityPlan,
    ActivityType,
    BeneficiaryType,
    BudgetProgress,
    CashInKindDetail,
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
    RationSize,
    RationType,
    TargetLocation,
    TransferCategory,
    TransferMechanismType,
    UnitType,
)

admin.site.register(Currency)
admin.site.register(LocationType)
admin.site.register(ImplementationModalityType)
admin.site.register(TransferMechanismType)
admin.site.register(PackageType)
admin.site.register(TransferCategory)
admin.site.register(GrantType)
admin.site.register(UnitType)
admin.site.register(CashInKindDetail)
admin.site.register(RationType)
admin.site.register(RationSize)


def export_as_csv(self, request, queryset):
    meta = self.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response


class FacilitySiteTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "cluster")
    list_filter = ("cluster",)
    actions = [export_as_csv]


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


@admin.action(description="Export as CSV")
def org_export_as_csv(self, request, queryset):
    meta = self.model._meta
    field_names = [field.name for field in meta.fields] + ["countries", "clusters"]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow(
            [getattr(obj, field) for field in field_names[:-2]]  # Existing fields
            + [
                ", ".join([country.name for country in obj.countries.all()]),  # Countries
                ", ".join([cluster.title for cluster in obj.clusters.all()]),
            ]
        )  # Clusters

    return response


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "type", "countries_count", "clusters_count")
    search_fields = ("name", "code")
    list_filter = ("type",)
    actions = [org_export_as_csv]

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
    list_display = ("code", "name", "countries_count", "clusters_count")
    search_fields = (
        "code",
        "name",
    )
    filter_horizontal = (
        "countries",
        "clusters",
    )
    actions = [export_as_csv]

    def countries_count(self, obj):
        return obj.countries.count()

    def clusters_count(self, obj):
        return obj.clusters.count()


admin.site.register(Donor, DonorAdmin)


class BeneficiaryTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "is_active", "country", "Clusters")
    search_fields = ("code", "name")
    list_filter = (
        "type",
        "clusters",
    )
    filter_horizontal = ("clusters",)
    actions = [export_as_csv]

    def Clusters(self, obj):
        clusters = obj.clusters.all()
        return ", ".join([c.title for c in clusters])


admin.site.register(BeneficiaryType, BeneficiaryTypeAdmin)


class DisaggregationAdmin(admin.ModelAdmin):
    list_display = ("name", "indicators_count", "clusters_count")
    search_fields = (
        "code",
        "name",
    )
    form = DisseggregationModelAdminForm
    # list_filter = ('cluster', 'country')
    filter_horizontal = ("clusters",)
    actions = [export_as_csv]

    def indicators_count(self, obj):
        return obj.indicators.count()

    def clusters_count(self, obj):
        return obj.clusters.count()


admin.site.register(Disaggregation, DisaggregationAdmin)


class DisaggregationInline(admin.TabularInline):
    model = Disaggregation.indicators.through
    extra = 1


class IndicatorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
    )
    search_fields = ("activity_types__name", "name")
    list_filter = ("activity_types__name",)
    inlines = [
        DisaggregationInline,
    ]

    filter_horizontal = ("activity_types",)
    actions = [export_as_csv]


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
    actions = [export_as_csv]


admin.site.register(ActivityDomain, ActivityDomainAdmin)


class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "activity_domain", "is_active")
    search_fields = (
        "name",
        "activity_domain__name",
        "code",
    )
    list_filter = ("activity_domain",)
    raw_id_fields = ["activity_domain"]
    prepopulated_fields = {"code": ["name"]}
    actions = [export_as_csv]


admin.site.register(ActivityType, ActivityTypeAdmin)


class ActivityDetailAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "activity_type",
        "code",
    )
    search_fields = ("activity_type__name", "name", "code")
    actions = [export_as_csv]


admin.site.register(ActivityDetail, ActivityDetailAdmin)


#############################################
####### Project Planning Model Admins #######
#############################################
def export_as_csv(self, request, queryset):
    meta = self.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response


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
    raw_id_fields = ["organization", "user"]
    actions = [export_as_csv]

    def show_clusters(self, obj):
        return ",\n".join([a.title for a in obj.clusters.all()])

    show_clusters.short_description = "Clusters"


admin.site.register(Project, ProjectAdmin)


class ActivityPlanAdmin(admin.ModelAdmin):
    list_display = ("activity_domain", "project_link", "state")
    search_fields = ("state", "project__title")
    list_filter = ("state",)
    raw_id_fields = ["project"]
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
    raw_id_fields = ["project", "activity_plan", "district", "implementing_partner", "zone"]
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
        "get_activity_domains",
        "grant",
        "amount_recieved",
        "budget_currency",
        "received_date",
        "country",
    )
    search_fields = ("project", "donor", "activity_domains", "country")
    list_filter = ("project",)

    # get activity domains for display list
    # Custom method to display the activity domains in the list
    def get_activity_domains(self, obj):
        return ", ".join([str(domain) for domain in obj.activity_domains.all()])

    get_activity_domains.short_description = "Activity Domains"


admin.site.register(BudgetProgress, BudgetProgressAdmin)
