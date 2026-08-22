#!/usr/bin/env python3
"""可視性観測が前回処理済みより新しい場合だけMemory更新を許可する。"""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path

VISIBILITY_PATH = Path("aieo_visibility_metrics.csv")
RESONANCE_PATH = Path("resonance_report.json")
REQUIRED_FIELDS = {
    "timestamp",
    "name",
    "github_followers",
    "github_repos",
    "web_mentions",
    "domain_mentions",
    "visibility_score",
}


def parse_timestamp(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("空のtimestampは処理できません")
    parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def newest_visibility_timestamp(path: Path = VISIBILITY_PATH) -> datetime:
    if not path.exists() or path.stat().st_size == 0:
        raise ValueError(f"{path} が存在しないか空です")

    timestamps = []
    invalid_count = 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_FIELDS - fields)
        if missing:
            raise ValueError(f"可視性データの必須列がありません: {missing}")

        # append-only履歴では壊れた過去行だけを無視し、有効な最新観測を採用する。
        for row in reader:
            try:
                timestamps.append(parse_timestamp(row.get("timestamp", "")))
            except (TypeError, ValueError):
                invalid_count += 1

    if not timestamps:
        raise ValueError("可視性データに有効なtimestampがありません")
    if invalid_count:
        print(
            "::warning title=AIEO visibility history contains invalid timestamps::"
            f"不正な過去timestamp {invalid_count}行を無視しました。"
        )
    return max(timestamps)


def latest_processed_timestamp(path: Path = RESONANCE_PATH) -> datetime | None:
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as handle:
            report = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path} を読み込めません: {exc}") from None

    entities = report.get("entities") if isinstance(report, dict) else None
    if not isinstance(entities, dict) or not entities:
        raise ValueError(f"{path} に有効なentitiesがありません")

    timestamps = []
    for entity, payload in entities.items():
        if not isinstance(payload, dict) or "source_timestamp" not in payload:
            raise ValueError(f"{path} の {entity} にsource_timestampがありません")
        timestamps.append(parse_timestamp(payload["source_timestamp"]))

    return max(timestamps)


def is_fresh(
    visibility_path: Path = VISIBILITY_PATH,
    resonance_path: Path = RESONANCE_PATH,
) -> tuple[bool, datetime, datetime | None]:
    source = newest_visibility_timestamp(visibility_path)
    processed = latest_processed_timestamp(resonance_path)
    return processed is None or source > processed, source, processed


def write_github_output(name: str, value: str) -> None:
    output_path = os.getenv("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as handle:
        handle.write(f"{name}={value}\n")


def iso_z(value: datetime | None) -> str:
    if value is None:
        return "none"
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    fresh, source, processed = is_fresh()
    write_github_output("fresh", "true" if fresh else "false")
    write_github_output("source_timestamp", iso_z(source))
    write_github_output("processed_timestamp", iso_z(processed))

    if fresh:
        print(f"✓ 新しい可視性観測を検出: {iso_z(source)}")
    else:
        # 同じ観測を新しいinteractionとして再記録しない。
        print(
            "::warning title=AIEO memory update skipped::"
            f"可視性観測 {iso_z(source)} は既に処理済みです。"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
