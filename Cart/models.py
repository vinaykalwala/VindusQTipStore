from django.db import models
from django.forms import ValidationError
from Users.models import CustomUser
from Products.models import Product, ProductVariant

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # ✅ Store final price

    def save(self, *args, **kwargs):
        if self.variant:
            self.price = self.product.price + self.variant.additional_price  # ✅ Adjust price based on variant
        else:
            self.price = self.product.price
        

        if self.quantity > self.product.stock:
            self.quantity = self.product.stock
        
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.variant}) - ${self.price}"


# Wishlist Model
class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} (Wishlist)"
