from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import *
from Cart.models import *

# Place Order
from django.shortcuts import render, redirect
import razorpay
from django.conf import settings

def place_order(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items:
        return redirect('view-cart')  # Redirect back if cart is empty
    
    order_items = []

    # ✅ Check stock before placing order
    for item in cart_items:
        product = item.product
        if item.quantity > product.stock:
            messages.error(request, f"Only {product.stock} items available for {product.name}.")
            return redirect('view-cart')
    
    # ✅ Updated Price Calculation (Includes Variant and Discount)
    total_price = sum(
        (item.product.discounted_price() + (item.variant.additional_price if item.variant else 0)) * item.quantity 
        for item in cart_items
    )

    # ✅ Store cart details in session
    request.session['cart_data'] = {
        'total_price': str(total_price),
        'items': [
            {
                'product_id': item.product.id, 
                'variant_id': item.variant.id if item.variant else None,  # Store Variant ID
                'quantity': item.quantity
            } 
            for item in cart_items
        ]
    }

    # ✅ Clear the cart after order placement
    cart_items.delete()

    return redirect('select-payment-method')

from django.shortcuts import render, redirect
from Users.models import Address
from Products.models import Product, ProductVariant  # Import ProductVariant

def select_payment_method(request):
    cart_data = request.session.get('cart_data')

    if not cart_data:
        return redirect('view-cart')  # Redirect if no cart data

    addresses = Address.objects.filter(user=request.user)  # Get user's addresses
    selected_address_id = request.session.get("selected_address_id", None)

    cart_items = []
    total_price = 0  # Initialize total price calculation

    for item in cart_data.get('items', []):  # Use .get() to avoid KeyError
        try:
            product = Product.objects.get(id=item['product_id'])  # Get base product
            price = product.discounted_price()  # Get discounted price from Product model
            
            # Check if a variant exists and update price accordingly
            variant_id = item.get('variant_id')  # Assuming variant_id is stored in session
            variant = None
            if variant_id:
                variant = ProductVariant.objects.filter(id=variant_id, product=product).first()
                if variant:
                    price += variant.additional_price  # Add variant-specific price
            
            quantity = item['quantity']
            subtotal = price * quantity
            total_price += subtotal  # Accumulate total price

            cart_items.append({
                "product": product,
                "variant": variant,  # Store variant if available
                "price": price,
                "quantity": quantity,
                "subtotal": subtotal
            })
        except Product.DoesNotExist:
            continue  # Skip the product if it doesn't exist

    return render(request, 'orders/select_payment.html', {
        'total_price': total_price,  # Updated total price with discount
        'cart_items': cart_items,  # Pass cart items with variants
        'addresses': addresses,
        'selected_address_id': selected_address_id
    })

from django.shortcuts import render, redirect
from django.conf import settings
import razorpay
from .models import Order, Payment  # Make sure these models exist
from django.utils.timezone import now
from datetime import timedelta

# ✅ Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
def razorpay_payment(request):
    cart_data = request.session.get('cart_data')

    if not cart_data:
        return redirect('view-cart')  # Ensures users are redirected if the cart is empty

    total_price = cart_data.get('total_price', 0)

    # Check if Razorpay order already exists
    if not request.session.get('razorpay_order_id'):
        razorpay_order = razorpay_client.order.create({
            "amount": int(float(total_price) * 100),  
            "currency": "INR",
            "payment_capture": "1"
        })
        # Store Razorpay order ID in session
        request.session['razorpay_order_id'] = razorpay_order['id']

    return render(request, 'orders/razorpay_payment.html', {
        'cart_data': cart_data,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': request.session['razorpay_order_id'],
        'amount': int(float(total_price) * 100),
        'currency': 'INR'
    })


def cod_payment(request):
    cart_data = request.session.get('cart_data')
    selected_address_id = request.session.get("selected_address_id")

    if not cart_data:
        return redirect('view-cart')

    selected_address = Address.objects.get(id=selected_address_id)

    # Create Order for COD immediately with discounted price
    order = Order.objects.create(
        user=request.user,
        address=selected_address,
        total_price=cart_data['total_price'],
        payment_method='COD',
        status='Pending',
        payment_status='Pending'
    )

    for item in cart_data['items']:
        product = Product.objects.get(id=item['product_id'])
        variant = ProductVariant.objects.get(id=item['variant_id']) if item['variant_id'] else None

        item_price = product.discounted_price() + (variant.additional_price if variant else 0)

        OrderItem.objects.create(
            order=order, 
            product=product, 
            variant=variant,
            quantity=item['quantity'], 
            price=item_price,
            status='Processing',
            expected_delivery_date=now().date() + timedelta(days=3)
        )

    Payment.objects.create(
        order=order,
        razorpay_order_id=None,
        status="Pending",  # COD payments are pending until cash is received
    )

    del request.session['cart_data']

    return redirect(reverse("order-summary"))

# Order Detail
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'orders/order_detail.html', {'order': order})

# Track Order
def track_order(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'orders/track_order.html', {'order': order})


def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_confirmation.html', {'order': order})

from django.views.decorators.csrf import csrf_exempt
from Products.models import Product, ProductVariant  # Import ProductVariant

from razorpay.errors import SignatureVerificationError

@csrf_exempt
def razorpay_callback(request):
    if request.method == "POST":
        # Log all POST data to help with debugging
        data = request.POST
        print("POST data received:", data)  # Logs all the received POST data
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        if not (razorpay_order_id and razorpay_payment_id and razorpay_signature):
            print("Missing required Razorpay parameters.")
            return render(request, "orders/payment_failed.html", {"error": "Invalid Razorpay response"})

        cart_data = request.session.get('cart_data')
        selected_address_id = request.session.get("selected_address_id")

        if not cart_data or not selected_address_id:
            print("Cart data or selected address missing.")
            return redirect('view-cart')

        try:
            selected_address = Address.objects.get(id=selected_address_id)

            # Verify payment using Razorpay utility
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
            except SignatureVerificationError as e:
                print(f"Signature verification failed: {e}")
                return render(request, "orders/payment_failed.html", {"error": "Payment verification failed. Signature mismatch."})

            # If signature verification is successful, create order
            order = Order.objects.create(
                user=request.user,
                address=selected_address,
                total_price=cart_data['total_price'],
                payment_method='Razorpay',
                status='pending',
                payment_status='Completed',
                razorpay_order_id=razorpay_order_id,
                razorpay_payment_id=razorpay_payment_id,
                razorpay_signature=razorpay_signature
            )

            # Add items to the order
            for item in cart_data['items']:
                product = Product.objects.get(id=item['product_id'])
                variant = ProductVariant.objects.get(id=item['variant_id']) if item.get('variant_id') else None
                item_price = product.discounted_price() + (variant.additional_price if variant else 0)

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    variant=variant,
                    quantity=item['quantity'],
                    price=item_price,
                    status='Processing',
                    expected_delivery_date=now().date() + timedelta(days=3)
                )

            # Record payment
            payment = Payment.objects.create(
                order=order,
                razorpay_order_id=razorpay_order_id,
                razorpay_payment_id=razorpay_payment_id,
                razorpay_signature=razorpay_signature,
                status="paid"
            )

            # Clear cart after successful payment
            if payment.status == "paid":
                request.session.pop('cart_data', None)
                request.session.pop('selected_address_id', None)
                request.session.pop('razorpay_order_id', None)

            return redirect(reverse("order-summary"))

        except SignatureVerificationError as e:
            print(f"Signature verification failed with error: {e}")
            return render(request, "orders/payment_failed.html", {"error": "Payment verification failed. Please try again."})

    return redirect('view-cart')

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Order, OrderItem

@login_required
def order_summary(request):
    user = request.user
    message = None  # Initialize message variable

    if user.is_superuser:
        orders = Order.objects.prefetch_related('items__product').order_by('-created_at')
    elif user.role == 'vendor':
        vendor_orders = OrderItem.objects.filter(product__vendor=user).values_list('order_id', flat=True).distinct()
        orders = Order.objects.filter(id__in=vendor_orders).prefetch_related('items__product').order_by('-created_at')
    else:
        orders = Order.objects.filter(user=user).prefetch_related('items__product').order_by('-created_at')

    for order in orders:
        order.discount_amount = sum(
            (item.product.price - item.product.discounted_price()) * item.quantity
            for item in order.items.all()
        )

        for item in order.items.all():
            item.can_cancel = item.status in ["Processing", "Pending"]
            
            # Ensure delivered_date is not None before doing date calculations
            if item.delivered_date:
                days_since_delivery = (timezone.now().date() - item.delivered_date).days
            else:
                days_since_delivery = None

            item.can_return_refund = (
                item.status == "Delivered" and 
                item.product.return_eligible and 
                days_since_delivery is not None and days_since_delivery <= item.product.return_days
            )

            item.can_replace = (
                item.status == "Delivered" and 
                item.product.replacement_eligible and 
                days_since_delivery is not None and days_since_delivery <= item.product.return_days
            )

    # ✅ Handle order cancellation request
    if request.method == "POST" and "cancel_order" in request.POST:
        order_id = request.POST.get("order_id")
        order = get_object_or_404(Order, id=order_id, user=user)
        message = order.cancel_order()  # Call the cancellation method and get message

    return render(request, 'orders/order_summary.html', {'orders': orders, 'message': message})


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.exceptions import ValidationError
from .models import BankDetail, OrderItem, Order

@csrf_exempt
def add_bank_details(request):
    """ ✅ API for users to add/update their bank details """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user

            bank_details, created = BankDetail.objects.get_or_create(user=user)

            bank_details.account_holder_name = data.get("account_holder_name")
            bank_details.bank_name = data.get("bank_name")
            bank_details.account_number = data.get("account_number")
            bank_details.ifsc_code = data.get("ifsc_code")
            bank_details.branch_name = data.get("branch_name")
            bank_details.save()

            return JsonResponse({"message": "Bank details added successfully!"}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from .models import OrderItem, Order

def cancel_order_item(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order = order_item.order  # Get the parent order

    if order_item.status in ["Cancelled", "Delivered"]:
        messages.error(request, "This item cannot be canceled.")
        return redirect("order-summary")

    with transaction.atomic():
        order_item.cancel_item()  # Cancel the item

        # ✅ If this was the **only** item in the order, cancel the entire order
        if order.items.filter(status__in=['Processing', 'Shipped', 'Out for Delivery']).count() == 0:
            order.cancel_order()
            messages.success(request, "All items in the order were canceled, so the entire order is canceled.")
        else:
            # ✅ Process partial refund for the canceled item
            if order.payment_method == "Razorpay" and order.payment_status == "Completed":
                refund_message = order.process_refund(order_item.subtotal())  
                messages.success(request, refund_message)
            else:
                messages.success(request, "Order item has been canceled successfully.")

    return redirect("order-summary")

def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status in ["Cancelled", "Delivered"]:
        messages.error(request, "Order cannot be canceled.")
        return redirect("order-summary")

    with transaction.atomic():
        order.cancel_order()  # Cancel order and restore stock

        # ✅ Process full refund if prepaid
        if order.payment_method == "Razorpay" and order.payment_status == "Completed":
            refund_message = order.process_refund()
            messages.success(request, refund_message)
        else:
            messages.success(request, "Order has been canceled successfully.")

    return redirect("order-summary")
