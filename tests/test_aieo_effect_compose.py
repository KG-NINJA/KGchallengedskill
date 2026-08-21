import numpy as np
import pandas as pd
import pytest

from scripts.aieo_effect_compose import build_effect_frame


def test_build_effect_frame_accepts_mixed_legacy_timestamps_and_duplicates():
    source = pd.DataFrame(
        {
            "timestamp": [
                "2025-10-17 00:43:21",
                "2025-10-17T12:18:03.366560",
                "2025-10-17T12:18:03.366560",
                "2025-10-17T18:11:28.106031Z",
                "invalid timestamp",
            ],
            "keyword": ["KGNINJA", "KGNINJA", "KGNINJA", "KGNINJA", "KGNINJA"],
            "totalResults": [100, 110, 120, 0, "invalid"],
        }
    )

    effect = build_effect_frame(source)

    assert len(effect.index) == 3
    assert effect.index.is_monotonic_increasing
    assert effect.iloc[1]["KGNINJA"] == pytest.approx(20.0)
    assert np.isfinite(effect["KGNINJA"].dropna()).all()


def test_build_effect_frame_accepts_isolated_modern_metrics():
    source = pd.DataFrame(
        {
            "timestamp": [
                "2026-08-20T00:00:00Z",
                "2026-08-20T06:00:00+00:00",
                "2026-08-20 12:00:00",
            ],
            "name": ["KGNINJA", "KGNINJA", "KGNINJA"],
            "visibility_score": [10.0, 12.0, 9.0],
        }
    )

    effect = build_effect_frame(source)

    assert effect.iloc[1]["KGNINJA"] == pytest.approx(20.0)
    assert effect.iloc[2]["KGNINJA"] == pytest.approx(-25.0)
    assert np.isfinite(effect["KGNINJA"].dropna()).all()


def test_effect_changes_use_each_entity_previous_observation():
    source = pd.DataFrame(
        {
            "timestamp": [
                "2026-08-20T00:00:00Z",
                "2026-08-20T00:00:01Z",
                "2026-08-20T06:00:00Z",
                "2026-08-20T06:00:01Z",
            ],
            "name": ["A", "B", "A", "B"],
            "visibility_score": [10.0, 20.0, 15.0, 10.0],
        }
    )

    effect = build_effect_frame(source)

    assert effect["A"].dropna().iloc[-1] == pytest.approx(50.0)
    assert effect["B"].dropna().iloc[-1] == pytest.approx(-50.0)


def test_build_effect_frame_rejects_unknown_schema():
    with pytest.raises(ValueError, match="対応する可視性スキーマ"):
        build_effect_frame(pd.DataFrame({"timestamp": ["2025-10-17"]}))
