import json
import warnings
from dataclasses import dataclass, field

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer

_MODELS_DIR = "ml/models"


def _patch_simple_imputer() -> None:
    orig = SimpleImputer.transform

    def _patched(self, X, **kwargs):
        if not hasattr(self, "_fill_dtype") and hasattr(self, "_fit_dtype"):
            self._fill_dtype = self._fit_dtype
        return orig(self, X, **kwargs)

    SimpleImputer.transform = _patched


_patch_simple_imputer()


@dataclass
class PredictionResult:
    predicted_recommended: bool
    ensemble_score: float
    model_scores: dict[str, float] = field(default_factory=dict)

    def scores_json(self) -> str:
        return json.dumps(self.model_scores)


class EnsembleBuyPredictor:
    def __init__(self) -> None:
        self._m1_vectorizer = None
        self._m1_model = None
        self._m2_pipeline = None
        self._m3_pipeline = None
        self._loaded = False
        self._load()

    def _load(self) -> None:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self._m1_vectorizer = joblib.load(f"{_MODELS_DIR}/count_vectorizer.pkl")
                self._m1_model = joblib.load(f"{_MODELS_DIR}/naive_bayes_count_vectors.pkl")
                self._m2_pipeline = joblib.load(f"{_MODELS_DIR}/pipeline_text_title.pkl")
                self._m3_pipeline = joblib.load(f"{_MODELS_DIR}/pipeline_extra_info.pkl")
            self._loaded = True
            print("[EnsembleBuyPredictor] All 3 models loaded successfully.")
        except Exception as exc:
            print(f"[EnsembleBuyPredictor] Model load failed — using rating fallback. Error: {exc}")

    def score_text(self, review_text: str) -> float:
        if not self._loaded:
            return 0.5
        try:
            X = self._m1_vectorizer.transform([review_text])
            return float(self._m1_model.predict_proba(X)[0][1])
        except Exception:
            return 0.5

    def predict(
        self,
        review_text: str,
        rating: float,
        review_title: str = "",
        price: float = 0.0,
        avg_product_rating: float = 0.0,
        product_rating_count: float = 0.0,
        brand_name: str = "",
        product_title: str = "",
    ) -> bool:
        return self.predict_full(
            review_text, rating, review_title,
            price, avg_product_rating, product_rating_count,
            brand_name, product_title,
        ).predicted_recommended

    def predict_full(
        self,
        review_text: str,
        rating: float,
        review_title: str = "",
        price: float = 0.0,
        avg_product_rating: float = 0.0,
        product_rating_count: float = 0.0,
        brand_name: str = "",
        product_title: str = "",
    ) -> PredictionResult:
        if not self._loaded:
            fallback = rating >= 4.0
            score = 1.0 if fallback else 0.0
            return PredictionResult(
                predicted_recommended=fallback,
                ensemble_score=score,
                model_scores={"rating_fallback": score},
            )

        scores: dict[str, float] = {}
        text_plus_title = f"{review_text} {review_title}".strip()

        try:
            X1 = self._m1_vectorizer.transform([review_text])
            scores["naive_bayes_text"] = float(self._m1_model.predict_proba(X1)[0][1])
        except Exception as exc:
            print(f"[M1] prediction error: {exc}")
            scores["naive_bayes_text"] = 0.5

        try:
            scores["naive_bayes_text_title"] = float(
                self._m2_pipeline.predict_proba([text_plus_title])[0][1]
            )
        except Exception as exc:
            print(f"[M2] prediction error: {exc}")
            scores["naive_bayes_text_title"] = 0.5

        try:
            df = pd.DataFrame([{
                "text_plus_title": text_plus_title,
                "price": price,
                "avg_product_rating": avg_product_rating,
                "product_rating_count": product_rating_count,
                "brand_name": brand_name,
                "product_title": product_title,
            }])
            scores["logistic_extra_info"] = float(
                self._m3_pipeline.predict_proba(df)[0][1]
            )
        except Exception as exc:
            print(f"[M3] prediction error: {exc}")
            scores["logistic_extra_info"] = 0.5

        ensemble_score = float(np.mean(list(scores.values())))
        return PredictionResult(
            predicted_recommended=ensemble_score >= 0.5,
            ensemble_score=round(ensemble_score, 4),
            model_scores={k: round(v, 4) for k, v in scores.items()},
        )


buy_predictor = EnsembleBuyPredictor()
