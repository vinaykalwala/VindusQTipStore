from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Address



admin.site.register(CustomUser)
admin.site.register(Address)
