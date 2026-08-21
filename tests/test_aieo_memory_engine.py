from pathlib import Path

import pandas as pd

from scripts.aieo_memory_engine import load_visibility_snapshot


def test_memory_prefers_isolated_visibility_metrics(tmp_path: Path):
    modern = tmp_path / "aieo_visibility_metrics.csv"
    legacy = tmp_path / "visibility_log.csv"

    pd.DataFrame(
        {
            "timestamp": [
                "2026-08-20T00:00:00Z",
                "2026-08-20T06:00:00Z",
                "2026-08-20T06:00:00Z",
            ],
            "name": ["KGNINJA", "KGNINJA", "SECOND"],
            "visibility_score": [30.0, 35.0, 20.0],
        }
    ).to_csv(modern, index=False)
    pd.DataFrame(
        {
            "timestamp": ["2026-08-20 00:00:00"],
            "keyword": ["KGNINJA AI"],
            "totalResults": [9999],
        }
    ).to_csv(legacy, index=False)

    snapshot = load_visibility_snapshot(modern, legacy)

    assert snapshot["source"] == str(modern)
    assert snapshot["metric_type"] == "visibility_score"
    assert snapshot["primary_name"] == "KGNINJA"
    assert snapshot["primary_value"] == 35.0
    assert snapshot["values"] == {"KGNINJA": 35.0, "SECOND": 20.0}


def test_memory_falls_back_to_latest_legacy_keyword_values(tmp_path: Path):
    modern = tmp_path / "missing-modern.csv"
    legacy = tmp_path / "visibility_log.csv"

    pd.DataFrame(
        {
            "timestamp": [
                "2026-08-20 00:00:00",
                "2026-08-20T06:00:00Z",
                "2026-08-20T06:00:00Z",
            ],
            "keyword": ["KGNINJA AI", "KGNINJA AI", "AIEO"],
            "totalResults": [100, 150, 2000],
        }
    ).to_csv(legacy, index=False)

    snapshot = load_visibility_snapshot(modern, legacy)

    assert snapshot["source"] == str(legacy)
    assert snapshot["metric_type"] == "result_count"
    assert snapshot["primary_name"] == "KGNINJA AI"
    assert snapshot["primary_value"] == 150.0
