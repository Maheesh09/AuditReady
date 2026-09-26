import pytest

from app.core.config import Settings
from app.core.flags import Flags


def test_tier_thresholds_are_ordered() -> None:
    s = Settings()
    assert 0 < s.tier_medium_min_confidence < s.tier_high_min_confidence <= 1


def test_llm_temperature_is_zero_by_default() -> None:
    assert Settings().llm_temperature == 0.0


def test_flags_default_off_and_read_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FEATURE_EXPORT_XLSX", raising=False)
    assert Flags().export_xlsx is False
    monkeypatch.setenv("FEATURE_EXPORT_XLSX", "true")
    assert Flags().export_xlsx is True
