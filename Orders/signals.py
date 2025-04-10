# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderItem, Order

@receiver(post_save, sender=OrderItem)
def update_order_status(sender, instance, **kwargs):
    all_items = instance.order.items.all()

    if all(i.status == 'Delivered' for i in all_items):
        instance.order.status = 'delivered'
    elif any(i.status == 'Out for Delivery' for i in all_items):
        instance.order.status = 'Out for Delivery'
    elif any(i.status == 'Shipped' for i in all_items):
        instance.order.status = 'shipped'
    elif all(i.status == 'Cancelled' for i in all_items):
        instance.order.status = 'cancelled'
    else:
        instance.order.status = 'Processing'

    instance.order.save()
