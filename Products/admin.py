from django.contrib import admin
from .models import Category, SubCategory, Product, ProductVariant

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product)
admin.site.register(ProductVariant)

from django.contrib import admin
from .models import Slider

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_at']
