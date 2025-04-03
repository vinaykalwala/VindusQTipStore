from django.urls import path
from .views import *

app_name = "Products"

urlpatterns = [
    path("", product_list, name="product_list"),
    path("add/", add_product, name="add_product"),  # ✅ Add Product URL
    path("<slug:product_slug>/", product_detail, name="product_detail"),
    path("<int:product_id>/delete/", delete_product, name="delete_product"),
    path("category/<slug:slug>/", category_products, name="category_products"),  # ✅ Category Products URL
    path("subcategory/<slug:slug>/", subcategory_products, name="subcategory_products"),  # ✅ Subcategory Products URL
    path('top-featured/', featured_products, name='top_featured_products'),
    path('product/edit/<int:product_id>/', edit_product, name='edit_product'),
    path('variant/edit/<int:variant_id>/', edit_variant, name='edit_variant'),
]
