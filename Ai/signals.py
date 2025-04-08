from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserActivity
from Orders.models import Order, OrderItem
from Cart.models import Cart, Wishlist
from Products.models import Product
from .ml_model import train_recommendation_model

### 🔒 Helper to safely get or create a unique user activity ###
def safe_get_or_create_activity(user, product, activity_type):
    """Ensures only one activity per user/product/type, prevents MultipleObjectsReturned."""
    existing = UserActivity.objects.filter(
        user=user,
        product=product,
        activity_type=activity_type
    ).first()
    
    if existing:
        print(f"⚠️ UserActivity already exists — skipping {activity_type} for {product.name}")
        return existing, False
    
    activity = UserActivity.objects.create(
        user=user,
        product=product,
        activity_type=activity_type,
        category=product.category,
        subcategory=product.subcategory,
    )
    print(f"✅ Created {activity_type} activity for {user} - {product.name}")
    return activity, True


### 1️⃣ Log user activity when an order is placed ###
@receiver(post_save, sender=Order)
def create_order_activity(sender, instance, created, **kwargs):
    if created:
        # print(f"🛒 Order placed by {instance.user}")

        order_items = OrderItem.objects.filter(order=instance)
        for item in order_items:
            safe_get_or_create_activity(
                user=instance.user,
                product=item.product,
                activity_type="ordered"
            )

        train_recommendation_model(instance.user)


### 2️⃣ Log user activity when a product is added to wishlist ###
@receiver(post_save, sender=Wishlist)
def create_wishlist_activity(sender, instance, created, **kwargs):
    if created:
        # print(f"💙 Wishlist updated: {instance.user} added {instance.product}")

        safe_get_or_create_activity(
            user=instance.user,
            product=instance.product,
            activity_type="wishlist"
        )


### 3️⃣ Log user activity when a product is added to the cart ###
@receiver(post_save, sender=Cart)
def create_cart_activity(sender, instance, created, **kwargs):
    if created:
        # print(f"🛍️ Cart updated: {instance.user} added {instance.product}")

        safe_get_or_create_activity(
            user=instance.user,
            product=instance.product,
            activity_type="cart"
        )


### 4️⃣ Log user activity when a product is viewed ###
def track_product_view(user, product):
    # print(f"👀 {user} viewed {product.name}")

    safe_get_or_create_activity(
        user=user,
        product=product,
        activity_type="view"
    )


### 5️⃣ Generate recommendations when user activity is logged ###
@receiver(post_save, sender=UserActivity)
def generate_recommendations(sender, instance, created, **kwargs):
    if created:
        # print(f"🔄 Signal triggered: Generating recommendations for {instance.user}")
        train_recommendation_model(instance.user)
