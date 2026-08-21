#!/usr/bin/env python3
"""分離された人物別可視性メトリクスからAIEO共鳴度を算出する。"""

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt

VISIBILITY_LOG = Path(
    os.getenv("AIEO_VISIBILITY_METRICS_LOG", "aieo_visibility_metrics.csv")
)
RESONANCE_OUTPUT = Path("resonance_snapshot.png")
REPORT_OUTPUT = Path("resonance_report.json")
REQUIRED_COLUMNS = {
    "timestamp",
    "name",
    "github_followers",
    "github_repos",
    "web_mentions",
    "domain_mentions",
    "visibility_score",
}


def utc_now_iso() -> str:
    """現在のUTC時刻をISO 8601形式で返す。"""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_visibility_data() -> list[dict]:
    """専用CSVを検証して全行を読み込む。"""
    if not VISIBILITY_LOG.exists():
        raise FileNotFoundError(f"{VISIBILITY_LOG} が見つかりません")

    with VISIBILITY_LOG.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        missing = sorted(REQUIRED_COLUMNS - set(reader.fieldnames or []))
        if missing:
            raise ValueError(f"可視性メトリクスに必須列がありません: {missing}")
        data = list(reader)

    if not data:
        raise ValueError("可視性メトリクスにデータ行がありません")
    print(f"✓ {len(data)}件の可視性メトリクスを読み込み")
    return data


def calculate_resonance_scores(visibility_data: list[dict]) -> dict:
    """対象ごとに時刻が最も新しい有効行から共鳴度を計算する。"""
    latest_rows: dict[str, tuple[datetime, dict]] = {}

    for row in visibility_data:
        name = str(row.get("name", "")).strip()
        timestamp_text = str(row.get("timestamp", "")).strip()
        if not name or not timestamp_text:
            continue
        try:
            timestamp = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        previous = latest_rows.get(name)
        if previous is None or timestamp > previous[0]:
            latest_rows[name] = (timestamp, row)

    resonance_scores: dict[str, dict] = {}
    for name, (timestamp, row) in latest_rows.items():
        try:
            github_followers = float(row["github_followers"])
            web_mentions = float(row["web_mentions"])
            domain_mentions = float(row["domain_mentions"])
        except (KeyError, TypeError, ValueError):
            continue

        domain_diversity = min(domain_mentions / 100, 40)
        mention_frequency = min(web_mentions / 1000, 40)
        impact = min(github_followers / 10, 20)
        total_resonance = domain_diversity + mention_frequency + impact

        resonance_scores[name] = {
            "resonance": round(total_resonance, 2),
            "domain_diversity": round(domain_diversity, 2),
            "mention_frequency": round(mention_frequency, 2),
            "impact": round(impact, 2),
            "source_timestamp": timestamp.isoformat().replace("+00:00", "Z"),
        }

    if not resonance_scores:
        raise ValueError("可視性メトリクスに有効な対象行がありません")
    return resonance_scores


def generate_resonance_visualization(resonance_scores: dict) -> None:
    """対象別の共鳴度を横棒グラフとして保存する。"""
    names = list(resonance_scores)
    scores = [resonance_scores[name]["resonance"] for name in names]

    plt.figure(figsize=(10, 5))
    plt.barh(names, scores)
    plt.xlabel("Resonance Score")
    plt.title("AIEO Resonance Index")
    plt.xlim(0, 100)
    plt.grid(axis="x", alpha=0.3, linestyle="--")
    plt.tight_layout()
    plt.savefig(RESONANCE_OUTPUT, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"✓ 可視化を保存: {RESONANCE_OUTPUT}")


def save_resonance_report(resonance_scores: dict) -> None:
    """共鳴度のJSONレポートを保存する。"""
    average = sum(item["resonance"] for item in resonance_scores.values()) / len(
        resonance_scores
    )
    report = {
        "timestamp": utc_now_iso(),
        "total_entities": len(resonance_scores),
        "average_resonance": round(average, 2),
        "entities": resonance_scores,
    }
    REPORT_OUTPUT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"✓ レポートを保存: {REPORT_OUTPUT}")


def main() -> None:
    """共鳴度の計算、可視化、レポート保存を実行する。"""
    print("=" * 60)
    print("AIEO Resonance Indexer")
    print(f"Started at: {utc_now_iso()}")
    print("=" * 60)

    scores = calculate_resonance_scores(load_visibility_data())
    generate_resonance_visualization(scores)
    save_resonance_report(scores)

    for name, score in scores.items():
        print(f"  {name}: {score['resonance']:.1f}")


if __name__ == "__main__":
    main()
