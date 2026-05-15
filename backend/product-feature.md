# Feature 1: Product Search

## Overview

Users can search the cosmetics and beauty product catalogue by entering a keyword string based on brand name or product description. The system returns a count of how many products matched and a ranked list of item previews. Clicking a preview leads to the full product detail page.

## Search Algorithm

### Preprocessing

All text is lowercased and non-alphanumeric characters are replaced with spaces before any comparison.

### Fuzzy Brand Expansion

Before vectorisation the query goes through a fuzzy-expansion step designed to handle common misspellings and abbreviations of brand names (e.g. "Maybeline" → "Maybelline New York").

1. Every word longer than three characters in every known brand name is collected into a brand-word index at startup.
2. Each token in the incoming query is compared against every brand word using `difflib.SequenceMatcher`.
3. If the character-level similarity ratio is ≥ 0.80 the canonical brand word is appended to the query.

This means "Maybeline" and "Maybelline New York" produce the same result set because both resolve to the same TF-IDF representation before scoring.

### TF-IDF Relevance Ranking

A TF-IDF index (unigram + bigram, sublinear term frequency) is built over the concatenated `brand + name + category + description` text of every product when the server starts. At query time:

1. The fuzzy-expanded query is transformed by the fitted vectoriser.
2. Cosine similarity is computed between the query vector and every product vector.
3. Products with a similarity score greater than 0 are returned, sorted by score descending.

Products with no term overlap after expansion are excluded from results entirely.

### Viewing Full Details

The search response contains only lightweight product previews. Clients use the `id` field in each preview to fetch full product details, including all reviews, via `GET /products/{id}`.

---

## API Documentation

### Search Products

```
GET /products/search
```

Returns all products whose text content (brand, name, category, description) is relevant to the keyword string, ranked by relevance.

#### Query Parameters

| Parameter | Type   | Required | Description                                    |
|-----------|--------|----------|------------------------------------------------|
| `q`       | string | Yes      | Keyword string (min length 1). Supports brand names, partial names, and misspellings. |

#### Response — 200 OK

```json
{
  "count": 2,
  "results": [
    {
      "id": 14,
      "name": "Fit Me Matte + Poreless Foundation",
      "brand": "Maybelline New York",
      "category": "Foundation",
      "price": 7.97,
      "image_url": "https://example.com/images/14.jpg"
    },
    {
      "id": 27,
      "name": "Age Rewind Concealer",
      "brand": "Maybelline New York",
      "category": "Concealer",
      "price": 9.49,
      "image_url": "https://example.com/images/27.jpg"
    }
  ]
}
```

| Field            | Type            | Description                                      |
|------------------|-----------------|--------------------------------------------------|
| `count`          | integer         | Total number of matched products.                |
| `results`        | array           | Matched product previews, sorted by relevance.   |
| `results[].id`   | integer         | Unique product ID. Use with `GET /products/{id}`.|
| `results[].name` | string          | Product name.                                    |
| `results[].brand`| string          | Brand name.                                      |
| `results[].category` | string      | Product category.                                |
| `results[].price`| number          | Price in USD.                                    |
| `results[].image_url` | string \| null | Product image URL, or null if unavailable.  |

#### Error Responses

| Status | Condition                          |
|--------|------------------------------------|
| 422    | `q` is missing or empty string.    |

#### Examples

```
GET /products/search?q=Maybeline
GET /products/search?q=maybelline+new+york
GET /products/search?q=foundation+matte
GET /products/search?q=lip+gloss
```

All of the above return results sorted by relevance score. The first two return the same set of Maybelline products due to fuzzy brand expansion.

---

### Get Product Detail

```
GET /products/{id}
```

Returns full details for a single product. Used when a user clicks on a search result preview.

#### Path Parameters

| Parameter | Type    | Required | Description       |
|-----------|---------|----------|-------------------|
| `id`      | integer | Yes      | Unique product ID.|

#### Response — 200 OK

```json
{
  "id": 14,
  "name": "Fit Me Matte + Poreless Foundation",
  "brand": "Maybelline New York",
  "category": "Foundation",
  "description": "Fit Me Matte + Poreless Foundation ...",
  "price": 7.97,
  "image_url": "https://example.com/images/14.jpg"
}
```

| Field         | Type           | Description                  |
|---------------|----------------|------------------------------|
| `id`          | integer        | Unique product ID.           |
| `name`        | string         | Product name.                |
| `brand`       | string         | Brand name.                  |
| `category`    | string         | Product category.            |
| `description` | string         | Full product description.    |
| `price`       | number         | Price in USD.                |
| `image_url`   | string \| null | Product image URL, or null.  |

#### Error Responses

| Status | Condition                      |
|--------|--------------------------------|
| 404    | No product with the given ID.  |

---

### Get Product Reviews

```
GET /products/{id}/reviews
```

Returns all reviews for a product. Typically called after loading the product detail page.

#### Path Parameters

| Parameter | Type    | Required | Description       |
|-----------|---------|----------|-------------------|
| `id`      | integer | Yes      | Unique product ID.|

#### Response — 200 OK

```json
[
  {
    "id": 301,
    "product_id": 14,
    "reviewer_name": "Jane D.",
    "rating": 4.5,
    "review_text": "Great coverage and finish.",
    "predicted_recommended": true,
    "recommended": true,
    "user_overridden": false,
    "created_at": "2024-03-15T10:22:00"
  }
]
```

| Field                   | Type              | Description                                              |
|-------------------------|-------------------|----------------------------------------------------------|
| `id`                    | integer           | Review ID.                                               |
| `product_id`            | integer           | ID of the reviewed product.                              |
| `reviewer_name`         | string            | Reviewer's display name.                                 |
| `rating`                | number            | Star rating (1.0 – 5.0).                                 |
| `review_title`          | string \| null    | Optional review title supplied by the reviewer.          |
| `review_text`           | string            | Review body.                                             |
| `predicted_recommended` | boolean \| null   | Ensemble ML prediction (buyer or not).                   |
| `recommended`           | boolean \| null   | Final label (ML prediction unless overridden by a human).|
| `user_overridden`       | boolean           | True if the ML label was manually corrected.             |
| `ensemble_score`        | number \| null    | Mean predicted-buyer probability across all three models (0.0 – 1.0). |
| `model_scores`          | object \| null    | Per-model predicted-buyer probabilities. Keys: `naive_bayes_text`, `naive_bayes_text_title`, `logistic_extra_info`. |
| `created_at`            | string (ISO 8601) | Timestamp of the review.                                 |

---

# Feature 2: Review Submission with ML Buy Prediction

## Overview

When a customer writes a review for a product, the system automatically predicts whether the reviewer is likely to buy the product again. This binary label (`true` = would buy, `false` = would not buy) is generated by an ensemble of three machine-learning classifiers, each trained on a different type of data. The predicted label is returned to the customer immediately after submission. If the customer disagrees with the prediction, they can override it before the review is finalised. Once confirmed, the review is persisted in the database and accessible via its own URL.

---

## Prediction Algorithm

### Ensemble of Three Models

Three pre-trained scikit-learn models are loaded at startup from `ml/models/`. Each model is trained on the same dataset (`cosmetics_beauty_products_reviews.csv`, 61 284 reviews) but operates on a different representation of the data, giving the ensemble complementary signal.

| Model key | Algorithm | Input data | Cross-val accuracy |
|---|---|---|---|
| `naive_bayes_text` | MultinomialNB | Review text → fixed 8 054-word count vector | 77.8% |
| `naive_bayes_text_title` | MultinomialNB (pipeline) | Review text + title concatenated → count vector (max 10 000 features) | 77.6% |
| `logistic_extra_info` | Logistic Regression (pipeline) | Text + title + price, brand name, product name, average product rating, rating count | **82.6%** |

### Fusion

Each model outputs a probability score between 0 and 1 representing the likelihood the reviewer is a buyer. The three scores are averaged:

```
ensemble_score = mean(naive_bayes_text, naive_bayes_text_title, logistic_extra_info)
predicted_recommended = ensemble_score >= 0.5
```

All three scores and the ensemble average are stored and returned in the review response so the customer can see how each model voted.

### Product Context for Model 3

The third model (logistic regression) requires structured product attributes in addition to text. These are sourced automatically at prediction time — the client does not need to supply them:

- **price** — from the product record
- **brand name** — from the product record
- **product name** — from the product record
- **average product rating** — computed from all existing reviews for that product
- **rating count** — total number of existing reviews for that product

### User Override

After the prediction is returned, the customer can choose a different label. Submitting a `recommended` field at review-creation time immediately applies the override (the ML prediction is still stored in `predicted_recommended` for reference). Alternatively, the customer can call the label override endpoint after creation. In both cases `user_overridden` is set to `true`.

---

## API Documentation

### Create Review (triggers ML prediction)

```
POST /products/{product_id}/reviews
```

Submits a new review for a product. The server runs the ensemble classifier on the review text, title, and product attributes, then returns the review with the predicted label and individual model scores. The reviewer can supply their own `recommended` value to immediately override the ML prediction.

#### Path Parameters

| Parameter    | Type    | Required | Description        |
|--------------|---------|----------|--------------------|
| `product_id` | integer | Yes      | ID of the product being reviewed. |

#### Request Body

```json
{
  "reviewer_name": "Jane Doe",
  "rating": 4.5,
  "review_title": "Absolutely love this!",
  "review_text": "This foundation blends beautifully and lasts all day. Definitely buying again.",
  "recommended": null
}
```

| Field           | Type            | Required | Description                                                                 |
|-----------------|-----------------|----------|-----------------------------------------------------------------------------|
| `reviewer_name` | string          | Yes      | Display name of the reviewer.                                               |
| `rating`        | number          | Yes      | Star rating from 1.0 to 5.0.                                                |
| `review_title`  | string          | No       | Optional short title for the review. Used by model 2 and model 3.           |
| `review_text`   | string          | Yes      | Full review body. Used by all three models.                                  |
| `recommended`   | boolean \| null | No       | If provided, overrides the ML prediction immediately. Omit to accept the ML label. |

#### Response — 201 Created

```json
{
  "id": 42,
  "product_id": 1,
  "reviewer_name": "Jane Doe",
  "rating": 4.5,
  "review_title": "Absolutely love this!",
  "review_text": "This foundation blends beautifully and lasts all day. Definitely buying again.",
  "predicted_recommended": true,
  "recommended": true,
  "user_overridden": false,
  "ensemble_score": 0.5977,
  "model_scores": {
    "naive_bayes_text": 0.7786,
    "naive_bayes_text_title": 0.9606,
    "logistic_extra_info": 0.0538
  },
  "created_at": "2026-05-13T06:42:12.203090"
}
```

| Field                   | Type              | Description                                                              |
|-------------------------|-------------------|--------------------------------------------------------------------------|
| `id`                    | integer           | Unique review ID. Use with `GET /reviews/{id}`.                          |
| `product_id`            | integer           | ID of the reviewed product.                                              |
| `reviewer_name`         | string            | Reviewer's display name.                                                 |
| `rating`                | number            | Star rating (1.0 – 5.0).                                                 |
| `review_title`          | string \| null    | Review title as submitted.                                               |
| `review_text`           | string            | Review body as submitted.                                                |
| `predicted_recommended` | boolean \| null   | Raw ensemble prediction before any user override.                        |
| `recommended`           | boolean \| null   | Final label shown on the site. Equals `predicted_recommended` unless the user overrode it. |
| `user_overridden`       | boolean           | `true` if the customer changed the ML label.                             |
| `ensemble_score`        | number            | Mean probability across all three models (0.0 – 1.0).                   |
| `model_scores`          | object            | Per-model probabilities. Keys: `naive_bayes_text`, `naive_bayes_text_title`, `logistic_extra_info`. |
| `created_at`            | string (ISO 8601) | Timestamp of submission.                                                 |

#### Error Responses

| Status | Condition                                        |
|--------|--------------------------------------------------|
| 404    | No product with the given `product_id`.          |
| 422    | Missing required fields or `rating` out of range.|

#### Examples

```
POST /products/14/reviews
POST /products/27/reviews
```

---

### Get Review by URL

```
GET /reviews/{review_id}
```

Returns a single review by its ID. Every review submitted to the system is accessible at this URL, making each review permanently linkable.

#### Path Parameters

| Parameter   | Type    | Required | Description      |
|-------------|---------|----------|------------------|
| `review_id` | integer | Yes      | Unique review ID.|

#### Response — 200 OK

```json
{
  "id": 42,
  "product_id": 1,
  "reviewer_name": "Jane Doe",
  "rating": 4.5,
  "review_title": "Absolutely love this!",
  "review_text": "This foundation blends beautifully and lasts all day. Definitely buying again.",
  "predicted_recommended": true,
  "recommended": true,
  "user_overridden": false,
  "ensemble_score": 0.5977,
  "model_scores": {
    "naive_bayes_text": 0.7786,
    "naive_bayes_text_title": 0.9606,
    "logistic_extra_info": 0.0538
  },
  "created_at": "2026-05-13T06:42:12.203090"
}
```

Same field definitions as the `POST` response above.

#### Error Responses

| Status | Condition                        |
|--------|----------------------------------|
| 404    | No review with the given ID.     |

---

### Override ML-Predicted Label

```
PATCH /reviews/{review_id}/label
```

Lets the reviewer replace the ML-predicted label with their own choice. Can be called at any point after the review is created. Sets `user_overridden` to `true` and updates `recommended`; the original `predicted_recommended` value is preserved unchanged.

#### Path Parameters

| Parameter   | Type    | Required | Description      |
|-------------|---------|----------|------------------|
| `review_id` | integer | Yes      | Unique review ID.|

#### Request Body

```json
{
  "recommended": false
}
```

| Field         | Type    | Required | Description                              |
|---------------|---------|----------|------------------------------------------|
| `recommended` | boolean | Yes      | The customer's chosen label (`true` / `false`). |

#### Response — 200 OK

Returns the full updated review object (same shape as `GET /reviews/{id}`), with `recommended` set to the new value and `user_overridden` set to `true`.

```json
{
  "id": 42,
  "product_id": 1,
  "reviewer_name": "Jane Doe",
  "rating": 4.5,
  "review_title": "Absolutely love this!",
  "review_text": "This foundation blends beautifully and lasts all day. Definitely buying again.",
  "predicted_recommended": true,
  "recommended": false,
  "user_overridden": true,
  "ensemble_score": 0.5977,
  "model_scores": {
    "naive_bayes_text": 0.7786,
    "naive_bayes_text_title": 0.9606,
    "logistic_extra_info": 0.0538
  },
  "created_at": "2026-05-13T06:42:12.203090"
}
```

#### Error Responses

| Status | Condition                    |
|--------|------------------------------|
| 404    | No review with the given ID. |
| 422    | `recommended` field missing. |

---

# Feature 3: Similar Product Recommendations

## Overview

When a customer views a product, the system automatically surfaces a ranked list of similar products they might also be interested in. Similarity is computed from two complementary signals — product content text and a numeric attribute profile derived from both item metadata and historical customer review data. The index is built once at server startup and all queries are served from the cached matrices, making recommendations fast regardless of catalogue size.

---

## Recommendation Algorithm

### Two Similarity Signals

#### Signal 1 — Content TF-IDF (weight: 60%)

Each product is represented as a TF-IDF vector over its concatenated `brand + name + category + description` text (unigram + bigram, sublinear term frequency, up to 30 000 features). Cosine similarity between two such vectors captures lexical overlap in product metadata — products sharing brand names, category terms, or descriptive words score high.

#### Signal 2 — Numeric Attribute Profile (weight: 40%)

Each product is also represented as a four-dimensional numeric vector:

| Feature | Source | Normalisation |
|---|---|---|
| `price` | `Product.price` | MinMaxScaler over all products |
| `avg_rating` | Mean of `Review.rating` across all reviews for the product | Divided by 5.0 (known max) |
| `buy_rate` | Proportion of reviews where `recommended = true` | Already in [0, 1]; defaults to 0.5 if no reviews |
| `log_review_count` | `log(1 + review_count)` | MinMaxScaler over all products |

`avg_rating` and `buy_rate` are derived from historical customer review data in the database, giving the recommender a "how customers received this product" dimension on top of raw item attributes. Products with similar price points and similar customer reception cluster together even when their descriptions differ.

All four features are scaled to [0, 1] before computing cosine similarity, so no single feature dominates due to scale differences.

#### Fusion

The two cosine similarity scores are linearly combined:

```
similarity = 0.60 × text_sim + 0.40 × numeric_sim
```

The product with the highest combined score is returned first. The query product itself is excluded (its self-similarity is suppressed to −1).

### Index Lifecycle

The index is built once at application startup after the database has been queried for all products and their review aggregates. Queries hit the cached TF-IDF and numeric matrices directly — there is no per-request re-fitting. If the application is restarted, the index is rebuilt from the current database state, incorporating any reviews submitted since the last restart.

---

## API Documentation

### Get Similar Products

```
GET /products/{product_id}/recommendations
```

Returns the top-k most similar products to the given product, ranked by combined similarity score descending.

#### Path Parameters

| Parameter    | Type    | Required | Description                   |
|--------------|---------|----------|-------------------------------|
| `product_id` | integer | Yes      | ID of the product to match against. |

#### Query Parameters

| Parameter | Type    | Required | Default | Description                         |
|-----------|---------|----------|---------|-------------------------------------|
| `top_k`   | integer | No       | 5       | Maximum number of recommendations to return. |

#### Response — 200 OK

```json
{
  "product_id": 181,
  "count": 5,
  "results": [
    {
      "id": 180,
      "name": "Maybelline New York Color Sensational Satin Lipstick",
      "brand": "Maybelline New York",
      "category": "General",
      "price": 499.0,
      "image_url": "https://www.nykaa.com/...",
      "similarity_score": 0.6453
    },
    {
      "id": 183,
      "name": "Maybelline New York Color Sensational Matte Metallic Lipstick",
      "brand": "Maybelline New York",
      "category": "General",
      "price": 475.0,
      "image_url": "https://www.nykaa.com/...",
      "similarity_score": 0.6314
    }
  ]
}
```

| Field                    | Type           | Description                                                      |
|--------------------------|----------------|------------------------------------------------------------------|
| `product_id`             | integer        | The ID of the queried product.                                   |
| `count`                  | integer        | Number of recommendations returned (≤ `top_k`).                 |
| `results`                | array          | Recommended products sorted by `similarity_score` descending.   |
| `results[].id`           | integer        | Product ID.                                                      |
| `results[].name`         | string         | Product name.                                                    |
| `results[].brand`        | string         | Brand name.                                                      |
| `results[].category`     | string         | Product category.                                                |
| `results[].price`        | number         | Price in local currency.                                         |
| `results[].image_url`    | string \| null | Product image URL, or null if unavailable.                       |
| `results[].similarity_score` | number    | Combined similarity score (0.0 – 1.0). Higher means more similar. |

#### Error Responses

| Status | Condition                           |
|--------|-------------------------------------|
| 404    | No product with the given ID.       |

#### Examples

```
GET /products/181/recommendations
GET /products/181/recommendations?top_k=10
GET /products/1/recommendations?top_k=3
```

---

# Feature 4: Per-Product Review Sentiment Summary

## Overview

When a customer views a product, they can request a sentiment overview of all existing reviews rather than reading through them individually. The system analyses every review for that product using an NLP classifier, groups them into positive, negative, and neutral buckets, and extracts the most representative keywords from each group. The result gives a quick "at a glance" picture of what customers appreciate and what they criticise, backed by actual vocabulary from the reviews.

---

## Sentiment Analysis Algorithm

### Step 1 — Per-Review Classification (M1 Model)

Each review text is scored using **M1** — the `naive_bayes_count_vectors` model (CountVectorizer with an 8 054-word fixed vocabulary + MultinomialNB), which was originally trained to predict buyer intent. The same model's probability output serves as a sentiment signal: a high buyer probability correlates with a positive review, and a low probability correlates with a negative one. This avoids loading any additional model and reuses the already-trained artefact from `ml/models/`.

The probability score for each review is thresholded as follows:

| Score range | Label |
|---|---|
| ≥ 0.65 | **Positive** |
| < 0.35 | **Negative** |
| 0.35 – 0.65 | **Neutral** |

### Step 2 — Keyword Extraction (TF-IDF)

Three separate TF-IDF vectorisers (unigram, sklearn english stopwords, minimum 3-letter tokens) are fitted on-the-fly over three review corpora:

1. **All reviews** → overall top keywords for the product
2. **Positive reviews only** → terms most characteristic of happy customers
3. **Negative reviews only** → terms most characteristic of unhappy customers

Terms are ranked by their summed TF-IDF weight across all documents in the respective corpus. The top 10 terms per group are returned.

### Step 3 — Aggregate Statistics

The response also includes aggregate statistics computed directly from the database:

- `avg_rating` — arithmetic mean of all star ratings for the product
- `buy_rate` — proportion of reviews where `recommended = true` (the final confirmed label, whether ML-predicted or user-overridden)
- Sentiment counts and percentages from Step 1

---

## API Documentation

### Get Sentiment Summary

```
GET /products/{product_id}/sentiment-summary
```

Returns a sentiment overview of all reviews for a product, including classification breakdown, aggregate rating stats, and top keywords extracted from positive and negative review groups.

#### Path Parameters

| Parameter    | Type    | Required | Description                      |
|--------------|---------|----------|----------------------------------|
| `product_id` | integer | Yes      | ID of the product to summarise.  |

#### Response — 200 OK

```json
{
  "product_id": 181,
  "review_count": 440,
  "avg_rating": 3.95,
  "buy_rate": 0.6568,
  "sentiment_breakdown": {
    "positive": 334,
    "negative": 33,
    "neutral": 73,
    "positive_pct": 75.9,
    "negative_pct": 7.5,
    "neutral_pct": 16.6
  },
  "top_keywords": [
    "lipstick", "shade", "good", "love", "glossy",
    "nice", "color", "lips", "like", "product"
  ],
  "top_positive_keywords": [
    "lipstick", "shade", "good", "love", "nice",
    "color", "like", "glossy", "lips", "product"
  ],
  "top_negative_keywords": [
    "shine", "lipstick", "glossy", "shade", "like",
    "lips", "red", "compulsion", "audacious", "matte"
  ]
}
```

| Field | Type | Description |
|---|---|---|
| `product_id` | integer | ID of the product. |
| `review_count` | integer | Total number of reviews analysed. |
| `avg_rating` | number | Mean star rating across all reviews (1.0 – 5.0). |
| `buy_rate` | number | Proportion of reviews with `recommended = true` (0.0 – 1.0). |
| `sentiment_breakdown.positive` | integer | Number of reviews classified as positive. |
| `sentiment_breakdown.negative` | integer | Number of reviews classified as negative. |
| `sentiment_breakdown.neutral` | integer | Number of reviews classified as neutral. |
| `sentiment_breakdown.positive_pct` | number | Percentage of positive reviews. |
| `sentiment_breakdown.negative_pct` | number | Percentage of negative reviews. |
| `sentiment_breakdown.neutral_pct` | number | Percentage of neutral reviews. |
| `top_keywords` | array of strings | Top 10 keywords across all reviews. |
| `top_positive_keywords` | array of strings | Top 10 keywords from positive reviews only. |
| `top_negative_keywords` | array of strings | Top 10 keywords from negative reviews only (empty if no negative reviews exist). |

#### Behaviour when there are no reviews

If the product exists but has no reviews, all numeric fields are 0, all keyword lists are empty, and the sentiment breakdown is all zeros.

#### Error Responses

| Status | Condition |
|--------|-----------|
| 404 | No product with the given ID. |

#### Examples

```
GET /products/181/sentiment-summary
GET /products/1/sentiment-summary
```
