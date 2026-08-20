import numpy as np
import pandas as pd
import pytest

from scripts.aieo_effect_compose import build_effect_frame


def test_build_effect_frame_accepts_mixed_timestamps_and_duplicates():
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
    assert np.isfinite(effect.to_numpy()).all()


def test_build_effect_frame_rejects_missing_required_columns():
    with pytest.raises(ValueError, match="missing columns"):
        build_effect_frame(pd.DataFrame({"timestamp": ["2025-10-17"]}))
