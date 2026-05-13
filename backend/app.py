from flask import Flask, jsonify, request
from flask_cors import CORS
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

app = Flask(__name__)
CORS(app) 
model = joblib.load('my_model.pkl')
df = pd.read_csv("cosmetics_beauty_products_reviews.csv")
df_raw = df.copy()
df_processed = pd.read_csv("processed.csv")
df_raw['clean_text'] = df_processed['processed_review']
print(df.columns)
# In app.py - Data Preparation Section
mapping = {
    'product_title': 'name',
    'brand_name': 'brand',
    'review_text': 'description',
    'price': 'price',
    'avg_product_rating': 'rating',
    'product_rating_count': 'ratingCount',
    'product_url': 'url'
}
# Clean duplicates based on title and assign unique IDs
unique_products = df_raw.drop_duplicates(subset=['product_title']).copy()
unique_products['id'] = range(1, len(unique_products) + 1)
products_db = unique_products.rename(columns=mapping)[
    ['id', 'name', 'brand', 'price', 'description', 'rating', 'ratingCount', 'url']
].to_dict('records')

BRAND_IMAGE_MAP = {
    "Colorbar": "colorbar.jpg",
    "Herbal Essences": "herbal.png",
    "Kay Beauty": "kay.webp",
    "L'Oreal Paris": "loreal.webp",
    "Lakme": "lakme.png",
    "Maybelline New York": "maybelline.png",
    "NYX Professional Makeup": "nyx.webp",
    "Nivea": "nivea.jpg",
    "Olay": "olay.png",
    "Nykaa Cosmetics": "nykaa.jpg", 
    "Nykaa Naturals": "nykaa.jpg"
}   

# Apply the mapping when you prepare your products_db
for product in products_db:
    # Use the exact brand name from the CSV/Dropdown
    brand_name = product.get('brand') 
    
    if brand_name in BRAND_IMAGE_MAP:
        # Construct the URL for the frontend
        product['imageUrl'] = f"/static/brands/{BRAND_IMAGE_MAP[brand_name]}"
    else:
        # Fallback to None so the frontend shows the letter placeholder
        product['imageUrl'] = None



# Task 1: Product Search (Handles basic keyword matching)
@app.route('/api/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '').lower()
    # Supports searching by name or description
    results = [p for p in products_db if query in p['name'].lower() or query in p['description'].lower()]
    return jsonify(results)

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(products_db)

# Task 1: Get single product details 
@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((p for p in products_db if p['id'] == product_id), None)
    return jsonify(product) if product else (jsonify({"error": "Not found"}), 404)

# Task 2: Machine Learning Prediction 
@app.route('/api/predict-review', methods=['POST'])
def predict_review():
    data = request.json
    review_text = data.get('review', '').strip()  # Get the review text and ensure it's a string
    product_id = data.get('productId') 
    
    # Convert product_id to int to match the DB format
    product = next((p for p in products_db if p['id'] == int(product_id)), None)
    
    # Safety Check: If product is not found, stop here instead of crashing
    if not product:
        print(f"Error: Product with ID {product_id} not found.")
        return jsonify({"label": "Not Buy", "error": "Product not found"}), 404

    try:
        # Use .get() with a default value (like 0) to prevent KeyError
        input_df = pd.DataFrame([{
            'text_plus_title': review_text,
            'price': float(product.get('price', 0)), 
            'avg_product_rating': float(product.get('rating', 0)),
            'product_rating_count': int(product.get('ratingCount', 0)),
            'brand_name': product.get('brand', 'Unknown'),
            'product_title': product.get('name', 'Unknown'),
            'product_url': product.get('url', ''),
            'imageUrl': product.get('imageUrl', ''),
        }])
        
        

        negative_words = ['bad', 'waste', 'disappointed', 'terrible', 'broke', 'hate', 'not good', 'awful', 'poor', 'worst', 'not',
                          'disappointing', 'horrible', 'regret', 'return', 'refund', 'useless', 'flawed', 'defective']
        is_negative = any(word in review_text.lower() for word in negative_words)

        prediction_proba = model.predict_proba(input_df)[0][1] # Probability of "Buy"

        if is_negative:
            prediction_proba -= 0.3  # Reduce confidence by 30% if negative words are present 

        label = "Buy" if prediction_proba > 0.5 else "Not Buy"
    
        return jsonify({"label": label})

    

    except Exception as e:
        print(f"Prediction Error: {e}")
        return jsonify({"label": "Not Buy", "error": str(e)}), 500

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(unique_products['clean_text'].fillna(''))

# Task 3: Recommendation Engine (Cosine Similarity)
@app.route('/api/products/<int:product_id>/recommendations')
def get_recommendations(product_id):
    # Find the index of the current product
    idx = next(i for i, p in enumerate(products_db) if p['id'] == product_id)
    
    # Calculate Similarity
    cosine_sim = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    
    # Get top 3 (excluding itself)
    top_indices = cosine_sim.argsort()[-4:-1][::-1]
    
    recommendations = []
    for i in top_indices:
        target = products_db[i]
        recommendations.append({
            "id": target['id'],
            "name": target['name'],
            "brand": target['brand'],
            "imageUrl": target['imageUrl'],
            "similarityScore": round(cosine_sim[i] * 100, 2) # Now this will be higher!
        })
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True, port=5000)