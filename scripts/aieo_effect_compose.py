import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MODERN_INPUT_FILE = Path("aieo_visibility_metrics.csv")
LEGACY_INPUT_FILE = Path("visibility_log.csv")
OUTPUT_LOG = "aieo_effect_log.csv"
CHART_FILE = "aieo_effect_chart.png"
MODERN_COLUMNS = {"timestamp", "name", "visibility_score"}
LEGACY_COLUMNS = {"timestamp", "keyword", "totalResults"}


def _normalize_source(df: pd.DataFrame) -> pd.DataFrame:
    """新旧どちらかの可視性スキーマを共通形式へ正規化する。"""
    columns = set(df.columns)
    if MODERN_COLUMNS.issubset(columns):
        normalized = df[["timestamp", "name", "visibility_score"]].rename(
            columns={"name": "keyword", "visibility_score": "value"}
        )
        source_name = "人物別可視性メトリクス"
    elif LEGACY_COLUMNS.issubset(columns):
        normalized = df[["timestamp", "keyword", "totalResults"]].rename(
            columns={"totalResults": "value"}
        )
        source_name = "旧版可視性履歴"
    else:
        expected = sorted(MODERN_COLUMNS), sorted(LEGACY_COLUMNS)
        raise ValueError(
            "対応する可視性スキーマの必須列がありません: "
            f"modern={expected[0]}, legacy={expected[1]}"
        )

    normalized = normalized.copy()
    normalized["timestamp"] = pd.to_datetime(
        normalized["timestamp"],
        format="mixed",
        errors="coerce",
        utc=True,
    ).dt.tz_convert(None)
    normalized["keyword"] = normalized["keyword"].astype("string").str.strip()
    normalized["value"] = pd.to_numeric(normalized["value"], errors="coerce")

    valid_rows = (
        normalized["timestamp"].notna()
        & normalized["keyword"].notna()
        & normalized["keyword"].str.len().gt(0)
        & normalized["value"].notna()
    )
    dropped_rows = int((~valid_rows).sum())
    normalized = normalized.loc[valid_rows]

    if normalized.empty:
        raise ValueError(f"{source_name}に有効な行がありません")
    if dropped_rows:
        print(f"⚠️ {source_name}から無効な{dropped_rows}行を除外しました")
    print(f"✓ {source_name}を使用: {len(normalized)}有効行")
    return normalized


def build_effect_frame(df: pd.DataFrame) -> pd.DataFrame:
    """対象ごとに直前観測との変化率を計算する。"""
    normalized = _normalize_source(df)

    # 対象ごとに時系列を独立させ、観測時刻がずれても直前値を失わない。
    normalized = (
        normalized.sort_values(["keyword", "timestamp"])
        .drop_duplicates(["keyword", "timestamp"], keep="last")
        .reset_index(drop=True)
    )
    normalized["effect"] = (
        normalized.groupby("keyword", sort=False)["value"]
        .pct_change(fill_method=None)
        .mul(100)
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
    )

    # 同一収集回の対象は同じ行へ揃える。過去のずれた観測は空欄を保持する。
    return (
        normalized.pivot_table(
            index="timestamp",
            columns="keyword",
            values="effect",
            aggfunc="last",
        )
        .sort_index()
    )


def select_input_file() -> Path:
    """人物別メトリクスを優先し、未作成なら旧版履歴へ戻す。"""
    for path in (MODERN_INPUT_FILE, LEGACY_INPUT_FILE):
        if path.exists() and path.stat().st_size > 0:
            return path
    raise FileNotFoundError(
        "可視性データがありません。先にVisibility Trackerを実行してください。"
    )


def main() -> None:
    """Effectログとグラフを生成する。"""
    input_file = select_input_file()
    effect_df = build_effect_frame(pd.read_csv(input_file))
    effect_df.to_csv(OUTPUT_LOG, encoding="utf-8")

    plt.figure(figsize=(10, 6))
    for keyword in effect_df.columns:
        series = effect_df[keyword].dropna()
        if not series.empty:
            plt.plot(series.index, series, marker="o", label=keyword)

    plt.title("AIEO Effect Analyzer (Visibility Change Rate)", fontsize=14)
    plt.xlabel("Timestamp")
    plt.ylabel("Effect % Change")
    if len(effect_df.columns):
        plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(CHART_FILE)
    plt.close()
    print(f"✅ {input_file}から{CHART_FILE}を生成しました")


if __name__ == "__main__":
    main()
