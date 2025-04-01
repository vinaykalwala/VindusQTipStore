from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel
    path("", home, name="home"),
    path('users/', include('Users.urls')),  # User authentication & profile
    path('products/', include('Products.urls')),  # Product listing & details
    path('cart/', include('Cart.urls')),  # Shopping cart
    path('orders/', include('Orders.urls')),  # Orders & tracking
    path('reviews/', include('Reviews.urls')),  # Product reviews
    path('recommendations/', include('Ai.urls')),  # AI-based recommendations
    path('analytics/', include('Analytics.urls')),  # Sales & product analytics
]

# Handling media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
