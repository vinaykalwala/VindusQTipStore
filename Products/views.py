from django.shortcuts import render, get_object_or_404

from Ai.signals import track_product_view
from .models import Product, Category, SubCategory
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from .forms import ProductForm

from django.shortcuts import render
from .models import Product, Category, SubCategory

def product_list(request):
    products = Product.objects.all()
    query = request.GET.get("search", "")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    sort_by = request.GET.get("sort_by")
    category_id = request.GET.get("category")
    subcategory_id = request.GET.get("subcategory")

    # ✅ Search by product name
    if query:
        products = products.filter(name__icontains=query)

    # ✅ Convert discount price on the fly for filtering
    if min_price:
        products = [p for p in products if p.discounted_price() >= float(min_price)]
    if max_price:
        products = [p for p in products if p.discounted_price() <= float(max_price)]

    # ✅ Sort by price (Highest to Lowest or vice versa)
    if sort_by == "price_high":
        products = sorted(products, key=lambda p: p.discounted_price(), reverse=True)
    elif sort_by == "price_low":
        products = sorted(products, key=lambda p: p.discounted_price())

    # ✅ Filter by category
    if category_id:
        products = [p for p in products if p.category_id == int(category_id)]
        subcategories = SubCategory.objects.filter(category_id=category_id)  
    else:
        subcategories = SubCategory.objects.all()

    # ✅ Filter by subcategory
    if subcategory_id:
        products = [p for p in products if p.subcategory_id == int(subcategory_id)]

    categories = Category.objects.all()

    return render(
        request,
        "products/product_list.html",
        {
            "products": products,
            "categories": categories,
            "subcategories": subcategories,
            "query": query,
            "min_price": min_price,
            "max_price": max_price,
            "sort_by": sort_by,
            "selected_category": category_id,
            "selected_subcategory": subcategory_id,
        },
    )


from django.shortcuts import render, get_object_or_404
from django.db.models import Avg
from Products.models import Product
from Reviews.models import Review

def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    variants = product.variants.all()

    if request.user.is_authenticated:
        track_product_view(request.user, product)

    # Calculate the exact average rating
    reviews = Review.objects.filter(product=product)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    total_reviews = reviews.count()

    # Compute discounted price
    discounted_price = product.discounted_price()

    # Include variant details for dynamic price calculation
    variant_data = [
        {
            "id": variant.id,
            "color": variant.color,
            "size": variant.size,
            "image": variant.image.url if variant.image else product.image.url,
            "additional_price": variant.additional_price,
            "final_price": discounted_price + variant.additional_price,  # Adjusting variant price with discount
            "original_price": product.price + variant.additional_price,
        }
        for variant in variants
    ]
    recently_viewed = request.session.get('recently_viewed', [])
    
    # Remove product if already in list to avoid duplicates
    if product.id in recently_viewed:
        recently_viewed.remove(product.id)

    # Add the product to the beginning of the list
    recently_viewed.insert(0, product.id)

    # Keep only the last 5 recently viewed products
    recently_viewed = recently_viewed[:5]

    # Save to session
    request.session['recently_viewed'] = recently_viewed

    # Fetch recently viewed product objects
    recently_viewed_products = Product.objects.filter(id__in=recently_viewed).exclude(id=product.id)

    # ✅ **Find Similar Products (Same Subcategory)**
    similar_products = Product.objects.filter(subcategory=product.subcategory).exclude(id=product.id)[:5]


    return render(request, 'products/product_detail.html', {
        'product': product,
        'variants': variants,
        'variant_data': variant_data,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
        'reviews': reviews,
        'discounted_price': discounted_price,
        'recently_viewed_products': recently_viewed_products,
        'similar_products': similar_products 
    })
from .forms import ProductForm, CategoryForm, SubCategoryForm, ProductVariantForm, SliderForm  # import SliderForm
from django.contrib.auth.decorators import login_required

@login_required
def add_product(request):
    # Forms initialized in both POST and GET to avoid missing references
    product_form = ProductForm()
    category_form = CategoryForm()
    subcategory_form = SubCategoryForm()
    variant_form = ProductVariantForm()
    slider_form = SliderForm() if request.user.is_superuser else None

    if request.method == "POST":
        if "category_submit" in request.POST:
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
                return redirect('Products:add_product')

        elif "subcategory_submit" in request.POST:
            subcategory_form = SubCategoryForm(request.POST)
            if subcategory_form.is_valid():
                subcategory_form.save()
                return redirect('Products:add_product')

        elif "variant_submit" in request.POST:
            variant_form = ProductVariantForm(request.POST, request.FILES)
            if variant_form.is_valid():
                variant_form.save()
                return redirect('Products:add_product')

        elif "product_submit" in request.POST:
            product_form = ProductForm(request.POST, request.FILES)
            if product_form.is_valid():
                product_form.save(user=request.user)
                return redirect('dashboard')

        elif "slider_submit" in request.POST and request.user.is_superuser:
            slider_form = SliderForm(request.POST, request.FILES)
            if slider_form.is_valid():
                slider_form.save()
                return redirect('Products:add_product')

    return render(request, "products/add_product.html", {
        "product_form": product_form,
        "category_form": category_form,
        "subcategory_form": subcategory_form,
        "variant_form": variant_form,
        "slider_form": slider_form  # Pass it to template
    })



from django.shortcuts import render, get_object_or_404
from .models import Product, ProductVariant
from Reviews.models import Review
from django.db.models import Avg

# View for Product Details (Including Reviews)
def view_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = product.variants.all()  # Get all variants related to this product
    reviews = Review.objects.filter(product=product).order_by('-created_at')  # Get reviews for this product
    avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0  # Calculate average rating
    
    return render(request, 'Products/view_product.html', {
        'product': product,
        'variants': variants,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),  # Round to 1 decimal place
    })

# View for Variant Details
def view_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    return render(request, 'Products/view_variant.html', {'variant': variant})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import ProductForm

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('vendor_dashboard')  # Redirect back to vendor dashboard after save
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/edit_product.html', {'form': form, 'product': product})

from .models import ProductVariant
from .forms import ProductVariantForm

@login_required
def edit_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id, product__vendor=request.user)

    if request.method == "POST":
        form = ProductVariantForm(request.POST, request.FILES, instance=variant)
        if form.is_valid():
            form.save()
            return redirect('vendor_dashboard')  # Redirect to vendor dashboard after save
    else:
        form = ProductVariantForm(instance=variant)

    return render(request, 'products/edit_variant.html', {'form': form, 'variant': variant})


# Delete Product View
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        product.delete()
        return redirect("product_list")
    return render(request, "products/delete_product.html", {"product": product})

# Category-wise Products
def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, 'products/category_products.html', {'category': category, 'products': products})

# Subcategory-wise Products
def subcategory_products(request, slug):
    subcategory = get_object_or_404(SubCategory, slug=slug)
    products = Product.objects.filter(subcategory=subcategory)
    return render(request, 'products/subcategory_products.html', {'subcategory': subcategory, 'products': products})



def featured_products(request):
    top_featured = Product.objects.filter(is_top_featured=True)
    
    # Modify each product to include the correct price
    for product in top_featured:
        product.final_price = product.discounted_price()  # Add final price to each product

    return render(request, 'featured_products.html', {'top_featured': top_featured})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Product

@login_required
def manage_products(request):
    if request.user.is_superuser:
        products = Product.objects.prefetch_related('variants').all()  # Prefetch variants
    else:
        products = Product.objects.filter(vendor=request.user).prefetch_related('variants')

    return render(request, 'products/manage_products.html', {'products': products})


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user != product.vendor and not request.user.is_superuser:
        messages.error(request, "You do not have permission to delete this product.")
        return redirect('Products:manage_products')

    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect('Products:manage_products')


@login_required
def delete_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)

    if request.user != variant.product.vendor and not request.user.is_superuser:
        messages.error(request, "You do not have permission to delete this variant.")
        return redirect('Products:manage_products')

    variant.delete()
    messages.success(request, "Variant deleted successfully.")
    return redirect('Products:manage_products')


from django.shortcuts import render
from .models import Product, Category, SubCategory
from .forms import SearchForm
from django.db.models import Q

def search_view(request):
    form = SearchForm()
    results = {
        'products': [],
        'categories': [],
        'subcategories': []
    }

    query = request.GET.get('query')
    if query:
        form = SearchForm(request.GET)
        if form.is_valid():
            q = form.cleaned_data['query']

            # 1. Search directly in products
            product_matches = Product.objects.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )

            # 2. Search matching categories & fetch their products
            matched_categories = Category.objects.filter(name__icontains=q)
            category_products = Product.objects.filter(category__in=matched_categories)

            # 3. Search matching subcategories & fetch their products
            matched_subcategories = SubCategory.objects.filter(name__icontains=q)
            subcategory_products = Product.objects.filter(subcategory__in=matched_subcategories)

            # Combine all products & eliminate duplicates
            all_matched_products = (
                product_matches | category_products | subcategory_products
            ).distinct()

            results['products'] = all_matched_products
            results['categories'] = matched_categories
            results['subcategories'] = matched_subcategories

    return render(request, 'products/search_results.html', {
        'form': form,
        'results': results,
        'query': query
    })


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .models import Product
from .forms import UpdateStockForm

@login_required
def low_stock_products(request):
    if request.user.is_superuser:
        products = Product.objects.filter(stock__lt=5)
    else:
        products = Product.objects.filter(stock__lt=5, vendor=request.user)

    if request.method == 'POST':
        if 'update_stock' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)

            # Superuser can only update if no vendor is assigned
            if request.user.is_superuser and product.vendor:
                messages.error(request, f"Superuser cannot update stock for vendor-managed product '{product.name}'.")
            else:
                form = UpdateStockForm(request.POST, instance=product)
                if form.is_valid():
                    form.save()
                    messages.success(request, f"Stock for '{product.name}' updated successfully.")
                    return redirect('Products:low_stock_products')

        elif 'send_alert' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)

            if product.vendor and product.vendor.email:
                vendor_email = product.vendor.email
                vendor_name = product.vendor.get_full_name() or product.vendor.username

                subject = f"⚠️ Low Stock Alert: {product.name}"
                message = f"""
Dear {vendor_name},

Your product "{product.name}" is currently low on stock with only {product.stock} units left.

Please update the stock from your dashboard at your earliest convenience.

Thank you,
Inventory Management Team
QTipStore
"""

                send_mail(subject, message.strip(), settings.DEFAULT_FROM_EMAIL, [vendor_email])
                messages.success(request, f"Alert email sent to {vendor_name} for '{product.name}'.")
            else:
                messages.error(request, "No vendor or email associated with the product.")
            return redirect('Products:low_stock_products')

    return render(request, 'products/low_stock_products.html', {
        'products': products,
        'stock_form': UpdateStockForm()
    })
