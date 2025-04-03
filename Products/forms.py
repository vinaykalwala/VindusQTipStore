from django import forms
from .models import Product, Category, ProductVariant, SubCategory

from django import forms
from .models import Product
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'subcategory', 'name', 'description', 'price', 'discount', 'stock', 'image']  # ✅ Add discount

    def save(self, user=None, commit=True):
        product = super().save(commit=False)
        if user and user.role == 'vendor':  # Assign vendor automatically
            product.vendor = user
        if commit:
            product.save()
        return product

# Category Form
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']

# SubCategory Form
class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['name', 'category', 'slug']

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['size', 'color', 'additional_price', 'image']

