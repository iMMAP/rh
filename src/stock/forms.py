from django import forms
from rh.models import Location

from .models import StockLocationDetails, StockReports, WarehouseLocation


class WarehouseLocationForm(forms.ModelForm):
    class Meta:
        model = WarehouseLocation
        fields = ("province", "district", "name")
        labels = {
            "name": "Warehouse Name",
        }
        # exclude = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["province"].queryset = Location.objects.filter(type="Province")
        self.fields["district"].queryset = Location.objects.filter(type="District")


class StockLocationDetailsForm(forms.ModelForm):
    class Meta:
        model = StockLocationDetails
        fields = "__all__"


class StockReportForm(forms.ModelForm):
    class Meta:
        model = StockReports
        fields = ["note"]
