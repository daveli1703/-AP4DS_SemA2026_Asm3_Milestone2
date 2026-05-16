# Demo Script — GLOW Beauty Shopping App
**4 members · 1 minute each · ~120 words per section**

---

## Member 1 — Product Search (Task 1)

**Frontend actions:**
1. Open the app on the **homepage** — the hero section ("Discover your perfect glow") is visible.
2. Point to the **search bar in the header** (`src/components/Header.jsx`).
3. Type **"maybelline"** and press Search — the hero disappears and a result count appears at the top (`"X results for 'maybelline'"` from `HomePage.jsx` line 155–156).
4. Point to the **result count** and the product cards in the grid — each card shows image, brand, price.
5. Clear the search, go back to the homepage. Open the **filter panel** — show the Brand dropdown, Category dropdown, and Min/Max price inputs (`HomePage.jsx` lines 200–259).
6. Select a brand from the dropdown and press **"Apply filters"**, show the grid update.
7. Click any product card to transition to the product detail page for Member 2.

**Backend to mention:**
- `backend/app/ml/search_engine.py` → `ProductSearchEngine.search()`: builds a **TF-IDF matrix** across product name, brand, category, and description; then runs cosine similarity against the query vector.
- `_fuzzy_expand()` (line 37): expands the query by fuzzy-matching brand words with an 80% similarity threshold — so misspellings like "maybellin" still match.
- `backend/app/routers/products.py` → `search_products()` (line 22): the FastAPI endpoint `GET /products/search` that wires the query string into the search engine.

> *"Welcome to GLOW — our beauty platform. On the homepage you can browse the full catalogue. The search bar here uses TF-IDF under the hood — I'll type 'maybelline' and the backend runs a cosine similarity score against every product's name, brand, and description. It also has fuzzy matching, so near-misspellings still return results. The count appears right here. We can also filter by brand, category, and price range — all fed as query parameters to the same FastAPI endpoint. Let me click a product to hand over to my teammate."*

---

## Member 2 — Product Detail & Reviews with ML Labels (Task 2)

**Frontend actions:**
1. Land on the **product detail page** (`src/pages/ProductDetailPage.jsx`).
2. Point to the **product info column** (right side): image on the left, brand, name, category tag, price, star rating, and description on the right.
3. Point to the **star rating and review count** — these come from the sentiment summary API call that runs in parallel with the product fetch (line 47–51 in `ProductDetailPage.jsx`).
4. Scroll down to the **Reviews section** (`src/components/ReviewList.jsx`) — show existing review cards.
5. Click **"Write a review"** button — the `ReviewForm` component opens (`src/components/ReviewForm.jsx`).
6. Fill in: **Your name** field, click a **star rating** using the star input widget, optionally type a **Review title**, then type a negative review text, e.g. *"This foundation broke me out and the coverage was terrible, I won't be buying again."*
7. Click **"Submit review"** — the form transitions to the **ML Prediction panel** (`ReviewForm.jsx` line 99):
   - Show the **verdict** ("You would not buy this again") with a red badge.
   - Point to the **confidence bar** showing the ensemble score percentage.
   - Point to the **model breakdown** — three rows: *Naive Bayes (text)*, *Naive Bayes (text + title)*, *Logistic Regression* — each with their individual probability bar.
8. Click **"Override"** to flip the label and save the correction.

**Backend to mention:**
- `backend/app/ml/predictor.py` → `EnsembleBuyPredictor.predict_full()` (line 85): runs **3 models** in sequence — Naive Bayes on count vectors (`m1`), Naive Bayes on text+title pipeline (`m2`), and a Logistic Regression pipeline that also ingests price, avg product rating, brand, and rating count (`m3`). The ensemble score is the mean of all three.
- `backend/app/routers/products.py` → `create_review()` (line 56): `POST /products/{id}/reviews` — saves the review and returns the prediction result in the response.
- `backend/app/routers/reviews.py` → `override_label()` (line 16): `PATCH /reviews/{id}/label` — persists the user-corrected recommendation label back to the database.

> *"Here's the full product page — image, brand, category, and price. Below that, the review section. I'll click 'Write a review', enter my name, give it one star, and type a negative review. When I submit, the text goes to our ensemble predictor — three models vote in parallel: a Naive Bayes on raw word counts, another Naive Bayes on text plus title, and a Logistic Regression that also factors in price and product rating. We get a verdict, a confidence score, and a breakdown per model. If the prediction is wrong, the user can hit Override — that sends a PATCH request to save the corrected label."*

---

## Member 3 — Recommendations (Task 3)

**Frontend actions:**
1. Stay on the product detail page, scroll **up** past the reviews section to the **"You might also like" section** (`src/components/RecommendationSection.jsx`).
2. Point to the **horizontally scrollable card track** — up to 8 cards are shown.
3. Point to the **"% match" badge** overlaid on each card image (e.g. "87% match") — explain it's the similarity score.
4. Point to the card info: brand name, product name, and price are all visible without clicking.
5. Click one of the recommendation cards — the app navigates to that product's detail page.
6. Show that the page **scrolls back to the top** and the "You might also like" section **reloads** with new recommendations relative to the newly viewed product.

**Backend to mention:**
- `backend/app/ml/recommender.py` → `RecommendationIndex.build()` (line 41): at startup, builds two matrices for every product — a **TF-IDF text matrix** (brand + name + category + description) and a **numeric matrix** (price, avg rating, buy rate, log review count), both normalised with MinMaxScaler.
- `RecommendationIndex.recommend()` (line 79): computes cosine similarity separately on text and numeric matrices, then blends them as **60% text + 40% numeric** — so products with similar descriptions and similar price/popularity rank together.
- `backend/app/routers/products.py` → `get_recommendations()` (line 61): `GET /products/{id}/recommendations?top_k=8` — returns the top-k scored products.

> *"Scrolling up, here's the 'You might also like' section. Each card shows a match percentage — that comes from our recommendation engine, which at startup builds a TF-IDF index across every product's text fields and a separate numeric index over price and rating data. At query time we compute cosine similarity on both, then blend them — sixty percent text, forty percent numeric. So a product that matches in description AND is similarly priced ranks higher. I'll click this card — we navigate to a new product and the recommendations update to be relative to it."*

---

## Member 4 — Additional Feature: Sentiment Analysis (Task 4)

**Frontend actions:**
1. On any product detail page, scroll to the **"Review Sentiment" panel** inside the info column (`ProductDetailPage.jsx` → `SentimentPanel` component, line 132).
2. Point to the **buy rate** at the top — e.g. "74% of reviewers recommend this product" (large percentage number).
3. Point to the **three sentiment bars** below it — Positive (green), Neutral (tan), Negative (red) — each with a percentage (e.g. 68% / 20% / 12%).
4. Point to the **"Top positive themes"** keyword tags (e.g. "love", "smooth", "moisturising") — highlight that these are extracted automatically from review text.
5. Point to the **"Top negative themes"** keyword tags (e.g. "broke", "dry", "smell") — contrast with the positive ones.
6. Optionally: navigate to a different product and show the panel updating with different keywords and sentiment breakdown.

**Backend to mention:**
- `backend/app/ml/sentiment_analyser.py` → `analyse()` (line 74): iterates through all reviews for the product. For each review it calls `score_fn` (the buy predictor's `score_text()`) to get a probability; reviews above **0.65** are positive, below **0.35** are negative, middle is neutral. The buy rate is the ratio of `recommended=True` labels.
- `_top_keywords()` (line 18): fits a **TF-IDF vectorizer** separately over positive texts and negative texts, then picks the top-N terms by aggregate TF-IDF score — that's what populates the keyword tags.
- `backend/app/routers/products.py` → `get_sentiment_summary()` (line 66): `GET /products/{id}/sentiment-summary` — the endpoint that delivers all of this to the frontend in one response.

> *"Our additional feature is the sentiment panel on every product page. Rather than a simple star average, we go deeper. At the top is the buy rate — the share of reviewers who said they'd repurchase. Below that are three sentiment bars: positive, neutral, negative — classified using our buy predictor as a scoring function, with thresholds at 0.65 and 0.35. And finally, we surface the top keywords from positive reviews and negative reviews separately, extracted with TF-IDF. So a shopper can instantly see that people love the texture but dislike the smell — without reading a single review themselves."*
