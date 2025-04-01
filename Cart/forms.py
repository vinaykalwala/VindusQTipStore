from django import forms
from .models import Cart

# Cart Update Form
class CartUpdateForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['quantity']
