import csv

import pandas as pd
import pytest

import scripts.aieo_visibility_tracker as tracker_module


class FakeResponse:
    def __init__(self, status_code: int, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


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


def test_google_credentials_missing_is_not_recorded_as_zero():
    tracker = tracker_module.VisibilityTracker()
    tracker.google_api_key = ""
    tracker.google_cx = ""

    with pytest.raises(tracker_module.ProviderError, match="設定されていません"):
        tracker.search_google('"KGNINJA"')


def test_google_http_error_is_sanitized_and_not_recorded_as_zero(monkeypatch):
    tracker = tracker_module.VisibilityTracker()
    tracker.google_api_key = "super-secret-api-key"
    tracker.google_cx = "cx-id"
    response = FakeResponse(
        429,
        {
            "error": {
                "status": "RESOURCE_EXHAUSTED",
                "message": "Daily Limit Exceeded",
                "errors": [{"reason": "dailyLimitExceeded"}],
            }
        },
    )
    monkeypatch.setattr(tracker.session, "get", lambda *args, **kwargs: response)

    with pytest.raises(tracker_module.ProviderError) as error:
        tracker.search_google('"KGNINJA"')

    message = str(error.value)
    assert "HTTP 429" in message
    assert "dailyLimitExceeded" in message
    assert "super-secret-api-key" not in message


def test_valid_google_zero_response_remains_a_real_zero(monkeypatch):
    tracker = tracker_module.VisibilityTracker()
    tracker.google_api_key = "test-key"
    tracker.google_cx = "test-cx"
    response = FakeResponse(200, {"searchInformation": {"totalResults": "0"}})
    monkeypatch.setattr(tracker.session, "get", lambda *args, **kwargs: response)

    assert tracker.search_google('"UNKNOWN"') == {"results": 0}


def test_provider_failure_does_not_append_partial_metrics(tmp_path, monkeypatch):
    metrics_path = tmp_path / "aieo_visibility_metrics.csv"
    monkeypatch.setattr(tracker_module, "VISIBILITY_LOG", metrics_path)
    monkeypatch.setattr(
        tracker_module,
        "load_users_config",
        lambda: [{"name": "KGNINJA", "github": "KG-NINJA"}],
    )

    def fail_collection(*args, **kwargs):
        raise tracker_module.ProviderError("quota exhausted")

    monkeypatch.setattr(
        tracker_module.VisibilityTracker, "track_person", fail_collection
    )

    with pytest.raises(tracker_module.ProviderError, match="quota exhausted"):
        tracker_module.main()

    assert not metrics_path.exists()
