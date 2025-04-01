from django import forms
from .models import UserPreference

# AI Preferences Form
class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['preferred_category', 'preferred_price_range']
