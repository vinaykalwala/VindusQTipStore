# Existing imports and models remain unchanged
import calendar
from django.db import models
from django.conf import settings
from django.utils import timezone

# Your existing models: Order, OrderItem, Product, ProductVariant, etc., stay as they are.

# Optional: SalesReport model for precomputed data
class SalesReport(models.Model):
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'vendor'},
        null=True, blank=True  # Null for platform-wide reports
    )
    year = models.PositiveIntegerField(null=True,blank=True)
    month = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 13)])  # 1=Jan, 12=Dec
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    total_orders = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('vendor', 'year', 'month')  # Unique per vendor/month

    def __str__(self):
        month_name = calendar.month_name[self.month]
        return f"{self.vendor.username if self.vendor else 'Platform'} - {month_name} {self.year}"