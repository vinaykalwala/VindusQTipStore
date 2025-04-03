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

# Add Product View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import ProductForm

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Handle image uploads
        if form.is_valid():
            form.save(user=request.user)  # Auto-assign vendor if applicable
            return redirect('product_list')  # Redirect after success
    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {'form': form})

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