from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Review
from Products.models import Product

def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        image = request.FILES.get("image")  # Get uploaded image

        # Save the review with the image
        Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            comment=comment,
            image=image
        )

        return redirect(reverse('Products:product_detail', kwargs={'product_slug': product.slug}))

    return render(request, 'reviews/add_review.html', {'product': product})
