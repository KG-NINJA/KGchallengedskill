import csv

import pandas as pd
import pytest

import scripts.aieo_visibility_tracker as tracker_module


def sample_metrics(timestamp: str, score: float) -> dict:
    return {
        "timestamp": timestamp,
        "name": "KGNINJA",
        "github_followers": 4,
        "github_repos": 59,
        "web_mentions": 120,
        "domain_mentions": 8,
        "visibility_score": score,
    }


def test_visibility_metrics_use_an_isolated_stable_schema(tmp_path, monkeypatch):
    metrics_path = tmp_path / "aieo_visibility_metrics.csv"
    monkeypatch.setattr(tracker_module, "VISIBILITY_LOG", metrics_path)

    tracker_module.save_visibility_log(
        [sample_metrics("2026-08-20T00:00:00Z", 33.5)]
    )
    tracker_module.save_visibility_log(
        [sample_metrics("2026-08-20T06:00:00Z", 34.0)]
    )

    with metrics_path.open("r", encoding="utf-8", newline="") as file:
        header = next(csv.reader(file))
    assert header == tracker_module.METRIC_FIELDS

    saved = pd.read_csv(metrics_path)
    assert saved.shape == (2, len(tracker_module.METRIC_FIELDS))
    assert saved["name"].tolist() == ["KGNINJA", "KGNINJA"]
    assert saved["visibility_score"].tolist() == [33.5, 34.0]


def test_visibility_metrics_reject_an_incompatible_existing_header(
    tmp_path, monkeypatch
):
    metrics_path = tmp_path / "aieo_visibility_metrics.csv"
    metrics_path.write_text("timestamp,keyword,totalResults\n", encoding="utf-8")
    monkeypatch.setattr(tracker_module, "VISIBILITY_LOG", metrics_path)

    with pytest.raises(ValueError, match="ヘッダーが不正"):
        tracker_module.save_visibility_log(
            [sample_metrics("2026-08-20T00:00:00Z", 33.5)]
        )


def test_track_person_uses_the_shared_collection_timestamp(monkeypatch):
    tracker = tracker_module.VisibilityTracker()
    monkeypatch.setattr(tracker, "fetch_github_user", lambda _: {})
    monkeypatch.setattr(tracker, "search_google", lambda *args, **kwargs: {"results": 0})

    observed_at = "2026-08-20T00:00:00Z"
    first = tracker.track_person("A", {}, observed_at=observed_at)
    second = tracker.track_person("B", {}, observed_at=observed_at)

    assert first["timestamp"] == observed_at
    assert second["timestamp"] == observed_at
