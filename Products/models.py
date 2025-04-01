from django.db import models
from Users.models import CustomUser
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)  
    image = models.ImageField(upload_to='categories/', default='categories/default.png')  # Add image field

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)  
    image = models.ImageField(upload_to='subcategories/', default='subcategories/default.png')  # Add image field

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        unique_together = ('category', 'name')

    def __str__(self):
        return f"{self.category.name} - {self.name}"



from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.db.models import Avg
from decimal import Decimal

class Product(models.Model):
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # CustomUser model
        on_delete=models.CASCADE,
        related_name="products",
        limit_choices_to={'role': 'vendor'},  # Only vendors can be selected
        null=True, blank=True  # Allow blank vendor (if not logged in as vendor)
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="products", blank=True, null=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)  # Auto-generated for SEO-friendly URLs
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', default='products/default.png')  # Default image
    is_top_featured = models.BooleanField(default=False)
    discount = models.PositiveIntegerField(default=0, help_text="Discount percentage (e.g. 10 for 10%)")
    created_at = models.DateTimeField(auto_now_add=True)
    return_eligible = models.BooleanField(default=True)
    return_days = models.PositiveIntegerField(default=7)

    replacement_eligible = models.BooleanField(default=True)
    replacement_days = models.PositiveIntegerField(default=7)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  # Auto-generate slug from name
        super().save(*args, **kwargs)
    
    

    def discounted_price(self):
        """ ✅ Calculate the discounted price with Decimal precision """
        if self.discount > 0:
            discount_factor = Decimal(str(1 - (self.discount / 100)))  # Convert to Decimal
            return self.price * discount_factor  # Multiply with Decimal
        return self.price


    def average_rating(self):
        return self.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0 

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    size = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='product_variants/', default='product_variants/default.png')  # Add image field

    def __str__(self):
        return f"{self.product.name} - {self.color} / {self.size}"



from django.db import models

class Slider(models.Model):
    image = models.ImageField(upload_to='sliders/')
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title if self.title else "Slider Image"
