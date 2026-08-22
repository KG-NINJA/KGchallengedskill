import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import scripts.aieo_memory_freshness as freshness
import scripts.aieo_visibility_workflow as visibility_workflow


def test_only_known_google_referrer_block_is_degraded():
    known = (
        "Google Custom SearchがHTTP 403を返しました: PERMISSION_DENIED / forbidden / "
        "Requests from referer <empty> are blocked."
    )
    assert visibility_workflow.is_known_provider_degradation(known)

    assert not visibility_workflow.is_known_provider_degradation(
        "Google Custom SearchがHTTP 429を返しました: dailyLimitExceeded"
    )
    assert not visibility_workflow.is_known_provider_degradation(
        "GitHub APIがHTTP 500を返しました"
    )
    assert not visibility_workflow.is_known_provider_degradation(
        "追跡対象がありません: config/users_to_track.json"
    )


def test_unrelated_tracker_failure_propagates(monkeypatch, tmp_path):
    output = tmp_path / "github-output.txt"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setattr(
        visibility_workflow.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=7,
            stdout="",
            stderr="GitHub APIがHTTP 500を返しました\n",
        ),
    )

    assert visibility_workflow.main() == 7
    assert "provider_degraded=false" in output.read_text(encoding="utf-8")


def test_known_referrer_block_degrades_without_failing(monkeypatch, tmp_path):
    output = tmp_path / "github-output.txt"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setattr(
        visibility_workflow.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=1,
            stdout=(
                "Google Custom SearchがHTTP 403を返しました: PERMISSION_DENIED / forbidden / "
                "Requests from referer <empty> are blocked.\n"
            ),
            stderr="traceback omitted by wrapper\n",
        ),
    )

    assert visibility_workflow.main() == 0
    assert "provider_degraded=true" in output.read_text(encoding="utf-8")


def write_visibility(path: Path, timestamps: list[str]) -> None:
    rows = [
        "timestamp,name,github_followers,github_repos,web_mentions,domain_mentions,visibility_score"
    ]
    rows.extend(f"{ts},KGNINJA,8,179,0,0,50" for ts in timestamps)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_report(path: Path, source_timestamp: str) -> None:
    path.write_text(
        json.dumps(
            {
                "entities": {
                    "KGNINJA": {
                        "source_timestamp": source_timestamp,
                    }
                }
            }
        ),
        encoding="utf-8",
    )


def test_memory_freshness_detects_new_observation(tmp_path):
    visibility = tmp_path / "metrics.csv"
    report = tmp_path / "resonance.json"
    write_visibility(visibility, ["2026-08-21T07:15:54Z", "2026-08-22T07:15:54Z"])
    write_report(report, "2026-08-21T07:15:54Z")

    fresh, source, processed = freshness.is_fresh(visibility, report)
    assert fresh is True
    assert source > processed


def test_memory_freshness_rejects_replayed_observation(tmp_path):
    visibility = tmp_path / "metrics.csv"
    report = tmp_path / "resonance.json"
    write_visibility(visibility, ["2026-08-21T07:15:54Z"])
    write_report(report, "2026-08-21T07:15:54Z")

    fresh, source, processed = freshness.is_fresh(visibility, report)
    assert fresh is False
    assert source == processed


def test_memory_freshness_fails_on_invalid_processed_report(tmp_path):
    visibility = tmp_path / "metrics.csv"
    report = tmp_path / "resonance.json"
    write_visibility(visibility, ["2026-08-21T07:15:54Z"])
    report.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="entities"):
        freshness.is_fresh(visibility, report)
