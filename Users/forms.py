from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Address

class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text="Required")
    last_name = forms.CharField(max_length=30, required=True, help_text="Required")
    phone = forms.CharField(max_length=15, required=True)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'profile_picture', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'customer'  # Assign role
        if commit:
            user.save()
        return user


class VendorRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text="Required")
    last_name = forms.CharField(max_length=30, required=True, help_text="Required")
    phone = forms.CharField(max_length=15, required=True)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'profile_picture', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'vendor'  # Assign role
        if commit:
            user.save()
        return user


class DeliveryPersonRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text="Required")
    last_name = forms.CharField(max_length=30, required=True, help_text="Required")
    phone = forms.CharField(max_length=15, required=True)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'profile_picture', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'delivery'  # Assign role
        if commit:
            user.save()
        return user
class DeliveryAdminRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text="Required")
    last_name = forms.CharField(max_length=30, required=True, help_text="Required")
    phone = forms.CharField(max_length=15, required=True)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'profile_picture', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'DeliveryAdmin'  # Assign role
        if commit:
            user.save()
        return user

# User Login Form
class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

# Address Form (Corrected)
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone_number', 'street_address', 'city', 'state', 'country', 'postal_code', 'is_default']


from django.contrib.auth.forms import PasswordChangeForm

# Forgot Password Form
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

# OTP Form
class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6)

# Reset Password Form
class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
