from .models import *

from django import forms


class WarehouseLocationForm(forms.ModelForm):
    class Meta:
        model = WarehouseLocation
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['province'].queryset = Location.objects.filter(type='Province')
        self.fields['district'].queryset = Location.objects.filter(type='District')


class StockLocationDetailsForm(forms.ModelForm):
    class Meta:
        model = StockLocationDetails
        fields = "__all__"


class StockReportForm(forms.ModelForm):
    class Meta:
        model = StockReports
        fields = ['note']