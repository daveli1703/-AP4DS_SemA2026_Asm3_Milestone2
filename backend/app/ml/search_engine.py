import re
from difflib import SequenceMatcher

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ProductSearchEngine:
    FUZZY_THRESHOLD = 0.80

    def __init__(self) -> None:
        self._vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=1,
            max_features=30000,
        )
        self._product_ids: list[int] = []
        self._brand_words: list[str] = []
        self._tfidf_matrix = None
        self._ready = False

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r"[^a-z0-9 ]", " ", text.lower()).strip()

    def _collect_brand_words(self, products) -> None:
        words: set[str] = set()
        for p in products:
            for w in p.brand.lower().split():
                if len(w) > 3:
                    words.add(w)
        self._brand_words = list(words)

    def _fuzzy_expand(self, query: str) -> str:
        tokens = query.split()
        extra: set[str] = set()
        token_set = set(tokens)
        for token in tokens:
            if len(token) <= 3:
                continue
            for brand_word in self._brand_words:
                if brand_word in token_set:
                    continue
                if SequenceMatcher(None, token, brand_word).ratio() >= self.FUZZY_THRESHOLD:
                    extra.add(brand_word)
        return (query + " " + " ".join(sorted(extra))).strip() if extra else query

    def build(self, products) -> None:
        if not products:
            return
        self._product_ids = [p.id for p in products]
        self._collect_brand_words(products)
        corpus = [
            self._clean(f"{p.brand} {p.name} {p.category} {p.description}")
            for p in products
        ]
        self._tfidf_matrix = self._vectorizer.fit_transform(corpus)
        self._ready = True

    def search(self, query: str) -> list[tuple[int, float]]:
        if not self._ready:
            return []
        processed = self._clean(query)
        expanded = self._fuzzy_expand(processed)
        q_vec = self._vectorizer.transform([expanded])
        scores: np.ndarray = cosine_similarity(q_vec, self._tfidf_matrix).flatten()
        results = [
            (self._product_ids[i], float(scores[i]))
            for i in range(len(self._product_ids))
            if scores[i] > 0
        ]
        results.sort(key=lambda x: x[1], reverse=True)
        return results


product_search_engine = ProductSearchEngine()
