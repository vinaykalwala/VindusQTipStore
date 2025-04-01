from django.shortcuts import render
from .models import SalesReport

# View Vendor Sales Report
def sales_report(request):
    reports = SalesReport.objects.filter(vendor=request.user)
    return render(request, 'analytics/sales_report.html', {'reports': reports})
