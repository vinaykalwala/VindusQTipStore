from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from Ai.models import Recommendation
from .models import CustomUser, Address
from .forms import UserRegistrationForm, UserLoginForm, AddressForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)  # Ensure FILES is included
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after registration
            messages.success(request, "Account created successfully!")
            return redirect('dashboard')  # Redirect to dashboard instead of login page
        else:
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

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

# User Profile
@login_required
def profile(request):
    return render(request, 'users/profile.html', {'user': request.user})

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

@login_required
def dashboard_view(request):
    user = request.user
    sliders = None
    subcategories = None
    categories = None
    top_featured_products = None
    recently_viewed_products = []
    recommended_products = set()  # Use a set to avoid duplicates
    top_discount_deals = []
    final_products = []

    if user.is_superuser:
        template = 'dashboard/admin_dashboard.html'

    elif user.role == 'vendor':
        template = 'dashboard/vendor_dashboard.html'

    elif user.role == 'customer':
        template = 'dashboard/customer_dashboard.html'

        sliders = Slider.objects.order_by('-uploaded_at')[:4]
        subcategories = SubCategory.objects.all()
        categories = Category.objects.all()
        top_featured_products = Product.objects.filter(is_top_featured=True)
        top_discount_deals = Product.objects.filter(discount__gt=0).order_by('-discount')[:6] 

        # Calculate discounted price for each product
        for product in top_featured_products:
            product.final_price = product.discounted_price()

        for product in top_discount_deals:
            product.final_price = product.price - (product.price * product.discount / 100)
        
        # Fetch recently viewed products
        recently_viewed_ids = request.session.get('recently_viewed', [])
        recently_viewed_products = Product.objects.filter(id__in=recently_viewed_ids)

        # ✅ Fetch recommended products (Order by latest recommendation timestamp)
        recommended_queryset = Recommendation.objects.filter(user=user).select_related('product').order_by('-created_at')[:5]
        for rec in recommended_queryset:
            recommended_products.add(rec.product)  # Store in set to prevent duplicates

        # ✅ Fetch additional products from each subcategory
        seen_subcategories = set()
        additional_products = set()

        for product in list(recommended_products):  # Convert set to list for iteration
            if product.subcategory_id not in seen_subcategories:
                seen_subcategories.add(product.subcategory_id)
                
                # One extra product from the same subcategory (Latest First)
                one_extra_product = Product.objects.filter(subcategory_id=product.subcategory_id) \
                    .exclude(id__in=[p.id for p in recommended_products]) \
                    .order_by('-created_at') \
                    .first()
                
                # Three more products from the same subcategory (Latest First)
                three_more_products = list(
                    Product.objects.filter(subcategory_id=product.subcategory_id)
                    .exclude(id__in=[p.id for p in recommended_products.union(additional_products)])  # Avoid duplicates
                    .order_by('-created_at')[:3]
                )
                
                if one_extra_product:
                    additional_products.add(one_extra_product)  # Store in set to prevent duplicates
                
                additional_products.update(three_more_products)  # Add multiple products at once

        # ✅ Combine recommendations & subcategory-based suggestions without duplicates
        final_products = list(recommended_products.union(additional_products))  # Merge sets and convert to list

        # ✅ Sort by latest timestamp (Newest First) & Show Only 10 Products
        final_products = sorted(final_products, key=lambda p: p.created_at, reverse=True)[:10]

    elif user.role == 'delivery':
        template = 'dashboard/delivery_dashboard.html'

    else:
        template = 'dashboard/default_dashboard.html'

    return render(request, template, {
        'user': user,
        'sliders': sliders,
        'subcategories': subcategories,
        'categories': categories,
        'top_featured_products': top_featured_products,
        'top_discount_deals': top_discount_deals,
        'recently_viewed_products': recently_viewed_products,
        'recommended_products': final_products  # Final cleaned-up list with no duplicates (Latest 10)
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
