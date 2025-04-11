from datetime import timedelta
from django.conf import settings
from django.utils import timezone 
from django.db import models
from django.forms import ValidationError
from Users.models import CustomUser, Address
from Products.models import Product, ProductVariant
from django.db import transaction
import logging
from django.conf import settings
from razorpay import Client, errors

logger = logging.getLogger(__name__)

ORDER_STATUS = (
    ('pending', 'Pending'),
    ('Confirmed', 'Confirmed'),
    ('shipped', 'Shipped'),
    ('Partially Shipped', 'Partially Shipped'),
    ('Partially Dispatched', 'Partially Dispatched'),
    ('Dispatched', 'Dispatched'),
    ('Out for Delivery', 'Out for Delivery'),
    ('delivered', 'Delivered'),
    ('Partially Delivered', 'Partially Delivered'),
    ('cancelled', 'Cancelled'),  
)

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=[('COD', 'Cash on Delivery'), ('Razorpay', 'Razorpay')], null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')], default='Pending')
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_date = models.DateField(null=True, blank=True)

    def cancel_order(self):
        """Cancels an order if it's not shipped and processes refund if prepaid"""
        if self.status in ['shipped', 'Out for Delivery', 'delivered']:
            return "You cannot cancel the order after it's shipped."

        with transaction.atomic():
            self.status = 'cancelled'

            # ✅ Restore stock
            for item in self.items.all():
                item.cancel_item()

            # ✅ Handle refunds for prepaid orders
            if self.payment_method == 'Razorpay' and self.payment_status == 'Completed':
                refund_message = self.process_refund()
                return refund_message  # Return refund status message

            self.save()

        return "Order cancelled successfully."
    

    def process_refund(self, item_id=None):
        """
        Handles refund for Razorpay orders.
        - If `item_id` is provided, refunds only the price of that item.
        - If `item_id` is None, refunds the full order amount.
        """
        client = Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        if not self.razorpay_payment_id:
            logger.error(f"Refund failed for Order {self.id}: Missing Razorpay Payment ID")
            return "Refund failed due to missing payment ID. Please contact support."

        try:
            if item_id:
                item_id = int(item_id)  # Ensure it's an integer
                logger.info(f"Searching for OrderItem with ID={item_id} in Order ID={self.id}")
                item = self.items.get(id=item_id)  # ✅ Using correct related_name
                refund_amount = int(item.subtotal() * 100)
            else:
                refund_amount = int(self.total_price * 100)
        except self.items.model.DoesNotExist:
            logger.error(f"Item not found in Order {self.id} for refund.")
            return "Item not found in order. Refund failed."

        # ✅ Check if the payment is captured before processing refund
        try:
            payment_info = client.payment.fetch(self.razorpay_payment_id)
            if payment_info.get("status") != "captured":
                logger.error(f"Refund failed for Order {self.id}: Payment not captured")
                return "Refund failed because the payment is not captured yet."

            refund = client.payment.refund(self.razorpay_payment_id, {"amount": refund_amount})

            if refund.get("status") == "processed":
                if refund_amount == self.total_price * 100:
                    self.payment_status = "Refunded"
                self.save()
                return f"Refund of ₹{refund_amount / 100} processed successfully."
            else:
                logger.error(f"Refund failed for Order {self.id} - Razorpay response: {refund}")
                return "Order cancelled, but refund processing failed. Please contact support."

        except errors.BadRequestError as e:
            logger.exception(f"Refund failed for Order {self.id}: {str(e)}")
            return "Order cancelled, but refund failed due to an issue with Razorpay. Please contact support."

    

    def __str__(self):
        return f"Order {self.id} - {self.user.username} ({self.status})"


# Order Items
class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('Dispatched', 'Dispatched'),
        ('Out for Delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Processing')  
    expected_delivery_date = models.DateField(null=True, blank=True) 
    delivered_date = models.DateField(null=True, blank=True)
    return_requested_at = models.DateTimeField(null=True, blank=True)
    replacement_requested_at = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(max_length=20, blank=True, null=True)
    delivery_otp = models.CharField(max_length=6, blank=True, null=True)
    otp_verified = models.BooleanField(default=False)
    delivery_person = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'role': 'delivery'},
        related_name='assigned_items'
    )

    
    def subtotal(self):
        return self.quantity * self.price
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Only true for new objects

        if is_new:
            if self.product.stock < self.quantity:
                raise ValidationError(f"Only {self.product.stock} items in stock for {self.product.name}")

            if not self.tracking_number:
                import uuid
                self.tracking_number = f"TRK-{uuid.uuid4().hex[:10].upper()}"

            # Deduct stock only on new
            self.product.stock -= self.quantity
            self.product.save()

            if not self.expected_delivery_date:
                from datetime import timedelta
                self.expected_delivery_date = timezone.now().date() + timedelta(days=5)

        super().save(*args, **kwargs)


    def cancel_item(self):
        """Cancels an order item, restores stock, and updates order total."""
        if self.status in ['Shipped', 'Out for Delivery', 'Delivered']:
            raise ValidationError("Item cannot be cancelled after it is shipped.")

        self.product.stock += self.quantity
        self.product.save()

        # ✅ Update order total price
        self.order.total_price -= self.subtotal()
        self.order.save()

        self.status = 'Cancelled'
        self.save()

        # ✅ Process partial refund if prepaid
        if self.order.payment_method == 'Razorpay' and self.order.payment_status == 'Completed':
            return self.order.process_refund(self.id)

        return "Item cancelled successfully."


    

    def __str__(self):
        return f"{self.order.id} - {self.product.name}"

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=100, unique=True,null=True, blank=True, default=None)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.status}"

class BankDetail(models.Model):
    """ ✅ Store user bank details for refunds """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="bank_details")
    account_holder_name = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50, unique=True)
    ifsc_code = models.CharField(max_length=20)
    branch_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.bank_name} ({self.account_number})"


class OrderTracking(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="tracking_logs")
    location = models.CharField(max_length=255)
    arrived_at = models.DateTimeField(default=timezone.now)
    departed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=OrderItem.STATUS_CHOICES)

    def __str__(self):
        return f"{self.order_item.tracking_number} - {self.status} @ {self.location}"