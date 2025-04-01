from django.db import models
from Users.models import CustomUser

class SalesReport(models.Model):
    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'vendor'})
    total_sales = models.DecimalField(max_digits=12, decimal_places=2)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor.username} - {self.date}"
