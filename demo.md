# Demo Script — GLOW Beauty Shopping App
**4 members · 1 minute each · ~120 words per section**

---

## Member 1 — Product Search (Task 1)

> *Start on the homepage with no search query.*

"Welcome to GLOW, our beauty and cosmetics shopping platform. The homepage loads a full catalogue of products — you can scroll through and browse everything we have.

Now, the first key feature is search. I'll type in 'maybelline' — notice it doesn't need to be perfectly spelled or capitalised. The system returns a result count straight away — right here it tells us exactly how many products matched. Each result shows a product preview with the image, brand, and price.

Let me try something broader — I'll search for 'moisturiser'. Again, instant results with the count shown. Clicking any card takes us into the full product detail page, which my next teammate will walk through."

---

## Member 2 — Product Detail & Reviews with ML Labels (Task 2)

> *Start on a product detail page.*

"Here's the full product page. You can see the product image, brand, price, category, and a description. Below that we have a sentiment summary built from all existing reviews — it shows what percentage of reviewers recommend the product, and breaks down positive, neutral, and negative sentiment with the top keywords people mention.

Now let me write a new review. I'll click 'Write a review', fill in my name, give it a star rating, and type something like — 'This foundation broke me out and the coverage was terrible, I won't be buying again.'

After submitting, our ML models analyse the text and predict whether I'd repurchase. You can see the verdict, the confidence score, and the individual breakdown across all three models. If I disagree, I can hit Override — and the corrected label is saved."

---

## Member 3 — Recommendations (Task 3)

> *Scroll to the recommendations section on a product detail page.*

"Scrolling down on any product page, you'll find the 'You might also like' section. This is our recommendation engine. It analyses product attributes and review data to find items most similar to the one you're currently viewing.

Each recommendation card shows a similarity score — so this one is an eighty-six percent match, this one seventy-two percent. These aren't random — they're ranked by how closely they relate to the current product.

Let me click one of these recommendations. We go straight to that new product's page, scrolled right back to the top. And the recommendations update too — they're now relative to this new product. So the more you explore, the more relevant the suggestions become."

---

## Member 4 — Additional Feature: Sentiment Analysis (Task 4)

> *Start on a product detail page, scrolled to the sentiment panel.*

"Our additional feature is the sentiment analysis panel, which you'll find on every product page. Rather than just showing a star rating average, we go much deeper.

At the top, we show the buy rate — the percentage of reviewers who actually recommend this product. Below that is a breakdown bar chart splitting all reviews into positive, neutral, and negative sentiment. And finally, we surface the most common keywords from positive reviews and negative reviews separately — so you can instantly see what people love and what they don't, without having to read every single review.

This is all generated automatically from the review text using our NLP models on the backend. It gives shoppers a much faster, more informed way to decide whether a product is right for them."
