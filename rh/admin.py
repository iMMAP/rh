from django.contrib import admin
from django.db.models import Count

from .models import *

admin.site.register(Currency)
admin.site.register(LocationType)


class ClusterAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'title','countries_count','donors_count')
    search_fields = ('code', 'name')
    list_filter = ('code',)

    # get the count of a many to many relationship with Donor model
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            donors_count=Count('donor'),
            countries_count=Count('countries')
        )
        return queryset

    def donors_count(self, obj):
        return obj.donors_count

    def countries_count(self, obj):
        return obj.countries_count
    
admin.site.register(Cluster, ClusterAdmin)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'code', 'level', 'original_name', 'type')
    list_filter = ('level', 'type')
    search_fields = ('name', 'parent__name', 'level', 'type')
admin.site.register(Location, LocationAdmin)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'type', 'countries_count','clusters_count')
    search_fields = ('name', 'type')
    list_filter = ('type', )

    def countries_count(self, obj):
        return obj.countries.count()
    
    def clusters_count(self, obj):
        return obj.clusters.count()
admin.site.register(Organization, OrganizationAdmin)


class DonorAdmin(admin.ModelAdmin):
    list_display = ('name','countries_count','clusters_count')
    search_fields = ('code', 'name',)
    # list_filter = ('cluster', 'country')
    
    def countries_count(self, obj):
        return obj.countries.count()
    
    def clusters_count(self, obj):
        return obj.clusters.count()
   
admin.site.register(Donor, DonorAdmin)




