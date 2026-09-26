"""Environment-based feature flags (Development Plan 4.6).

Unfinished features merge to main switched off. Enable with e.g. FEATURE_EXPORT_XLSX=true.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Flags(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FEATURE_", env_file=".env", extra="ignore")

    export_xlsx: bool = False
    replay_mode: bool = False  # AI-13: serve last successful run if the LLM is down


@lru_cache
def get_flags() -> Flags:
    return Flags()
