from django.contrib import admin
from .models import ActivityReport



# Register your models here.
class ActivityReportAdmin(admin.ModelAdmin):
    list_display = (
        'project', 'activity_plan', 'location', 'boys', 'girls', 'men', 'women', 'elderly_men', 'elderly_women',
        'households')
    search_fields = (
        'project__title', 'location__name', 'boys', 'girls', 'men', 'women', 'elderly_men', 'elderly_women',
        'households')
    list_filter = ('project', 'activity_plan', 'location')
admin.site.register(ActivityReport, ActivityReportAdmin)