from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserActivity
from Orders.models import Order, OrderItem
from Cart.models import Cart, Wishlist
from Products.models import Product
from .ml_model import train_recommendation_model

### 1️⃣ Log user activity when an order is placed ###
@receiver(post_save, sender=Order)
def create_order_activity(sender, instance, created, **kwargs):
    """Log when a user places an order."""
    if created:
        print(f"🛒 Order placed by {instance.user}")  # Debugging log

        # Fetch all products related to the order
        order_items = OrderItem.objects.filter(order=instance)
        for item in order_items:
            _, created_activity = UserActivity.objects.get_or_create(
                user=instance.user,
                product=item.product,
                activity_type="ordered",
                defaults={
                    "category": item.product.category,
                    "subcategory": item.product.subcategory,
                }
            )
            if not created_activity:
                print(f"⚠️ UserActivity already exists — skipping ordered for {item.product}")


        # Trigger AI model training
        train_recommendation_model(instance.user)


### 2️⃣ Log user activity when a product is added to wishlist ###
@receiver(post_save, sender=Wishlist)
def create_wishlist_activity(sender, instance, created, **kwargs):
    """Log when a user adds a product to the wishlist."""
    if created:
        print(f"💙 Wishlist updated: {instance.user} added {instance.product}")  # Debugging

        _, created_activity = UserActivity.objects.get_or_create(
            user=instance.user,
            product=instance.product,
            activity_type="wishlist",
            defaults={
                "category": instance.product.category,
                "subcategory": instance.product.subcategory,
            }
        )
        if not created_activity:
            print(f"⚠️ UserActivity already exists — skipping wishlist for {instance.product}")


### 3️⃣ Log user activity when a product is added to the cart ###
@receiver(post_save, sender=Cart)
def create_cart_activity(sender, instance, created, **kwargs):
    """Log when a user adds a product to the cart."""
    if created:
        print(f"🛍️ Cart updated: {instance.user} added {instance.product}")

        _, created_activity = UserActivity.objects.get_or_create(
            user=instance.user,
            product=instance.product,
            activity_type="cart",
            defaults={
                "category": instance.product.category,
                "subcategory": instance.product.subcategory,
            }
        )
        if not created_activity:
            print("⚠️ UserActivity already exists — skipping cart activity.")


### 4️⃣ Log user activity when a product is viewed ###
def track_product_view(user, product):
    """Logs when a user views a product (ensuring uniqueness)."""
    print(f"👀 {user} viewed {product.name}")  # Debugging

    _, created_activity = UserActivity.objects.get_or_create(
        user=user,
        product=product,
        activity_type="view",
        defaults={  
            "category": product.category,
            "subcategory": product.subcategory,
        }
    )
    if not created_activity:
        print(f"⚠️ UserActivity already exists — skipping view for {product.name}")


### 5️⃣ Generate recommendations when user activity is logged ###
@receiver(post_save, sender=UserActivity)
def generate_recommendations(sender, instance, created, **kwargs):
    """Automatically update recommendations when user activity is recorded."""
    if created:
        print(f"🔄 Signal triggered: Generating recommendations for {instance.user}")  # Debugging
        train_recommendation_model(instance.user)
