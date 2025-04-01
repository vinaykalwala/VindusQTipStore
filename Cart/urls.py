from django.urls import path
from .views import *

urlpatterns = [
    path('viewcart/', view_cart, name='view-cart'),
    path('cart/update/<int:item_id>/', update_cart, name='update-cart'),
    path('add/<int:product_id>/', add_to_cart, name='add-to-cart'),
    path('remove/<int:cart_id>/', remove_from_cart, name='remove-from-cart'),
    path('clear-cart/', clear_cart, name='clear-cart'),  # ✅ Added clear cart endpoint
    path('add-to-wishlist/<int:product_id>/', add_to_wishlist, name='add-to-wishlist'),
    path('remove-from-wishlist/<int:wishlist_id>/', remove_from_wishlist, name='remove-from-wishlist'),  # ✅ Added remove wishlist
    path('move-to-cart/<int:product_id>/', move_to_cart, name='move-to-cart'),  # ✅ Move from wishlist to cart
    path('viewwishlist/', view_wishlist, name='view-wishlist'),
]
