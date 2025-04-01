from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register, name='user-register'),
    path('login/', login_view, name='user-login'),
    path('logout/', logout_view, name='user-logout'),
    path('profile/', profile, name='user-profile'),
    path('addresses/', address_list, name='address-list'),
    path('addresses/add/', add_address, name='add-address'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('select-address/', select_address, name='select-address'),
    path('add-address/', add_address, name='add-address'),
]
