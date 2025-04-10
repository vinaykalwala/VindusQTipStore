from django.urls import path
from .views import *

app_name = "Products"

urlpatterns = [
    path("", product_list, name="product_list"),
    path("add/", add_product, name="add_product"),  # ✅ Add Product URL
    path("<int:product_id>/delete/", delete_product, name="delete_product"),
    path("category/<slug:slug>/", category_products, name="category_products"),  # ✅ Category Products URL
    path("subcategory/<slug:slug>/", subcategory_products, name="subcategory_products"),  # ✅ Subcategory Products URL
    path('top-featured/', featured_products, name='top_featured_products'),
    path('product/edit/<int:product_id>/', edit_product, name='edit_product'),
    path('variant/edit/<int:variant_id>/', edit_variant, name='edit_variant'),
    path('product/<int:product_id>/', view_product, name='view_product'),
    path('variant/<int:variant_id>/', view_variant, name='view_variant'),
    path('manage/', manage_products, name='manage_products'),
    path('delete_product/<int:product_id>/', delete_product, name='delete_product'),
    path('delete_variant/<int:variant_id>/', delete_variant, name='delete_variant'),
    path('search/', search_view, name='search'),
    path('low-stock/', low_stock_products, name='low_stock_products'),
    path("<slug:product_slug>/", product_detail, name="product_detail"),

    
]
