from django import forms
from .models import Order

# Order Placement Form
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['address', 'payment_method']
