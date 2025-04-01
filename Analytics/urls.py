from django.urls import path
from .views import *

urlpatterns = [
    path('sales/', sales_report, name='sales-report'),
    # path('performance/', product_performance, name='product-performance'),
]
