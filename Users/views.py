from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from Ai.models import Recommendation
from Orders.models import OrderItem
from .models import CustomUser, Address
from .forms import DeliveryAdminRegistrationForm, UserLoginForm, AddressForm
from .forms import CustomerRegistrationForm, VendorRegistrationForm, DeliveryPersonRegistrationForm
import random
from django.core.mail import send_mail
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CustomerRegistrationForm, VendorRegistrationForm, DeliveryPersonRegistrationForm
from .models import CustomUser

import random
from django.core.mail import send_mail
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from .forms import CustomerRegistrationForm, VendorRegistrationForm, DeliveryPersonRegistrationForm

# Function to send OTP via email
def send_otp(email, request):
    otp = get_random_string(6, allowed_chars='1234567890')  # Generate 6-digit OTP
    request.session['otp'] = otp  # Store OTP in session
    request.session['email'] = email  # Store email

    subject = "Your OTP for Registration"
    message = f"Your OTP for account registration is {otp}. Please do not share it with anyone. If you did not receive the email, please check your Spam or Junk folder."
    sender_email = "durgaprakash1102@gmail.com"  # Replace with your SMTP email

    send_mail(subject, message, sender_email, [email])

# Customer Registration View (with OTP)
def register_customer(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            request.session['user_data'] = form.cleaned_data  # Store user data in session
            send_otp(form.cleaned_data['email'], request)  # Send OTP
            messages.success(request, "OTP sent to your email. Please verify.")
            return redirect('verify_registration_otp')  # Redirect to OTP verification
    else:
        form = CustomerRegistrationForm()

    return render(request, 'users/register_customer.html', {'form': form})

# Vendor Registration View (with OTP)
def register_vendor(request):
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            request.session['user_data'] = form.cleaned_data  # Store user data in session
            send_otp(form.cleaned_data['email'], request)  # Send OTP
            messages.success(request, "OTP sent to your email. Please verify.")
            return redirect('verify_registration_otp')  # Redirect to OTP verification
    else:
        form = VendorRegistrationForm()

    return render(request, 'users/register_vendor.html', {'form': form})

# Delivery Person Registration View (with OTP)
def register_delivery_person(request):
    if request.method == 'POST':
        form = DeliveryPersonRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            request.session['user_data'] = form.cleaned_data  # Store user data in session
            send_otp(form.cleaned_data['email'], request)  # Send OTP
            messages.success(request, "OTP sent to your email. Please verify.")
            return redirect('verify_registration_otp')  # Redirect to OTP verification
    else:
        form = DeliveryPersonRegistrationForm()

    return render(request, 'users/register_delivery.html', {'form': form})

def register_delivery_admin(request):
    if request.method == 'POST':
        form = DeliveryAdminRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            request.session['user_data'] = form.cleaned_data  # Store temporarily in session
            send_otp(form.cleaned_data['email'], request)  # Send OTP to email
            messages.success(request, "OTP sent to your email. Please verify.")
            return redirect('verify_registration_otp')  # Redirect to OTP verification view
    else:
        form = DeliveryAdminRegistrationForm()

    return render(request, 'users/register_delivery_admin.html', {'form': form})

# OTP Verification for Registration
def verify_registration_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        email = request.session.get('email')
        user_data = request.session.get('user_data')

        if entered_otp == stored_otp:
            user_model = get_user_model()
            existing_user = user_model.objects.filter(email=email).first()
            if existing_user:
                messages.error(request, "User with this email already exists.")
                return redirect('home')  # Redirect to appropriate registration

            # Create user after OTP verification
            role = user_data.get('role', 'customer')  # Default to customer
            if role == 'vendor':
                form = VendorRegistrationForm(user_data)
            elif role == 'delivery':
                form = DeliveryPersonRegistrationForm(user_data)
            else:
                form = CustomerRegistrationForm(user_data)

            if form.is_valid():
                user = form.save()
                login(request, user)  # Log the user in
                del request.session['otp']
                del request.session['email']
                del request.session['user_data']
                messages.success(request, "Registration successful!")
                return redirect('dashboard')
            else:
                messages.error(request, "Something went wrong. Please try again.")
                return redirect('home')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'users/verify_registration_otp.html')

# User Login
def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

# User Logout
@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    user = request.user
    addresses = Address.objects.filter(user=user)  # Fetch all addresses for the logged-in user
    return render(request, 'users/profile.html', {
        'user': user,
        'addresses': addresses  # Pass addresses to the template
    })
# Address Management
@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'users/address_list.html', {'addresses': addresses})

@login_required
def add_address(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address added successfully!")
            return redirect('users:address_list')
    else:
        form = AddressForm()
    return render(request, 'users/add_address.html', {'form': form})



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from Products.models import Product, Category, SubCategory, Slider
from Ai.models import Recommendation
from Reviews.models import Review
from django.contrib.auth import get_user_model
from django.db.models import Prefetch, Avg
import random
from datetime import timedelta, datetime


User = get_user_model()

@login_required
def dashboard_view(request):
    user = request.user
    sliders = None
    subcategories = None
    categories = None
    top_featured_products = []
    recently_viewed_products = []
    recommended_products = set()
    top_discount_deals = []
    final_products = []
    vendor_products = None
    vendors_with_products = None 
    unassociated_products=[]
    order_items=[]
    delivery_people=[]

    if user.is_superuser:
        template = 'dashboard/admin_dashboard.html'
        vendors = User.objects.filter(role='vendor')
        vendors_with_products = vendors.prefetch_related(
            Prefetch('products', queryset=Product.objects.all().order_by('-created_at'))
        )
        unassociated_products = Product.objects.filter(vendor__isnull=True)

    elif user.role == 'vendor':
        template = 'dashboard/vendor_dashboard.html'
        vendor_products = Product.objects.filter(vendor=user).order_by('-created_at')

    elif user.role == 'customer':
        template = 'dashboard/customer_dashboard.html'

        sliders = Slider.objects.order_by('-uploaded_at')[:4]
        subcategories = SubCategory.objects.all()
        categories = Category.objects.all()
        top_featured_products = list(Product.objects.filter(is_top_featured=True))
        top_discount_deals = list(Product.objects.filter(discount__gt=0).order_by('-discount')[:6])

        for product in top_featured_products:
            product.final_price = product.discounted_price()
            reviews = Review.objects.filter(product=product)
            product.avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            product.total_reviews = reviews.count()

        for product in top_discount_deals:
            product.final_price = product.price - (product.price * product.discount / 100)
            reviews = Review.objects.filter(product=product)
            product.avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            product.total_reviews = reviews.count()
            product.auction_end_time = datetime.now() + timedelta(hours=random.randint(1, 6), minutes=random.randint(0, 59))

        recently_viewed_ids = request.session.get('recently_viewed', [])
        recently_viewed_products = list(Product.objects.filter(id__in=recently_viewed_ids))
        for product in recently_viewed_products:
            reviews = Review.objects.filter(product=product)
            product.avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            product.total_reviews = reviews.count()

        recommended_queryset = Recommendation.objects.filter(user=user).select_related('product').order_by('-created_at')[:5]
        for rec in recommended_queryset:
            recommended_products.add(rec.product)

        seen_subcategories = set()
        additional_products = set()

        for product in list(recommended_products):
            if product.subcategory_id not in seen_subcategories:
                seen_subcategories.add(product.subcategory_id)

                one_extra_product = Product.objects.filter(subcategory_id=product.subcategory_id) \
                    .exclude(id__in=[p.id for p in recommended_products]) \
                    .order_by('-created_at') \
                    .first()

                three_more_products = list(
                    Product.objects.filter(subcategory_id=product.subcategory_id)
                    .exclude(id__in=[p.id for p in recommended_products.union(additional_products)])
                    .order_by('-created_at')[:3]
                )

                if one_extra_product:
                    additional_products.add(one_extra_product)

                additional_products.update(three_more_products)

        final_products = list(recommended_products.union(additional_products))
        final_products = sorted(final_products, key=lambda p: p.created_at, reverse=True)[:10]

        # Add avg_rating and total_reviews to each final recommended product
        for product in final_products:
            reviews = Review.objects.filter(product=product)
            product.avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            product.total_reviews = reviews.count()

    elif user.role == 'delivery':
        template = 'dashboard/delivery_dashboard.html'
        query = request.GET.get('q', '').strip()
        user = request.user
        if user.role != 'delivery':
            return JsonResponse({'error': 'Access denied'}, status=403)

        order_items = OrderItem.objects.filter(delivery_person=user).order_by('-id')
        if query:
            order_items = order_items.filter(tracking_number__icontains=query)

        for item in order_items:
            item.STATUS_CHOICES = OrderItem.STATUS_CHOICES
        
        for item in order_items:
            item.is_delivered = (item.status == "delivered")

    elif user.role == 'DeliveryAdmin':
        template = 'dashboard/default_dashboard.html'
        query = request.GET.get('q', '').strip()
        
        order_items = OrderItem.objects.select_related('order', 'product', 'delivery_person').order_by('-id')

        if query:
            order_items = order_items.filter(tracking_number__icontains=query)
        
        order_items = order_items.all()
        delivery_people = CustomUser.objects.filter(role='delivery')
        for item in order_items:
            item.STATUS_CHOICES = OrderItem.STATUS_CHOICES
        
        for item in order_items:
            item.is_delivered = (item.status == "delivered")
    else :
        return redirect('user-login')


    return render(request, template, {
        'user': user,
        'sliders': sliders,
        'subcategories': subcategories,
        'categories': categories,
        'top_featured_products': top_featured_products,
        'top_discount_deals': top_discount_deals,
        'recently_viewed_products': recently_viewed_products,
        'recommended_products': final_products,
        'vendor_products': vendor_products,
        'vendors_with_products': vendors_with_products,
        'unassociated_products': unassociated_products,
        'order_items': order_items,
        'delivery_people': delivery_people
    })


def select_address(request):
    if request.method == "POST":
        address_id = request.POST.get("selected_address")
        request.session["selected_address_id"] = address_id  # Store selected address in session
        return redirect("select-payment-method")
    return redirect("select-payment-method")


def add_address(request):
    if request.method == "POST":
        new_address = Address.objects.create(
            user=request.user,
            full_name=request.POST["full_name"],
            phone_number=request.POST["phone_number"],
            street_address=request.POST["street_address"],
            city=request.POST["city"],
            state=request.POST["state"],
            country=request.POST["country"],
            postal_code=request.POST["postal_code"]
        )
        request.session["selected_address_id"] = str(new_address.id)  # Auto-select new address
        return redirect("select-payment-method")
    return redirect("select-payment-method")


from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.crypto import get_random_string
from .forms import ForgotPasswordForm, OTPForm, ResetPasswordForm

# Password Change View (logged-in user)
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('user-profile')  # Redirect to profile or any other page
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'users/change_password.html', {'form': form})

from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from .forms import ForgotPasswordForm, OTPForm, ResetPasswordForm

# Forgot Password Request (Generate OTP)
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = get_user_model().objects.filter(email=email).first()

        if user:
            otp = get_random_string(6, allowed_chars='1234567890')  # Generate OTP
            # Send OTP to user's email (real email delivery using SMTP)
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is {otp}.',
                'no-reply@yourdomain.com',  # You can use any placeholder here
                [email],
                fail_silently=False,  # Set this to True in case you want to ignore errors
            )
            request.session['otp'] = otp
            request.session['email'] = email
            messages.success(request, 'OTP sent to your email address.')
            return redirect('verify_otp')  # Redirect to OTP verification page
        else:
            messages.error(request, 'No account found with that email address.')

    return render(request, 'users/forgot_password.html')


# OTP Verification View
def verify_otp(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        if otp_entered == request.session.get('otp'):
            return redirect('reset_password')  # Proceed to reset password
        else:
            messages.error(request, 'Invalid OTP')
    
    return render(request, 'users/verify_otp.html')

# Reset Password View
def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = get_user_model().objects.filter(email=request.session.get('email')).first()
        if user:
            user.set_password(password)
            user.save()
            messages.success(request, 'Your password has been reset successfully.')
            return redirect('user-login')  # Redirect to login page after password reset
        else:
            messages.error(request, 'Failed to reset password.')
    
    return render(request, 'users/reset_password.html')
