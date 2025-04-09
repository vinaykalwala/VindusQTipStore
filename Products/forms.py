from django import forms
from .models import Product, Category, ProductVariant, SubCategory

from django import forms
from .models import Product
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

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
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),  # Show all products
        empty_label="Select Product",
        widget=forms.Select
    )

    class Meta:
        model = ProductVariant
        fields = ['product', 'size', 'color', 'additional_price', 'image']


class SearchForm(forms.Form):
    query = forms.CharField(max_length=255, label='', widget=forms.TextInput(attrs={
        'placeholder': 'Search products, categories, or subcategories...',
        'class': 'form-control',
    }))
