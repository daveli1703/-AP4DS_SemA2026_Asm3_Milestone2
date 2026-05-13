# %% [markdown]
# # Assignment 3: Milestone I Natural Language Processing
# ## Task 1. Basic Text Pre-processing
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
# This notebook presents the implementation of Task 1 for Assignment 3 Milestone I.  
# The aim of this task is to preprocess the `review_text` field from the cosmetics and beauty product reviews dataset so that the text can be prepared for later feature extraction and classification tasks.
# 
# The preprocessing pipeline follows the assignment requirements strictly. It includes:
# - extracting the review text
# - tokenising text using the required regular expression
# - converting all words to lowercase
# - removing words with length less than 2
# - removing stopwords using the provided stopword list
# - removing words that appear only once in the document collection
# - removing the top 20 most frequent words based on document frequency
# 
# After preprocessing, the cleaned reviews are saved as `processed.csv`, and the final vocabulary is saved as `vocab.txt` in the required format.
# 

# %% [markdown]
# ### Assignment Requirements Checklist
# 
# This notebook implements the Task 1 from the milestone brief:
# 
# - use only `review_text` for preprocessing
# - tokenize with `r"[a-zA-Z]+(?:[-'][a-zA-Z]+)?"`
# - lowercase tokens, remove one-character tokens, and remove provided stopwords
# - remove collection-level singleton terms by term frequency
# - remove the top 20 terms by document frequency
# - save cleaned review text to `processed.csv`
# - save an alphabetically sorted zero-based vocabulary to `vocab.txt`
# 
# Rows are kept in the same order as the original dataset. Reviews with missing `review_text` are treated as empty text so that downstream feature files still contain one row per original review.

# %% [markdown]
# ## Importing libraries

# %%
# Core libraries
import re
from collections import Counter

# Data handling
import pandas as pd
from IPython.display import display
import numpy as np

# %% [markdown]
# ### 1.1 Examining and loading data
# 
# In this section, the dataset and stopword list are loaded and inspected.  
# The main field used in Task 1 is `review_text`, as required by the assignment.
# 
# Missing `review_text` values are not removed from the dataset. They are handled as empty reviews during preprocessing so the generated files remain aligned with the original review indices.

# %%
# Load dataset
df = pd.read_csv("cosmetics_beauty_products_reviews.csv")

# Load stopwords
with open("stopwords_en.txt", "r", encoding="utf-8") as f:
    stopwords = set(line.strip().lower() for line in f if line.strip())

# Display basic dataset information
print("Dataset shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values in relevant columns:")
print(df[["review_text", "review_title", "is_a_buyer"]].isna().sum())

print("\nSample rows:")
display(df.head())

# %% [markdown]
# ### 1.2 Pre-processing data
# 
# This section performs the required text preprocessing steps on the `review_text` field only.  
# The process follows the assignment instructions strictly:
# 
# 1. Tokenise using the required regular expression  
# 2. Convert all tokens to lowercase  
# 3. Remove words with length less than 2  
# 4. Remove stopwords using the provided file  
# 5. Remove words that appear only once in the whole collection  
# 6. Remove the top 20 most frequent words based on document frequency  
# 
# The final cleaned reviews will then be used to generate `processed.csv` and `vocab.txt`.

# %% [markdown]
# #### Preprocessing implementation
# 
# The code below applies each preprocessing step in sequence and prepares both the cleaned review collection and the final vocabulary.

# %%
# Make a copy and preserve the original row order for downstream alignment
task1_df = df.copy()
missing_review_count = task1_df["review_text"].isna().sum()

# Missing review text is represented as an empty document rather than dropping the review
task1_df["review_text_for_processing"] = task1_df["review_text"].fillna("")

# Required tokenisation regex from the assignment
token_pattern = re.compile(r"[a-zA-Z]+(?:[-'][a-zA-Z]+)?")

# Step 1-4: tokenise, lowercase, remove tokens with length < 2, remove stopwords
def initial_preprocess(text):
    tokens = token_pattern.findall(str(text))
    tokens = [token.lower() for token in tokens]
    tokens = [token for token in tokens if len(token) >= 2]
    tokens = [token for token in tokens if token not in stopwords]
    return tokens

task1_df["tokens_initial"] = task1_df["review_text_for_processing"].apply(initial_preprocess)

# Step 5: remove words that appear only once in the whole collection based on term frequency
term_freq = Counter()
for tokens in task1_df["tokens_initial"]:
    term_freq.update(tokens)

tokens_after_tf = []
for tokens in task1_df["tokens_initial"]:
    filtered = [token for token in tokens if term_freq[token] > 1]
    tokens_after_tf.append(filtered)

task1_df["tokens_tf"] = tokens_after_tf

# Step 6: remove top 20 most frequent words based on document frequency
doc_freq = Counter()
for tokens in task1_df["tokens_tf"]:
    unique_tokens = set(tokens)
    doc_freq.update(unique_tokens)

top_20_df_words = set([word for word, freq in doc_freq.most_common(20)])

task1_df["tokens_final"] = task1_df["tokens_tf"].apply(
    lambda tokens: [token for token in tokens if token not in top_20_df_words]
)

# Create processed text column
task1_df["processed_review"] = task1_df["tokens_final"].apply(lambda tokens: " ".join(tokens))

# Build vocabulary from final cleaned reviews
vocab_words = sorted(set(token for tokens in task1_df["tokens_final"] for token in tokens))
vocab_dict = {word: idx for idx, word in enumerate(vocab_words)}

# Quick checks
print("Number of original reviews preserved:", len(task1_df))
print("Missing review_text values treated as empty reviews:", missing_review_count)
print("Vocabulary size:", len(vocab_words))
print("Top 20 words removed by document frequency:")
print(sorted(top_20_df_words))

print("\nSample processed reviews:")
display(task1_df[["review_text", "processed_review"]].head())

# %% [markdown]
# ## Saving required outputs
# 
# The cleaned review data is saved as `processed.csv`, and the final vocabulary is saved as `vocab.txt` in the required format:
# 
# `word_string:word_integer_index`
# 
# The vocabulary is sorted alphabetically and indexing starts from 0, as required.

# %%
# Save processed.csv
processed_output = task1_df[["processed_review"]].copy()
processed_output.to_csv("processed.csv", index=False)

# Save vocab.txt
with open("vocab.txt", "w", encoding="utf-8") as f:
    for word in vocab_words:
        f.write(f"{word}:{vocab_dict[word]}\n")

print("Saved processed.csv and vocab.txt successfully.")

# Preview outputs
print("\nprocessed.csv preview:")
display(processed_output.head())

print("\nvocab.txt preview:")
for word in vocab_words[:20]:
    print(f"{word}:{vocab_dict[word]}")

# %% [markdown]
# ## Summary
# 
# In Task 1, the `review_text` field was preprocessed using the required tokenisation rule and cleaning steps.  
# The workflow included lowercasing, stopword removal, removal of rare terms based on collection term frequency, and removal of the top 20 most frequent words based on document frequency.  
# 
# The final cleaned reviews were saved in `processed.csv`, and the resulting unigram vocabulary was saved in `vocab.txt` using alphabetical ordering and zero-based indexing.

# %% [markdown]
# ### Output validation checks
# 
# These checks confirm that the saved files can be loaded again, the vocabulary uses the required ordering and indexing, and the processed review file still has one row per original review.

# %%
# Final validation checks

# Check processed.csv exists and loads. keep_default_na=False preserves intentionally blank reviews.
processed_check = pd.read_csv("processed.csv", keep_default_na=False)
print("processed.csv shape:", processed_check.shape)
print("Rows match original dataset:", len(processed_check) == len(df))
print("Blank processed reviews:", (processed_check["processed_review"].astype(str) == "").sum())
display(processed_check.head())

# Check vocab.txt format
with open("vocab.txt", "r", encoding="utf-8") as f:
    vocab_lines = [line.strip() for line in f if line.strip()]

print("\nNumber of vocab entries:", len(vocab_lines))
print("First 10 vocab entries:")
for line in vocab_lines[:10]:
    print(line)

# Verify alphabetical order and zero-based indexing
parsed_vocab = [line.rsplit(":", 1) for line in vocab_lines]
words_only = [item[0] for item in parsed_vocab]
indices_only = [int(item[1]) for item in parsed_vocab]

print("\nVocabulary sorted alphabetically:", words_only == sorted(words_only))
print("Index starts at 0:", indices_only[0] == 0 if indices_only else False)
print("Sequential indices:", indices_only == list(range(len(indices_only))))

# %%
# Reload original data for an independent audit of the removal rules
df_original = pd.read_csv("cosmetics_beauty_products_reviews.csv")
missing_review_count = df_original["review_text"].isna().sum()
df_original["review_text_for_processing"] = df_original["review_text"].fillna("")

with open("stopwords_en.txt", "r", encoding="utf-8") as f:
    stopwords = set(line.strip().lower() for line in f if line.strip())

token_pattern = re.compile(r"[a-zA-Z]+(?:[-'][a-zA-Z]+)?")

def initial_preprocess(text):
    tokens = token_pattern.findall(str(text))
    tokens = [t.lower() for t in tokens]
    tokens = [t for t in tokens if len(t) >= 2]
    tokens = [t for t in tokens if t not in stopwords]
    return tokens

df_original["tokens_initial"] = df_original["review_text_for_processing"].apply(initial_preprocess)

# Term frequency
tf = Counter()
for tokens in df_original["tokens_initial"]:
    tf.update(tokens)

singleton_words = {word for word, count in tf.items() if count == 1}

df_original["tokens_tf"] = df_original["tokens_initial"].apply(
    lambda tokens: [t for t in tokens if t not in singleton_words]
)

# Document frequency
df_counter = Counter()
for tokens in df_original["tokens_tf"]:
    df_counter.update(set(tokens))

top20_df = {word for word, count in df_counter.most_common(20)}

print("Original rows audited:", len(df_original))
print("Missing review_text values treated as empty reviews:", missing_review_count)
print("Number of singleton words removed:", len(singleton_words))
print("Top 20 DF words removed:", sorted(top20_df))

# Final vocab from file
with open("vocab.txt", "r", encoding="utf-8") as f:
    final_vocab = {line.strip().rsplit(":", 1)[0] for line in f if line.strip()}

print("Any stopwords still in vocab?:", any(word in stopwords for word in final_vocab))
print("Any singleton words still in vocab?:", any(word in singleton_words for word in final_vocab))
print("Any top20 DF words still in vocab?:", any(word in top20_df for word in final_vocab))


