from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count
from django.utils import timezone
import calendar
from .models import SalesReport
from Orders.models import *

@login_required
def vendor_sales_report(request):
    if request.user.role != 'vendor':
        return render(request, '403.html', status=403)

    year = int(request.GET.get('year', timezone.now().year))
    report = get_vendor_sales_report(request.user, year)
    return render(request, 'analytics/vendor_sales_report.html', {'report': report})


@staff_member_required
def superuser_sales_report(request):
    year = int(request.GET.get('year', timezone.now().year))
    report = get_superuser_sales_report(year)
    return render(request, 'analytics/superuser_sales_report.html', {'report': report})


def get_vendor_sales_report(vendor, year):
    vendor_products = Product.objects.filter(vendor=vendor)

    order_items = OrderItem.objects.select_related('order', 'product').filter(
        product__in=vendor_products,
        order__created_at__year=year
    ).annotate(order_item_count=Count('order__items'))

    filtered_items = []
    for item in order_items:
        order = item.order
        if item.order_item_count == 1:
            if order.status in ['shipped', 'Out for Delivery', 'delivered'] and item.status not in ['Cancelled', 'Returned & Refunded']:
                filtered_items.append(item)
        else:
            if order.payment_method == 'Razorpay' and item.status in ['Shipped', 'Out for Delivery', 'Delivered']:
                filtered_items.append(item)
            elif order.payment_method == 'COD' and item.status == 'Delivered':
                filtered_items.append(item)

    total_revenue = sum([(item.price or 0) * (item.quantity or 1) for item in filtered_items])
    total_orders = len(set(item.order.id for item in filtered_items))

    monthly_map = defaultdict(lambda: {'revenue': 0, 'order_ids': set()})
    for item in filtered_items:
        month = item.order.created_at.month
        monthly_map[month]['revenue'] += (item.price or 0) * (item.quantity or 1)
        monthly_map[month]['order_ids'].add(item.order.id)

    monthly_sales = []
    for i in range(1, 13):
        monthly_sales.append({
            'month_name': calendar.month_name[i],
            'revenue': monthly_map[i]['revenue'],
            'order_count': len(monthly_map[i]['order_ids']),
        })

    max_revenue = max([m['revenue'] for m in monthly_sales]) or 1
    for sale in monthly_sales:
        sale['bar_height'] = int((sale['revenue'] / max_revenue) * 200)

    top_products_map = {}
    for item in filtered_items:
        name = item.product.name
        if name not in top_products_map:
            top_products_map[name] = {'total_sold': 0, 'revenue': 0}
        top_products_map[name]['total_sold'] += item.quantity
        top_products_map[name]['revenue'] += item.price * item.quantity

    top_products = sorted([
        {'product__name': name, 'total_sold': data['total_sold'], 'revenue': data['revenue']}
        for name, data in top_products_map.items()
    ], key=lambda x: x['total_sold'], reverse=True)[:5]

    return {
        'year': year,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'monthly_sales': monthly_sales,
        'top_products': top_products,
    }


def get_superuser_sales_report(year):
    order_items = OrderItem.objects.select_related('order', 'product').filter(
        order__created_at__year=year
    ).annotate(order_item_count=Count('order__items'))

    filtered_items = []
    for item in order_items:
        order = item.order
        if item.order_item_count == 1:
            if order.status in ['shipped', 'Out for Delivery', 'delivered'] and item.status not in ['Cancelled', 'Returned & Refunded']:
                filtered_items.append(item)
        else:
            if order.payment_method == 'Razorpay' and item.status in ['Shipped', 'Out for Delivery', 'Delivered']:
                filtered_items.append(item)
            elif order.payment_method == 'COD' and item.status == 'Delivered':
                filtered_items.append(item)

    total_revenue = sum([(item.price or 0) * (item.quantity or 1) for item in filtered_items])
    total_orders = len(set(item.order.id for item in filtered_items))

    monthly_map = defaultdict(lambda: {'revenue': 0, 'order_ids': set()})
    for item in filtered_items:
        month = item.order.created_at.month
        monthly_map[month]['revenue'] += (item.price or 0) * (item.quantity or 1)
        monthly_map[month]['order_ids'].add(item.order.id)

    monthly_sales = []
    for i in range(1, 13):
        monthly_sales.append({
            'month_name': calendar.month_name[i],
            'revenue': monthly_map[i]['revenue'],
            'order_count': len(monthly_map[i]['order_ids']),
        })

    max_revenue = max([m['revenue'] for m in monthly_sales]) or 1
    for sale in monthly_sales:
        sale['bar_height'] = int((sale['revenue'] / max_revenue) * 200)

    top_products_map = {}
    for item in filtered_items:
        name = item.product.name
        if name not in top_products_map:
            top_products_map[name] = {'total_sold': 0, 'revenue': 0}
        top_products_map[name]['total_sold'] += item.quantity
        top_products_map[name]['revenue'] += item.price * item.quantity

    top_products = sorted([
        {'product__name': name, 'total_sold': data['total_sold'], 'revenue': data['revenue']}
        for name, data in top_products_map.items()
    ], key=lambda x: x['total_sold'], reverse=True)[:5]

    return {
        'year': year,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'monthly_sales': monthly_sales,
        'top_products': top_products,
    }
