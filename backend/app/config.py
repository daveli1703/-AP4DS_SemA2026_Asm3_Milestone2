from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Beauty Shop API"
    database_url: str = "sqlite:///./beauty_shop.db"
    reviews_csv_path: str = "data/reviews.csv"
    ml_model_path: str = "ml/models/predictor.pkl"

    model_config = {"env_file": ".env"}


settings = Settings()
