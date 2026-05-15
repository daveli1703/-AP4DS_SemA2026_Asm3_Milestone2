# Models Reference

This document describes all trained models saved in the `models/` directory. They are produced by running `task2_3.ipynb` to completion. All models predict the binary target `is_a_buyer` (1 = verified buyer, 0 = not) on the cosmetics/beauty product reviews dataset (`cosmetics_beauty_products_reviews.csv`).

---

## Dataset & Labels

- **Source:** `cosmetics_beauty_products_reviews.csv` — 61,284 reviews
- **Target:** `is_a_buyer` (bool → int: 1 = buyer, 0 = non-buyer)
- **Class distribution:** ~78.7% positive (buyers), highly imbalanced
- **Majority-class baseline accuracy:** ~78.69%
- **Evaluation:** 5-fold stratified cross-validation (`StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`)

---

## Preprocessing Artifacts

### `models/count_vectorizer.pkl`
- **Type:** `sklearn.feature_extraction.text.CountVectorizer`
- **Input:** processed review text (string)
- **Vocabulary:** fixed 8,054-word vocabulary from `vocab.txt` (produced by Task 1 preprocessing)
- **Output:** sparse count matrix of shape `(n_reviews, 8054)`
- **Notes:** Vocabulary is pre-set, so the vectorizer does not need to be re-fitted. Transform only.

### `models/tfidf_vectorizer.pkl`
- **Type:** `sklearn.feature_extraction.text.TfidfVectorizer`
- **Input:** processed review text (string)
- **Vocabulary:** same fixed 8,054-word vocabulary from `vocab.txt`
- **Output:** sparse TF-IDF matrix of shape `(n_reviews, 8054)`
- **Fitted on:** full 61,284 processed reviews
- **Notes:** Used to compute per-token TF-IDF weights for the weighted GloVe embedding step. Not used directly for classification.

---

## Classification Models

### `models/dummy_classifier.pkl`
- **Type:** `sklearn.dummy.DummyClassifier(strategy="most_frequent")`
- **Input:** ignored (any array of shape `(n, 1)`)
- **Cross-val accuracy:** ~78.69% (equals majority baseline by design)
- **Purpose:** majority-class baseline — always predicts class 1 (buyer). Used as a lower-bound reference to judge whether other models are learning real signal.

---

### `models/naive_bayes_count_vectors.pkl`
- **Type:** `sklearn.naive_bayes.MultinomialNB`
- **Input:** sparse count vector of shape `(n, 8054)` — produced by `count_vectorizer`
- **Cross-val accuracy:** ~77.82%
- **Notes:** Performs *below* the majority baseline. Count vectors with MultinomialNB appear to pick up on vocabulary patterns that slightly hurt accuracy on this imbalanced dataset. Suitable only for sparse non-negative integer features.

---

### `models/logistic_regression_unweighted_embeddings.pkl`
- **Type:** `sklearn.linear_model.LogisticRegression(max_iter=1000)`
- **Input:** dense vector of shape `(n, 50)` — unweighted average of GloVe-50 token embeddings
- **Embedding model:** `glove-wiki-gigaword-50` (loaded via `gensim.downloader`)
- **Cross-val accuracy:** ~78.67%
- **Notes:** Reviews with no tokens in the GloVe vocabulary receive a zero vector. Marginally below the majority baseline — the averaged embedding loses most sentiment signal.

---

### `models/logistic_regression_weighted_embeddings.pkl`
- **Type:** `sklearn.linear_model.LogisticRegression(max_iter=1000)`
- **Input:** dense vector of shape `(n, 50)` — TF-IDF weighted average of GloVe-50 token embeddings
- **Embedding model:** `glove-wiki-gigaword-50` (loaded via `gensim.downloader`)
- **Cross-val accuracy:** ~78.68%
- **Notes:** Best review-text-only model. TF-IDF weighting down-weights common terms and amplifies rare descriptive words. Still very close to the majority baseline — review text alone is a weak predictor of buyer status.

---

### `models/pipeline_text_title.pkl`
- **Type:** `sklearn.pipeline.Pipeline`
  - Step 1: `CountVectorizer(max_features=10000)` — fitted on `processed_review + " " + review_title`
  - Step 2: `MultinomialNB`
- **Input:** single string column — concatenation of processed review body and lowercased review title
- **Cross-val accuracy:** ~77.62%
- **Notes:** Adding the review title hurt accuracy slightly compared to review text alone. The pipeline is self-contained: the internal vectorizer is included and does not need to be applied separately before inference.

---

### `models/pipeline_extra_info.pkl`
- **Type:** `sklearn.pipeline.Pipeline`
  - Preprocessor: `ColumnTransformer` with three branches:
    - `text` — `CountVectorizer(max_features=10000)` on `text_plus_title` column
    - `num` — `SimpleImputer(median)` + `StandardScaler(with_mean=False)` on `["price", "avg_product_rating", "product_rating_count"]`
    - `cat` — `SimpleImputer(most_frequent)` + `OneHotEncoder(handle_unknown="ignore")` on `["brand_name", "product_title"]`
  - Classifier: `LogisticRegression(max_iter=1000)`
- **Input:** a pandas DataFrame with columns: `text_plus_title` (str), `price` (float), `avg_product_rating` (float), `product_rating_count` (float), `brand_name` (str), `product_title` (str)
- **Cross-val accuracy:** ~82.58%
- **Notes:** Best-performing model overall — the only one that meaningfully beats the majority baseline. Structured product attributes (brand, price, ratings) carry more predictive signal than review text alone.

---

## Performance Summary

| Model file | Algorithm | Feature input | CV Accuracy |
|---|---|---|---|
| `dummy_classifier.pkl` | DummyClassifier | — | 78.69% (baseline) |
| `naive_bayes_count_vectors.pkl` | MultinomialNB | Count vectors | 77.82% |
| `logistic_regression_unweighted_embeddings.pkl` | Logistic Regression | Unweighted GloVe-50 | 78.67% |
| `logistic_regression_weighted_embeddings.pkl` | Logistic Regression | TF-IDF weighted GloVe-50 | 78.68% |
| `pipeline_text_title.pkl` | Pipeline (CV + NB) | Text + title | 77.62% |
| `pipeline_extra_info.pkl` | Pipeline (CT + LR) | Text + title + product info | **82.58%** |

---

## Loading a Model

```python
import joblib
import numpy as np

model = joblib.load("models/pipeline_extra_info.pkl")
# model.predict(df_input)  # df_input must have the required columns (see above)
```

For the embedding-based models, the GloVe vectors must be recomputed before inference:

```python
import gensim.downloader as api
embedding_model = api.load("glove-wiki-gigaword-50")
```

---

## File Dependencies

| File | Produced by |
|---|---|
| `processed.csv` | `task1.ipynb` |
| `vocab.txt` | `task1.ipynb` |
| `count_vectors.txt` | `task2_3.ipynb` (Task 2) |
| `unweighted_vectors.txt` | `task2_3.ipynb` (Task 2) |
| `weighted_vectors.txt` | `task2_3.ipynb` (Task 2) |
| `models/*.pkl` | `task2_3.ipynb` (final cells) |
