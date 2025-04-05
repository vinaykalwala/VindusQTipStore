from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
import calendar
from .models import SalesReport
from Orders.models import *

@login_required
def vendor_sales_report(request):
    if request.user.role != 'vendor':
        return render(request, '403.html', status=403)

    year = request.GET.get('year', timezone.now().year)
    year = int(year)

    report = get_vendor_sales_report(request.user, year)
    return render(request, 'analytics/vendor_sales_report.html', {'report': report})

@staff_member_required
def superuser_sales_report(request):
    year = request.GET.get('year', timezone.now().year)
    year = int(year)

    report = get_superuser_sales_report(year)
    return render(request, 'analytics/superuser_sales_report.html', {'report': report})

def get_vendor_sales_report(vendor, year):
    vendor_products = Product.objects.filter(vendor=vendor)
    order_items = OrderItem.objects.filter(
        product__in=vendor_products,
        order__created_at__year=year,
        order__status__in=['shipped', 'Out for Delivery', 'delivered']
    )

    total_revenue = order_items.aggregate(total=Sum('price', field="price * quantity"))['total'] or 0
    total_orders = order_items.values('order').distinct().count()

    # Month-wise sales using TruncMonth
    monthly_sales = order_items.annotate(
        month=TruncMonth('order__created_at')
    ).values('month').annotate(
        revenue=Sum('price', field="price * quantity"),
        order_count=Count('order', distinct=True)
    ).order_by('month')

    # Convert to month names and fill missing months
    all_months = [{'month_name': calendar.month_name[i], 'revenue': 0, 'order_count': 0} for i in range(1, 13)]
    for item in monthly_sales:
        month_num = item['month'].month
        all_months[month_num - 1] = {
            'month_name': calendar.month_name[month_num],
            'revenue': item['revenue'] or 0,
            'order_count': item['order_count']
        }

    top_products = order_items.values('product__name').annotate(
        total_sold=Sum('quantity'),
        revenue=Sum('price', field="price * quantity")
    ).order_by('-total_sold')[:5]

    return {
        'year': year,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'monthly_sales': all_months,
        'top_products': top_products,
    }

def get_superuser_sales_report(year):
    order_items = OrderItem.objects.filter(
        order__created_at__year=year,
        order__status__in=['shipped', 'Out for Delivery', 'delivered']
    )

    total_revenue = order_items.aggregate(total=Sum('price', field="price * quantity"))['total'] or 0
    total_orders = order_items.values('order').distinct().count()

    # Month-wise sales using TruncMonth
    monthly_sales = order_items.annotate(
        month=TruncMonth('order__created_at')
    ).values('month').annotate(
        revenue=Sum('price', field="price * quantity"),
        order_count=Count('order', distinct=True)
    ).order_by('month')

    # Convert to month names and fill missing months
    all_months = [{'month_name': calendar.month_name[i], 'revenue': 0, 'order_count': 0} for i in range(1, 13)]
    for item in monthly_sales:
        month_num = item['month'].month
        all_months[month_num - 1] = {
            'month_name': calendar.month_name[month_num],
            'revenue': item['revenue'] or 0,
            'order_count': item['order_count']
        }

    vendor_performance = order_items.values('product__vendor__username').annotate(
        revenue=Sum('price', field="price * quantity"),
        order_count=Count('order', distinct=True)
    ).order_by('-revenue')

    top_products = order_items.values('product__name').annotate(
        total_sold=Sum('quantity'),
        revenue=Sum('price', field="price * quantity")
    ).order_by('-total_sold')[:5]

    return {
        'year': year,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'monthly_sales': all_months,
        'vendor_performance': vendor_performance,
        'top_products': top_products,
    }