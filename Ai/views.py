from django.shortcuts import render
from .models import Recommendation

# Show AI-Based Recommendations
def recommendations(request):
    recommended_products = Recommendation.objects.filter(user=request.user).order_by('-score')[:5]
    return render(request, 'ai/recommendations.html', {'recommended_products': recommended_products})

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Recommendation
from Products.models import Product
from Products.serializers import ProductSerializer

@api_view(["GET"])
def get_recommendations(request, user_id):
    """Fetch recommended products for a user, including products from the same subcategories."""

    # Get recommended products from the Recommendation model
    recommendations = Recommendation.objects.filter(user_id=user_id).order_by("-score")
    recommended_products = [rec.product for rec in recommendations]

    # Get subcategories of recommended products
    subcategory_ids = set(product.subcategory.id for product in recommended_products if product.subcategory)

    # Fetch additional products from the same subcategories (excluding already recommended ones)
    additional_products = Product.objects.filter(subcategory_id__in=subcategory_ids).exclude(id__in=[p.id for p in recommended_products])

    # Combine recommended and additional products
    all_products = list(recommended_products) + list(additional_products)

    # Serialize and return the response
    return Response(ProductSerializer(all_products, many=True).data)
