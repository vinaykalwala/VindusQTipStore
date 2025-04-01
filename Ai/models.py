from django.db import models
from Users.models import CustomUser
from Products.models import Product

# AI-Based Product Recommendations
class Recommendation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    score = models.FloatField()  # AI-generated score
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation for {self.user.username}: {self.product.name} ({self.score})"

from django.db import models
from Users.models import CustomUser
from Products.models import Product, Category, SubCategory

class UserActivity(models.Model):
    VIEW = "view"
    WISHLIST = "wishlist"
    CART = "cart"
    PURCHASE = "purchase"

    ACTIVITY_CHOICES = [
        (VIEW, "Viewed"),
        (WISHLIST, "Added to Wishlist"),
        (CART, "Added to Cart"),
        (PURCHASE, "Purchased"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product', 'activity_type')

    def __str__(self):
        return f"{self.user.username} {self.get_activity_type_display()} {self.product.name}"
