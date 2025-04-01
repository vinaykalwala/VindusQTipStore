from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, Wishlist
from Orders.models import Order  # Import Order model if not already imported
from Products.models import Product

from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart

def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('product', 'variant')
    
    for item in cart_items:
        product = item.product
        additional_price = item.variant.additional_price if item.variant else 0

        # ✅ Fix: Recalculate total price correctly
        discounted_price = product.discounted_price()  # Get discounted price
        item.total_price = (discounted_price + additional_price) * item.quantity  # ✅ Ensure correct price

    return render(request, 'cart/view_cart.html', {'cart_items': cart_items})

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Cart, Product

def update_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "increase":
            if cart_item.quantity < cart_item.product.stock:  # ✅ Stock check
                cart_item.quantity += 1
            else:
                messages.warning(request, f"Only {cart_item.product.stock} items available for {cart_item.product.name}.")
                return redirect('view-cart')

        elif action == "decrease":
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                messages.warning(request, "Minimum quantity is 1.")
                return redirect('view-cart')

        cart_item.save()
        messages.success(request, "Cart updated successfully!")

    return redirect('view-cart')

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Cart
from Products.models import Product, ProductVariant

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variant_id = request.POST.get("variant_id")  # ✅ Get selected variant from form
    variant = None

    if variant_id:  # If variant selected, fetch it
        variant = get_object_or_404(ProductVariant, id=variant_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user, product=product, variant=variant
    )

    if not created:
        cart_item.quantity += 1  # ✅ Increment quantity if already in cart

    cart_item.save()
    return redirect('view-cart')


# Remove from Cart
def remove_from_cart(request, cart_id):
    Cart.objects.filter(id=cart_id, user=request.user).delete()
    return redirect('view-cart')

# Remove All Cart Items After Order Placement
def clear_cart(request):
    Cart.objects.filter(user=request.user).delete()
    return redirect('view-cart')

# View Wishlist
def view_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'cart/view_wishlist.html', {'wishlist_items': wishlist_items})

# Add to Wishlist
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('view-wishlist')

# Remove from Wishlist
def remove_from_wishlist(request, wishlist_id):
    Wishlist.objects.filter(id=wishlist_id, user=request.user).delete()
    return redirect('view-wishlist')

# Move Item from Wishlist to Cart
def move_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Remove from wishlist
    Wishlist.objects.filter(user=request.user, product=product).delete()

    # Add to cart or increment quantity
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view-cart')
