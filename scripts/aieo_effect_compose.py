import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

INPUT_FILE = "visibility_log.csv"
OUTPUT_LOG = "aieo_effect_log.csv"
CHART_FILE = "aieo_effect_chart.png"
REQUIRED_COLUMNS = {"timestamp", "keyword", "totalResults"}


def build_effect_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize legacy visibility rows and calculate percentage changes."""
    missing_columns = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing_columns:
        raise ValueError(f"visibility log is missing columns: {missing_columns}")

    normalized = df[["timestamp", "keyword", "totalResults"]].copy()
    normalized["timestamp"] = pd.to_datetime(
        normalized["timestamp"],
        format="mixed",
        errors="coerce",
        utc=True,
    ).dt.tz_convert(None)
    normalized["keyword"] = normalized["keyword"].astype("string").str.strip()
    normalized["totalResults"] = pd.to_numeric(
        normalized["totalResults"], errors="coerce"
    )

    valid_rows = (
        normalized["timestamp"].notna()
        & normalized["keyword"].notna()
        & normalized["keyword"].str.len().gt(0)
        & normalized["totalResults"].notna()
    )
    dropped_rows = int((~valid_rows).sum())
    normalized = normalized.loc[valid_rows]

    if normalized.empty:
        raise ValueError("visibility log contains no valid rows")
    if dropped_rows:
        print(f"⚠️ Dropped {dropped_rows} invalid visibility rows")

    # Legacy producers can append the same timestamp/keyword more than once.
    # Keep the latest row rather than failing with DataFrame.pivot().
    pivot_df = (
        normalized.pivot_table(
            index="timestamp",
            columns="keyword",
            values="totalResults",
            aggfunc="last",
        )
        .sort_index()
    )

    previous = pivot_df.shift(1).replace(0, np.nan)
    effect_df = (
        pivot_df.diff()
        .div(previous)
        .mul(100)
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
    )
    return effect_df


def main() -> None:
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(
            f"{INPUT_FILE} が存在しません。Visibilityジョブを先に実行してください。"
        )

    df = pd.read_csv(INPUT_FILE)
    effect_df = build_effect_frame(df)
    effect_df.to_csv(OUTPUT_LOG, encoding="utf-8")

    plt.figure(figsize=(10, 6))
    for keyword in effect_df.columns:
        plt.plot(effect_df.index, effect_df[keyword], marker="o", label=keyword)

    plt.title("AIEO Effect Analyzer (Visibility Change Rate)", fontsize=14)
    plt.xlabel("Timestamp")
    plt.ylabel("Effect % Change")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(CHART_FILE)
    plt.close()
    print(f"✅ Chart saved as {CHART_FILE}")


if __name__ == "__main__":
    main()
