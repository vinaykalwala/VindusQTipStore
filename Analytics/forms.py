from django import forms
from .models import SalesReport

# Sales Report Filter Form
class SalesReportFilterForm(forms.Form):
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)
