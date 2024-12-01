from django.contrib import admin

from rh.models import Location

from .models import (
    StockItemsType,
    StockMonthlyReport,
    StockReport,
    StockUnit,
    Warehouse,
)

# Register your models here.


def get_app_list(self, request):
    """

    ***IMPORTANT***
    Add future new models here in this ordering method and then register
    in admin.
    ***IMPORTANT***

    *Overrides orignal method of sorting models in admin view.
    Return a sorted list of all the installed apps that have been
    registered in this site.
    """
    # Retrieve the original list
    app_dict = self._build_app_dict(request)
    app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())

    return app_list


# Override the get_app_list of AdminSite
admin.AdminSite.get_app_list = get_app_list


#############################################
########### Stock Types Model Admin #############
#############################################
class StockTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "cluster")
    search_fields = ("Name", "cluster")
    list_filter = ("cluster",)


admin.site.register(StockItemsType, StockTypeAdmin)


#############################################
########### Stock Units Model Admin #############
#############################################
admin.site.register(StockUnit)


##############################################
###### Warehouse Location Model Admin ########
##############################################
class WarehouseLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "province", "district")
    search_fields = ("name", "province__name")
    list_filter = ("name",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "province":
            kwargs["queryset"] = Location.objects.filter(type="Province")
        if db_field.name == "district":
            kwargs["queryset"] = Location.objects.filter(type="District")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Warehouse, WarehouseLocationAdmin)

##############################################
###### Warehouse Location Model Admin ########
##############################################
# class StockLocationDetailsAdmin(admin.ModelAdmin):
#     readonly_fields = ['created_at']
admin.site.register(StockReport)

# class StockReportsAdmin(admin.ModelAdmin):
admin.site.register(StockMonthlyReport)
