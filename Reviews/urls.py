from django.urls import path
from .views import *

urlpatterns = [
    path('add/<int:product_id>/', add_review, name='add-review'),
    # path('edit/<int:review_id>/', edit_review, name='edit-review'),
    # path('delete/<int:review_id>/', delete_review, name='delete-review'),
]
