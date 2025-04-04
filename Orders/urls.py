from django.urls import path
from .views import *

urlpatterns = [
    path('place/', place_order, name='place-order'),
    path('select-payment/', select_payment_method, name='select-payment-method'),  # ✅ NEW
    path('razorpay-payment/', razorpay_payment, name='razorpay-payment'),
    path('razorpay-callback/', razorpay_callback, name='razorpay-callback'),
    path('cod-payment/', cod_payment, name='cod-payment'),
    path('order-confirmation/<int:order_id>/', payment_success, name='order-confirmation'),
    path('<int:order_id>/', order_detail, name='order-detail'),
    path('track/<int:order_id>/', track_order, name='track-order'),
    path("order-summary/", order_summary, name="order-summary"),
    path('orders/', orders_page, name='orders_page'),
    
    path('add-bank-details/', add_bank_details, name="add_bank_details"),
    path('cancel-order/<int:order_id>/', cancel_order, name='cancel_order'),
    path('cancel-item/<int:order_item_id>/', cancel_order_item, name='cancel_order_item'),

    
]
