from pydantic import BaseModel


class SentimentBreakdownSchema(BaseModel):
    positive: int
    negative: int
    neutral: int
    positive_pct: float
    negative_pct: float
    neutral_pct: float


class SentimentSummaryResponse(BaseModel):
    product_id: int
    review_count: int
    avg_rating: float
    buy_rate: float
    sentiment_breakdown: SentimentBreakdownSchema
    top_keywords: list[str]
    top_positive_keywords: list[str]
    top_negative_keywords: list[str]
