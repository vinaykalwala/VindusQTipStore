from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderItem, Order

@receiver(post_save, sender=OrderItem)
def update_order_status(sender, instance, **kwargs):
    order = instance.order
    items = order.items.all()
    
    item_statuses = [item.status for item in items]

    if all(status == 'delivered' for status in item_statuses):
        order.status = 'delivered'
        # Get the latest delivered_date among all items in the order
        latest_delivery_date = order.items.filter(status='delivered') \
            .order_by('-delivered_date') \
            .values_list('delivered_date', flat=True) \
            .first()

        if latest_delivery_date:
            order.delivered_date = latest_delivery_date

        order.save()

    elif any(status == 'delivered' for status in item_statuses) and not all(status == 'delivered' for status in item_statuses):
        order.status = 'Partially Delivered'

    elif all(status == 'Out for Delivery' for status in item_statuses):
        order.status = 'Out for Delivery'

    elif any(status == 'Out for Delivery' for status in item_statuses):
        order.status = 'Out for Delivery'

    elif all(status == 'Dispatched' for status in item_statuses):
        order.status = 'Dispatched'

    elif any(status == 'Dispatched' for status in item_statuses):
        order.status = 'Partially Dispatched'

    elif all(status == 'shipped' for status in item_statuses):
        order.status = 'shipped'

    elif any(status == 'shipped' for status in item_statuses):
        order.status = 'Partially Shipped'

    elif all(status == 'cancelled' for status in item_statuses):
        order.status = 'cancelled'

    elif all(status in ['pending', 'Confirmed'] for status in item_statuses):
        order.status = 'Confirmed'

    else:
        order.status = 'pending'  # fallback or mixed state

    order.save()
