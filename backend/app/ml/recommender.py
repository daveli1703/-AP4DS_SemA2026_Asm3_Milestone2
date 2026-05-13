import re
import warnings
from dataclasses import dataclass, field

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

from app.models.product import Product

TEXT_WEIGHT = 0.60
NUMERIC_WEIGHT = 0.40


@dataclass
class ReviewStats:
    avg_rating: float = 0.0
    buy_rate: float = 0.5
    review_count: int = 0


@dataclass
class ScoredProduct:
    product: Product
    similarity_score: float


class RecommendationIndex:
    def __init__(self) -> None:
        self._products: list[Product] = []
        self._id_to_idx: dict[int, int] = {}
        self._text_matrix = None
        self._numeric_matrix = None
        self._ready = False

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r"[^a-z0-9 ]", " ", text.lower()).strip()

    def build(self, products: list[Product], review_stats: dict[int, ReviewStats]) -> None:
        if not products:
            return

        self._products = products
        self._id_to_idx = {p.id: i for i, p in enumerate(products)}

        corpus = [
            self._clean(f"{p.brand} {p.name} {p.category} {p.description}")
            for p in products
        ]
        vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=1,
            max_features=30_000,
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._text_matrix = vectorizer.fit_transform(corpus)

        rows = []
        for p in products:
            stats = review_stats.get(p.id, ReviewStats())
            rows.append([p.price, stats.avg_rating, stats.buy_rate, float(np.log1p(stats.review_count))])

        raw = np.array(rows, dtype=np.float64)
        scaled = MinMaxScaler().fit_transform(raw)
        self._numeric_matrix = np.nan_to_num(scaled, nan=0.0, posinf=0.0, neginf=0.0) + 1e-9

        self._ready = True
        print(
            f"[RecommendationIndex] Built index: {len(products)} products, "
            f"{self._text_matrix.shape[1]} text features, "
            f"{self._numeric_matrix.shape[1]} numeric features."
        )

    def recommend(self, product_id: int, top_k: int = 5) -> list[ScoredProduct]:
        if not self._ready:
            return []

        idx = self._id_to_idx.get(product_id)
        if idx is None:
            return []

        text_sim = cosine_similarity(self._text_matrix[idx], self._text_matrix).flatten()
        num_sim = cosine_similarity(self._numeric_matrix[idx : idx + 1], self._numeric_matrix).flatten()

        combined = TEXT_WEIGHT * text_sim + NUMERIC_WEIGHT * num_sim
        combined[idx] = -1.0

        top_indices = np.argsort(combined)[::-1][:top_k]
        return [
            ScoredProduct(
                product=self._products[i],
                similarity_score=round(float(combined[i]), 4),
            )
            for i in top_indices
            if combined[i] > 0
        ]


recommendation_index = RecommendationIndex()
