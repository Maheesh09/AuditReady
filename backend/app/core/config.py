"""Application settings.

Every tunable value (thresholds, model IDs, limits) lives here and is read from
environment variables, never hard-coded in business logic (Development Plan 4.4).
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    app_env: Literal["local", "staging", "production", "test"] = "local"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    # --- Supabase (used from Day 2) ---
    supabase_url: str = ""
    supabase_jwt_secret: str = ""
    supabase_jwt_audience: str = "authenticated"
    database_url: str = ""

    # --- Google Document AI ---
    gcp_project_id: str = ""
    docai_location: str = "us"
    docai_processor_id: str = ""

    # --- LLM (pin the exact model ID on Day 1; change only via PR + eval results) ---
    anthropic_api_key: str = ""
    llm_model_id: str = ""
    llm_temperature: float = 0.0
    llm_max_concurrency: int = 5

    # --- Retrieval ---
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    cohere_api_key: str = ""
    retrieval_top_k: int = 20
    rerank_top_n: int = 5
    rerank_min_score: float = 0.30

    # --- Confidence tiers (Section 10.1) ---
    tier_high_min_confidence: float = 0.90
    tier_medium_min_confidence: float = 0.70

    # --- Validation rules (Section 10.2) ---
    min_monthly_wage_lkr: float = 0.0  # set from current Sri Lankan law before the demo (R07)
    max_weekly_hours: float = 60.0  # R09
    expiring_soon_days: int = 60  # R04

    # --- Uploads (Section 12.2) ---
    max_upload_mb: int = 10
    max_pages: int = 10
    temp_object_max_age_minutes: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
