from django.urls import path
from .views import *

urlpatterns = [
    path('vendor/report/', vendor_sales_report, name='vendor_sales_report'),
    path('admin/report/', superuser_sales_report, name='superuser_sales_report'),
]
