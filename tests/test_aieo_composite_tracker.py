import numpy as np
import pandas as pd
import pytest

from scripts.aieo_composite_tracker import build_resonance_frame


def test_single_effect_series_produces_finite_resonance():
    source = pd.DataFrame(
        {
            "timestamp": [
                "2026-08-20T00:00:00Z",
                "2026-08-20T06:00:00Z",
            ],
            "KGNINJA": [0.0, 20.0],
        }
    )

    result = build_resonance_frame(source)

    assert result["resonance_index"].tolist() == [100.0, 100.0]
    assert np.isfinite(result["resonance_index"]).all()


def test_multiple_effect_series_are_bounded():
    source = pd.DataFrame(
        {
            "timestamp": ["2026-08-20 00:00:00", "2026-08-20T06:00:00Z"],
            "A": [0.0, 300.0],
            "B": [0.0, -300.0],
        }
    )

    result = build_resonance_frame(source)

    assert result["resonance_index"].between(0.0, 100.0).all()
    assert result.iloc[1]["resonance_index"] == 0.0


def test_resonance_rejects_missing_timestamp():
    with pytest.raises(ValueError, match="timestamp"):
        build_resonance_frame(pd.DataFrame({"A": [1.0]}))
