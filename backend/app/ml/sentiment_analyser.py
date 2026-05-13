import re
from dataclasses import dataclass, field

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from app.models.review import Review

POSITIVE_THRESHOLD = 0.65
NEGATIVE_THRESHOLD = 0.35
TOP_N = 10


def _clean(text: str) -> str:
    return re.sub(r"[^a-z\s]", " ", text.lower()).strip()


def _top_keywords(texts: list[str], n: int = TOP_N) -> list[str]:
    if not texts:
        return []
    vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 1),
        stop_words="english",
        min_df=1,
        max_features=5_000,
        token_pattern=r"(?u)\b[a-z]{3,}\b",
    )
    try:
        matrix = vectorizer.fit_transform(texts)
    except ValueError:
        return []
    scores = np.asarray(matrix.sum(axis=0)).flatten()
    top_indices = np.argsort(scores)[::-1][:n]
    vocab = vectorizer.get_feature_names_out()
    return [vocab[i] for i in top_indices]


@dataclass
class SentimentBreakdown:
    positive: int = 0
    negative: int = 0
    neutral: int = 0

    @property
    def total(self) -> int:
        return self.positive + self.negative + self.neutral

    @property
    def positive_pct(self) -> float:
        return round(self.positive / self.total * 100, 1) if self.total else 0.0

    @property
    def negative_pct(self) -> float:
        return round(self.negative / self.total * 100, 1) if self.total else 0.0

    @property
    def neutral_pct(self) -> float:
        return round(self.neutral / self.total * 100, 1) if self.total else 0.0


@dataclass
class SentimentSummary:
    product_id: int
    review_count: int
    avg_rating: float
    buy_rate: float
    sentiment_breakdown: SentimentBreakdown
    top_keywords: list[str] = field(default_factory=list)
    top_positive_keywords: list[str] = field(default_factory=list)
    top_negative_keywords: list[str] = field(default_factory=list)


def analyse(product_id: int, reviews: list[Review], score_fn) -> SentimentSummary:
    if not reviews:
        return SentimentSummary(
            product_id=product_id,
            review_count=0,
            avg_rating=0.0,
            buy_rate=0.0,
            sentiment_breakdown=SentimentBreakdown(),
        )

    avg_rating = round(float(np.mean([r.rating for r in reviews])), 2)

    recommended_values = [r.recommended for r in reviews if r.recommended is not None]
    buy_rate = round(sum(recommended_values) / len(recommended_values), 4) if recommended_values else 0.0

    breakdown = SentimentBreakdown()
    positive_texts: list[str] = []
    negative_texts: list[str] = []
    all_texts: list[str] = []

    for review in reviews:
        raw = review.review_text or ""
        cleaned = _clean(raw)
        all_texts.append(cleaned)
        prob = score_fn(raw)

        if prob >= POSITIVE_THRESHOLD:
            breakdown.positive += 1
            positive_texts.append(cleaned)
        elif prob < NEGATIVE_THRESHOLD:
            breakdown.negative += 1
            negative_texts.append(cleaned)
        else:
            breakdown.neutral += 1

    return SentimentSummary(
        product_id=product_id,
        review_count=len(reviews),
        avg_rating=avg_rating,
        buy_rate=buy_rate,
        sentiment_breakdown=breakdown,
        top_keywords=_top_keywords(all_texts, TOP_N),
        top_positive_keywords=_top_keywords(positive_texts, TOP_N),
        top_negative_keywords=_top_keywords(negative_texts, TOP_N),
    )
