from django.urls import path
from .views import *

urlpatterns = [
    path('', recommendations, name='personalized-recommendations'),
    path("recommendations/<int:user_id>/", get_recommendations, name="get_recommendations"),
]
