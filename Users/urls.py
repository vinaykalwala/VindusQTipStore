from django.urls import path
from .views import *

urlpatterns = [
    path('register/customer/', register_customer, name='register_customer'),
    path('register/vendor/', register_vendor, name='register_vendor'),
    path('register/delivery/', register_delivery_person, name='register_delivery_person'),
    path('register/delivery-admin/', register_delivery_admin, name='register_delivery_admin'),
    path('verify-registration-otp/', verify_registration_otp, name='verify_registration_otp'),
    path('login/', login_view, name='user-login'),
    path('logout/', logout_view, name='user-logout'),
    path('profile/', profile, name='user-profile'),
    path('addresses/', address_list, name='address-list'),
    path('addresses/add/', add_address, name='add-address'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('select-address/', select_address, name='select-address'),
    path('add-address/', add_address, name='add-address'),
    path('change-password/', change_password, name='change_password'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('reset-password/',reset_password, name='reset_password'),
    path('seller',sellerpage, name='sellerpage'),
]
