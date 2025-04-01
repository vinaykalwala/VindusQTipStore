import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from Products.models import Product
from .models import UserActivity, Recommendation

def train_recommendation_model(user):
    """Train an AI model based on user interactions and generate recommendations."""

    # Get user activity
    user_activities = UserActivity.objects.filter(user=user)
    if not user_activities.exists():
        return  # No activity, no recommendations

    # Convert data into a DataFrame
    data = []
    for activity in user_activities:
        data.append({
            "product_id": activity.product.id,
            "category": activity.product.category.name,
            "subcategory": activity.product.subcategory.name if activity.product.subcategory else "",
            "activity_type": activity.activity_type,
        })

    df = pd.DataFrame(data)

    # Feature Engineering: Convert categories, subcategories, and activity type into text
    df["text"] = df["category"] + " " + df["subcategory"] + " " + df["activity_type"]

    # Use TF-IDF to convert text into numerical features
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df["text"])

    # Compute similarity scores between products
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # Get similarity scores for each product
    similarity_scores = similarity_matrix.mean(axis=1)
    sorted_indices = similarity_scores.argsort()[::-1][:10]  # Get top 10 products
    top_products = df.iloc[sorted_indices]["product_id"].values.flatten()  # Extract product IDs

    # Remove old recommendations and save new ones
    Recommendation.objects.filter(user=user).delete()
    for idx, product_id in enumerate(top_products):
        score = similarity_scores[sorted_indices[idx]]  # Get correct similarity score
        Recommendation.objects.create(user=user, product_id=product_id, score=round(score, 2))

    return Recommendation.objects.filter(user=user)
