# %% [markdown]
# # Assignment 3 – Milestone I: Natural Language Processing
# ## Task 2 & Task 3
# 
# | Student Name | Student ID |
# |---|---|
# | Ly Chi Hung | s4046014 |
# | Le Nguyen Kiet | s4043909 |
# | Tran Vu Nhat Tin | s3870729 |
# | Phan Hoang Vu | s4192517 |
# 
# Environment: Python 3 and Jupyter Notebook
# 
# ### Introduction
# This notebook presents the implementation of Task 2 and Task 3 for Assignment 3 Milestone I.  
# Task 2 focuses on generating feature representations for cosmetics and beauty product reviews, including count vectors, unweighted embedding vectors, and TF-IDF weighted embedding vectors.  
# Task 3 focuses on building and evaluating classification models to predict purchasing behaviour (`is_a_buyer`) using different feature settings and comparing their performance through 5-fold cross validation.
# 

# %% [markdown]
# ## Importing libraries
# 
# This section imports the libraries required for feature generation, machine learning experiments, and output formatting.

# %%
import re
import numpy as np
import pandas as pd
from IPython.display import display

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

import gensim.downloader as api

print("Libraries imported successfully.")

# %% [markdown]
# ## Task 2. Generating Feature Representations for Cosmetics/Beauty Reviews
# 
# In this task, three document representations are generated from the review text:
# 1. count vector representation based on the vocabulary from Task 1
# 2. unweighted document embeddings using a pretrained word embedding model
# 3. TF-IDF weighted document embeddings using the same embedding model
# 
# These outputs are later used in Task 3 for classification experiments.

# %% [markdown]
# ### Task 2 Output Contract
# 
# The three files generated in this task must all keep the original review order:
# 
# - `count_vectors.txt`: sparse review vectors using the integer indices from `vocab.txt`
# - `unweighted_vectors.txt`: averaged pretrained embedding vectors for each review
# - `weighted_vectors.txt`: TF-IDF weighted averaged embedding vectors for each review
# 
# Rows with no remaining tokens are still written to the output files. This keeps the file row number aligned with the original dataset row number.

# %% [markdown]
# ### 2.1 Loading data and Task 1 outputs
# 
# The dataset, processed reviews, and Task 1 vocabulary are loaded.  
# The processed review text is used as the main input for Task 2 feature generation.

# %%
# Load original dataset
df = pd.read_csv("cosmetics_beauty_products_reviews.csv")

# Load processed reviews from Task 1. keep_default_na=False preserves intentionally blank reviews.
processed_df = pd.read_csv("processed.csv", keep_default_na=False)

# Attach processed review column while preserving original row order and indices.
df["processed_review"] = processed_df["processed_review"].fillna("").astype(str)

# Load vocabulary from vocab.txt
vocab_list = []
vocab_dict = {}

with open("vocab.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            word, idx = line.rsplit(":", 1)
            vocab_list.append(word)
            vocab_dict[word] = int(idx)

print("Original dataset shape:", df.shape)
print("Processed review shape:", processed_df.shape)
print("Missing original review_text values:", df["review_text"].isna().sum())
print("Blank processed reviews:", (df["processed_review"] == "").sum())
print("Vocabulary size:", len(vocab_list))

display(df[["processed_review", "review_title", "is_a_buyer"]].head())

# %% [markdown]
# ### 2.2 Count vector representation
# 
# The count vector representation is generated using the Task 1 vocabulary only.  
# This ensures consistency between preprocessing and sparse encoding.

# %%
count_vectorizer = CountVectorizer(
    vocabulary=vocab_dict,
    token_pattern=r"(?u)\b\w[\w'-]*\b"
)

X_count = count_vectorizer.transform(df["processed_review"].fillna(""))

print("Count vector shape:", X_count.shape)
print("Number of non-zero values:", X_count.nnz)

# %% [markdown]
# ### 2.3 Loading pretrained embedding model
# 
# A pretrained 50-dimensional GloVe model is loaded using `gensim.downloader`.  
# This model is used as the common embedding source for both the unweighted and TF-IDF weighted document vectors.

# %% [markdown]
# #### Embedding model choice
# 
# This notebook uses `glove-wiki-gigaword-50`, a compact 50-dimensional pretrained GloVe model available through `gensim.downloader`.  
# The model size is manageable for the assignment while still providing semantic word vectors for the review tokens.

# %%
# Load pretrained embedding model
embedding_model = api.load("glove-wiki-gigaword-50")
embedding_dim = embedding_model.vector_size

print("Embedding dimension:", embedding_dim)

# %% [markdown]
# ### 2.4 Unweighted and TF-IDF weighted document embeddings
# 
# For each processed review:
# - the unweighted document embedding is computed as the average of token embeddings
# - the weighted document embedding is computed as the TF-IDF weighted average of token embeddings

# %%
# Tokenize processed reviews by whitespace
tokenized_reviews = df["processed_review"].fillna("").apply(lambda x: x.split()).tolist()

# Build TF-IDF from processed reviews using Task 1 vocabulary
tfidf_vectorizer = TfidfVectorizer(
    vocabulary=vocab_dict,
    token_pattern=r"(?u)\b\w[\w'-]*\b"
)

X_tfidf = tfidf_vectorizer.fit_transform(df["processed_review"].fillna(""))
tfidf_vocab_index = {word: idx for idx, word in enumerate(tfidf_vectorizer.get_feature_names_out())}

def get_unweighted_embedding(tokens, model, dim):
    vectors = [model[word] for word in tokens if word in model]
    if len(vectors) > 0:
        return np.mean(vectors, axis=0)
    return np.zeros(dim)

def get_weighted_embedding(tokens, model, dim, tfidf_row, tfidf_vocab_index):
    weighted_sum = np.zeros(dim)
    total_weight = 0.0

    for word in tokens:
        if word in model and word in tfidf_vocab_index:
            weight = tfidf_row[0, tfidf_vocab_index[word]]
            if weight > 0:
                weighted_sum += model[word] * weight
                total_weight += weight

    if total_weight > 0:
        return weighted_sum / total_weight
    return np.zeros(dim)

# Unweighted vectors
unweighted_vectors = np.array([
    get_unweighted_embedding(tokens, embedding_model, embedding_dim)
    for tokens in tokenized_reviews
])

# Weighted vectors
weighted_vectors = np.array([
    get_weighted_embedding(tokens, embedding_model, embedding_dim, X_tfidf[i], tfidf_vocab_index)
    for i, tokens in enumerate(tokenized_reviews)
])

print("Unweighted vectors shape:", unweighted_vectors.shape)
print("Weighted vectors shape:", weighted_vectors.shape)

# %% [markdown]
# ### 2.5 Saving Task 2 outputs
# 
# The required output files are saved in text-based formats.  
# Each line starts with `#` followed by the review row index, then a comma, then the vector content. Empty sparse rows are still written as `#index,` so the row is not lost.

# %%
def save_sparse_count_vectors(filename, matrix):
    with open(filename, "w", encoding="utf-8") as f:
        for i in range(matrix.shape[0]):
            row = matrix.getrow(i)
            indices = row.indices
            values = row.data
            pairs = [f"{idx}:{val}" for idx, val in zip(indices, values)]
            line = f"#{i}," + ",".join(pairs)
            f.write(line + "\n")

def save_dense_vectors(filename, matrix):
    with open(filename, "w", encoding="utf-8") as f:
        for i, vec in enumerate(matrix):
            values = ",".join(str(x) for x in vec)
            f.write(f"#{i},{values}\n")

save_sparse_count_vectors("count_vectors.txt", X_count)
save_dense_vectors("unweighted_vectors.txt", unweighted_vectors)
save_dense_vectors("weighted_vectors.txt", weighted_vectors)

print("Task 2 output files saved successfully.")

# %% [markdown]
# ## Task 3. Cosmetics/Beauty Products Review Classification
# This task compares different review representations and examines whether adding more information improves predictive accuracy for `is_a_buyer`.

# %% [markdown]
# ### Task 3 Evaluation Design
# 
# All comparisons use the same target variable, `is_a_buyer`, and the same 5-fold stratified cross-validation split.  
# Because the labels are imbalanced, the majority-class baseline is reported beside the model results so the accuracy values have a meaningful reference point.

# %% [markdown]
# ### 3.1 Preparing labels and validation setting
# The classification target is `is_a_buyer`, and evaluation is performed using 5-fold stratified cross validation.

# %%
# Convert label to integer if needed
if df["is_a_buyer"].dtype == bool:
    y = df["is_a_buyer"].astype(int)
else:
    y = df["is_a_buyer"].map({"True": 1, "False": 0, True: 1, False: 0}).astype(int)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Majority-class baseline for interpreting accuracy on this imbalanced dataset.
dummy_model = DummyClassifier(strategy="most_frequent")
dummy_scores = cross_val_score(
    dummy_model,
    np.zeros((len(y), 1)),
    y,
    cv=cv,
    scoring="accuracy"
)

print("Label distribution:")
print(y.value_counts())
print("\nMajority-class baseline accuracy:", dummy_scores.mean())

# %% [markdown]
# ### 3.2 Q1: Which review representation performs best?
# 
# Three review-text representations are compared using 5-fold cross validation:
# 
# - count vectors
# - unweighted embeddings
# - TF-IDF weighted embeddings
# 
# The majority-class baseline is included in the results table to show whether the models are learning beyond the label imbalance.

# %%
# Models
count_model = MultinomialNB()  # suitable for sparse count vectors
unweighted_model = LogisticRegression(max_iter=1000)  # suitable for dense embedding vectors
weighted_model = LogisticRegression(max_iter=1000)

# Cross-validation
count_scores = cross_val_score(count_model, X_count, y, cv=cv, scoring="accuracy")
unweighted_scores = cross_val_score(unweighted_model, unweighted_vectors, y, cv=cv, scoring="accuracy")
weighted_scores = cross_val_score(weighted_model, weighted_vectors, y, cv=cv, scoring="accuracy")

q1_results = pd.DataFrame({
    "Representation": [
        "Majority Baseline",
        "Count Vectors",
        "Unweighted Embeddings",
        "Weighted Embeddings"
    ],
    "Mean Accuracy": [
        dummy_scores.mean(),
        count_scores.mean(),
        unweighted_scores.mean(),
        weighted_scores.mean()
    ],
    "Std Accuracy": [
        dummy_scores.std(),
        count_scores.std(),
        unweighted_scores.std(),
        weighted_scores.std()
    ]
})

display(q1_results.sort_values("Mean Accuracy", ascending=False))

# %% [markdown]
# ### Q1 Result Interpretation
# 
# The best review-only representation is the non-baseline row with the highest mean accuracy.  
# Because most reviews are labelled as buyer reviews, the majority-class baseline is a strong reference point. A representation that only matches this baseline is not providing much practical signal, even if the raw accuracy looks high.
# 
# The count-vector model is useful as a sparse lexical baseline, while the weighted and unweighted embedding models test whether pretrained semantic information improves the prediction.

# %% [markdown]
# ### 3.3 Q2: Does more information improve accuracy?
# 
# Three input settings are compared:
# 
# - review text only
# - review text and review title
# - review text, review title, and additional product information
# 
# The text vectorizer for the title experiment is fitted inside the cross-validation pipeline to avoid fitting it on the full dataset before evaluation.

# %%
# Make a copy for Task 3 Q2
df_q2 = df.copy()

# Ensure text columns are strings, not NaN
df_q2["processed_review"] = df_q2["processed_review"].fillna("").astype(str)
df_q2["review_title_clean"] = df_q2["review_title"].fillna("").astype(str).str.lower()
df_q2["text_plus_title"] = df_q2["processed_review"] + " " + df_q2["review_title_clean"]

# Text only baseline: use the best review-only representation from Q1
text_only_scores = weighted_scores

# Text + title. The vectorizer is inside the pipeline so it is fitted within each CV fold.
text_title_model = make_pipeline(
    CountVectorizer(max_features=10000),
    MultinomialNB()
)
text_title_scores = cross_val_score(
    text_title_model,
    df_q2["text_plus_title"],
    y,
    cv=cv,
    scoring="accuracy"
)

# Text + title + extra product information
numeric_features = ["price", "avg_product_rating", "product_rating_count"]
categorical_features = ["brand_name", "product_title"]

numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler(with_mean=False))
])

categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer(
    transformers=[
        ("text", CountVectorizer(max_features=10000), "text_plus_title"),
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features)
    ]
)

extra_info_model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(max_iter=1000))
])

extra_info_scores = cross_val_score(extra_info_model, df_q2, y, cv=cv, scoring="accuracy")

q2_results = pd.DataFrame({
    "Feature Setting": [
        "Review Text Only",
        "Review Text + Title",
        "Review Text + Title + Extra Product Information"
    ],
    "Mean Accuracy": [
        text_only_scores.mean(),
        text_title_scores.mean(),
        extra_info_scores.mean()
    ],
    "Std Accuracy": [
        text_only_scores.std(),
        text_title_scores.std(),
        extra_info_scores.std()
    ]
})

display(q2_results.sort_values("Mean Accuracy", ascending=False))

# %% [markdown]
# ### Q2 Result Interpretation
# 
# This table should be read as an incremental feature comparison.  
# If the title setting improves over review text only, then short review summaries add useful signal. If the full product-information setting improves further, then structured product attributes such as brand, price, product title, and product-level ratings help explain buyer behaviour beyond the review wording alone.
# 
# The comparison is still based on accuracy, so the results should also be interpreted against the majority-class baseline from the previous section.

# %% [markdown]
# ## Summary
# 
# In Task 2, three feature representations were generated from the processed review text: count vectors, unweighted document embeddings, and TF-IDF weighted document embeddings. These representations were saved in the required output formats while preserving one output row per original review.
# 
# In Task 3, 5-fold cross validation was used to compare the predictive performance of the review-based representations for classifying `is_a_buyer`. A majority-class baseline was included because the target labels are imbalanced.
# 
# Additional experiments were then conducted to investigate whether more information improves accuracy. The notebook compares review text only, review text plus title, and review text plus title plus structured product attributes.


# ==========================================
# CODE FOR MILESTONE 2: EXPORTING THE MODEL
# ==========================================
import joblib
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

print("Training final model for Web App deployment...")

# 1. Create a single Pipeline that does BOTH vectorizing and predicting at the same time
final_web_model = make_pipeline(
    TfidfVectorizer(token_pattern=r"(?u)\b\w[\w'-]*\b", max_features=10000),
    LogisticRegression(max_iter=1000)
)

# 2. Train the pipeline on ALL the review text and labels
final_web_model.fit(df["processed_review"].fillna(""), y)

# 3. Save the pipeline as ONE single .pkl file
joblib.dump(final_web_model, 'my_model.pkl')

print("✅ FINAL MODEL SAVED! You can now move 'my_model.pkl' to your backend folder.")